//
// LLVM Function Assemply Generator Pass
//
// 27 May 2022  bjc   Project 3 COSC75
//
#include "llvm/IR/InstIterator.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/InstrTypes.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"
#include "llvm/Analysis/TargetLibraryInfo.h"
#include <iostream>
#include <sstream>
#include <algorithm>
#include <regex>

using namespace llvm;

// Change the DEBUG_TYPE define to the friendly name of your pass
#define DEBUG_TYPE "generatorpass"

#define REGISTER_SIZE 8

#define STATIC_REGISTERS 5
std::string function_static_registers[STATIC_REGISTERS] = {"%rbx", "%r12", "%r13", "%r14", "%r15"};

std::string addBlockPrefix(std::string blockId)
{
    return "__" + blockId;
}

template <typename K>
bool contains(std::set<K> const &set, K const &key)
{
    return set.find(key) != set.end();
}

#define MAX_REGISTERS 12
// The Registers we will use
std::string registers[MAX_REGISTERS] = {
    "%rax",
    "%rcx",
    "%rdx",
    "%rsi",
    "%r8",
    "%r9",
    "%r10",
    "%r11",
    "%r12",
    "%r13",
    "%r14",
    "%r15"};

// Helpers, these are drawn from Ben's Code
namespace helpers
{
    // Helper method to x86Program::dust_out_slots
    // Returns whether @instruction uses @value
    bool instruction_makes_use_of(llvm::Instruction const &instruction, llvm::Value const *value)
    {
        // for (llvm::User const *user : value->users()) {
        //     if (&instruction == user) {
        //         return true;
        //     }
        // }

        for (llvm::Value const *operand : instruction.operands())
        {
            if (operand == value)
            {
                return true;
            }
        }

        return false;
    }

    bool recursively_check_for_uses(llvm::BasicBlock const *block, llvm::Value const *value, std::set<llvm::BasicBlock const *> &seen)
    {
        if (value->isUsedInBasicBlock(block))
        {
            return true;
        }

        llvm::Instruction const &terminator = *block->getTerminator();
        for (int i = 0; i < terminator.getNumSuccessors(); i++)
        {
            llvm::BasicBlock const *child_block = terminator.getSuccessor(i);
            if (!contains(seen, child_block))
            {
                seen.insert(child_block);
                if (recursively_check_for_uses(child_block, value, seen))
                {
                    return true;
                }
            }
        }

        return false;
    }

    // Helper method to x86Program::dust_out_slots
    // Returns whether @value has any uses reachable from just after @it (i.e. not including @it)
    bool has_reachable_uses(llvm::BasicBlock::const_iterator it, llvm::Value const *value)
    {
        while (!it->isTerminator())
        {
            it++;
            if (instruction_makes_use_of(*it, value))
            {
                return true;
            }
        }

        // Note that `seen` starts out empty, so we may revisit the starting block if there's a loop.
        // This is actually good because if we can revisit the starting block, then there's definitely a reachable use.
        // (i.e. @it's instruction)
        std::set<llvm::BasicBlock const *> seen;

        // The terminator instruction of the block we started in
        llvm::Instruction const &terminator = llvm::cast<llvm::Instruction>(*it);
        for (int i = 0; i < terminator.getNumSuccessors(); i++)
        {
            llvm::BasicBlock const *child_block = terminator.getSuccessor(i);
            if (!contains(seen, child_block))
            {
                seen.insert(child_block);
                if (recursively_check_for_uses(child_block, value, seen))
                {
                    return true;
                }
            }
        }

        return false;
    }
}

namespace
{
    // Structure for building the x86 instructions.
    struct X86Builder
    {
        std::vector<std::string> Instructions;

        // Write a comment
        void debug(std::string str)
        {
            Instructions.push_back("# " + str);
        }

        // Start the module
        void start()
        {
            Instructions.push_back(".globl _start");
        }

        // Close the module
        void close()
        {
            label("_start");
            call("main");
            move("%rax", "%rbx");
            move("$1", "%rax");
            Instructions.push_back("int $128");
        }

        // Create a move instruction: `mov <from>, <to>`
        void move(std::string from, std::string to)
        {
            if (from != to)
            {
                std::string trueFrom = from;
                std::string trueTo = to;

                if (from[0] == '-')
                {
                    push("%r8");
                    trueFrom = "(%r8)";
                    move("%rbp", "%r8");
                    calc("sub", "$" + std::to_string(-stoi(from)), "%r8", "%r8");
                }
                if (to[0] == '-')
                {
                    push("%r9");
                    trueTo = "%r9";
                }

                Instructions.push_back("mov " + trueFrom + ", " + trueTo);

                if (to[0] == '-')
                {
                    move("%rbp", "%r8");
                    calc("sub", "$" + std::to_string(-stoi(to)), "%r8", "%r8");
                    move("%r9", "(%r8)");
                    pop("%r9");
                }
                if (from[0] == '-')
                {
                    pop("%r8");
                }
            }
        }

        // Create a compare instruction: `cmp <a>, <b>`
        void cmp(std::string a, std::string b)
        {
            Instructions.push_back("cmp " + a + ", " + b);
        }
        // Create a push instruction: `push <reg>`
        void push(std::string reg)
        {
            Instructions.push_back("push " + reg);
        }
        // Create a pop instruction: `pop <reg>`
        void pop(std::string reg)
        {
            Instructions.push_back("pop " + reg);
        }
        // Create a return instruction: `ret`
        void ret()
        {
            Instructions.push_back("ret\n");
        }
        // Create a jmp instruction: `jmp <dest>`
        void jmp(std::string dest)
        {
            Instructions.push_back("jmp " + dest);
        }
        // Create a predicated jump instrction `j<pred> dest`
        void jxx(CmpInst::Predicate pred, std::string dest)
        {
            if (pred == CmpInst::ICMP_EQ)
            {
                Instructions.push_back("je " + dest);
            }
            else if (pred == CmpInst::ICMP_SLT)
            {
                Instructions.push_back("jl " + dest);
            }
            else if (pred == CmpInst::ICMP_SLE)
            {
                Instructions.push_back("jl " + dest);
                Instructions.push_back("je " + dest);
            }
            else if (pred == CmpInst::ICMP_SGT)
            {
                Instructions.push_back("jg " + dest);
            }
            else if (pred == CmpInst::ICMP_SGE)
            {
                Instructions.push_back("jg " + dest);
                Instructions.push_back("je " + dest);
            }
            else if (pred == CmpInst::ICMP_NE)
            {
                Instructions.push_back("jne " + dest);
            };
        }
        // Create a call instruction: `call <F.name>`
        void call(Function *F)
        {
            std::string name = F->getName();
            call(name);
        }
        // Create a call instruction: `call <dest>`
        void call(std::string dest)
        {
            Instructions.push_back("call " + dest);
        }
        // Create a label: `<label>:`
        void label(std::string label)
        {
            Instructions.push_back(label + ":");
        }

        // Create a calculation {add, sub} instruction: `op from to` + `mov to dest`
        void calc(std::string op, std::string from, std::string to, std::string dest)
        {
            std::string trueFrom = from;
            std::string trueTo = to;
            std::string trueDest = dest;

            if (from[0] == '-')
            {
                trueFrom = (trueTo == "%r9") ? "%r8" : "%r9";
                push(trueFrom);

                move("%rbp", trueFrom);
                calc("sub", "$" + std::to_string(-stoi(from)), trueFrom, trueFrom);
                move("(" + trueFrom + ")", trueFrom);
            }
            if (to[0] == '-')
            {
                trueTo = (trueFrom == "%r9") ? "%r8" : "%r9";
                push(trueTo);

                move("%rbp", trueTo);
                calc("sub", "$" + std::to_string(-stoi(to)), trueTo, trueTo);
                move("(" + trueTo + ")", trueTo);
            }

            Instructions.push_back(op + " " + trueFrom + ", " + trueTo);

            bool moved = false;
            if (dest[0] == '-')
            {
                push("%r8");
                push("%r9");
                trueDest = "%r8";
                move(trueTo, "%r9");
                move("%rbp", trueDest);
                calc("sub", "$" + std::to_string(-stoi(dest)), trueDest, trueDest);
                move("%r9", "(" + trueDest + ")");
                moved = true;
                pop("%r9");
                pop("%r8");
            }
            if (to[0] == '-')
            {
                if (!moved)
                    move(trueTo, dest);
                pop("%r9");
                moved = true;
            }
            if (from[0] == '-')
            {
                if (!moved)
                    move(trueTo, dest);
                pop("%r8");
                moved = true;
            }
            if (!moved)
            {
                move(trueTo, dest);
            }
        }

        // Create a calculation instruciton {mul, div}: `op <to>` [result stored in %rax]
        void calc(std::string op, std::string to)
        {
            std::string trueTo = to;
            push("%r8");
            if (to[0] == '-')
            {
                trueTo = "%r8";
                move("%rbp", trueTo);
                calc("sub", "$" + std::to_string(-stoi(to)), trueTo, trueTo);
                move("(%r8)", trueTo);
            }
            Instructions.push_back(op + " " + trueTo);
            pop("%r8");
        }

        // Historical name assign was to assign registers to temporary values, not necessary anymore due to smart stack use.
        // Now it just combines all the lines.
        std::string assign()
        {
            std::stringstream stream;
            for (auto I : Instructions)
            {
                stream << I << "\n";
            }
            return stream.str();
        }
    };

    // Structure holds memory data, including where values are stored.
    struct Memory
    {
        // Value -> location mapping
        // Location can be a register, or an offset from the base pointer
        std::map<Value *, std::string> DS;
        // Temporary count, fluid as we assign/unassign registers.
        int temporary = 0;
        // Current block, used for future value use checking (Ben's code)
        BasicBlock *CurrentBlock;
        // Current stack offset
        int stack_offset = 0;

        // Incrase Stack offset
        void push()
        {
            stack_offset -= REGISTER_SIZE;
        }
        // Decrease stack offset
        void pop()
        {
            stack_offset += REGISTER_SIZE;
        }

        // Start a new block
        void
        startNewBlock(BasicBlock *B)
        {
            CurrentBlock = B;
        }

        // Start a new function, i.e. set temproary back to zero
        void startNewFunction()
        {
            temporary = 0;
        }

        // Get a new location, prefer register space, otherwise pick current offset
        std::string getNewLocation(std::string disallowed)
        {
            // Default to temporary, which should be low
            int next = registers[temporary] == disallowed ? temporary + 1 : temporary;
            for (int i = 0; i < temporary; i++)
            {
                // If for some reason we've freed a spot smaller than temporary, lets go with that one!
                bool found = false;
                for (auto P : DS)
                {
                    if ((P.second[0] != '%' && stoi(P.second) == i) || P.second == disallowed)
                    {
                        found = true;
                        break;
                    }
                }
                if (!found)
                {
                    next = i;
                    break;
                }
            }
            if (next == temporary)
                temporary++;

            // If we are trying to use a register that we don't have access to, then we need to default to using the stack.
            if (next >= MAX_REGISTERS)
            {
                // There are no more registers, so we need to allocate space for this value on the stack...
                push();
                return std::to_string(stack_offset - REGISTER_SIZE);
            }

            return std::to_string(next);
        }

        // Get the location for a value
        //
        // @param constant_allow (bool, default = false) : if true, and value is a constant, will return $<val>
        // @param disallowed (string [future should be iterator], default = "") : if set, disallows assignment to given reigster.
        std::string getLocationFor(Value *V, bool constant_allow = false, std::string disallowed = "")
        {
            if (constant_allow)
            {
                if (ConstantInt *Const = dyn_cast<ConstantInt>(V))
                {
                    return "$" + std::to_string(Const->getSExtValue());
                }
            }

            for (auto P : DS)
            {
                if (P.first == V)
                {
                    // If it's a standard register (rdi) or a stack offset, return that string
                    if (P.second[0] == '%' || P.second[0] == '-')
                    {
                        return P.second;
                    }

                    // Otherwise what's stored is a reigster number, so lets get the register name

                    return registers[stoi(P.second)];
                }
            }
            // Get a new location, that is not disallowed
            std::string loc = getNewLocation(disallowed);

            if (loc[0] == '-')
            {
                DS.insert(std::make_pair(V, loc));
                return loc;
            }

            auto reg = registers[stoi(loc)];
            if (reg != disallowed)
            {
                DS.insert(std::make_pair(V, loc));
                return reg;
            }

            errs() << "PICKED AN INVALID REGISTER\n";
            exit(EXIT_FAILURE);
        }

        // Sets the location of a value manually to loc.
        void
        setLocation(Value *V, std::string loc)
        {
            for (auto P : DS)
            {
                if (P.first == V)
                {
                    P.second = loc;
                    return;
                }
            }

            auto P = std::make_pair(V, loc);
            DS.insert(P);
        }

        // Removes a location from the data store
        void remove(std::string loc)
        {
            for (auto P : DS)
            {
                if (P.second == loc)
                {
                    DS.erase(P.first);
                    break;
                }
            }
        }
    };

    // Generator/Memory Structure.
    struct Generator
    {
        X86Builder Builder;
        Memory Mem;
        std::map<BasicBlock *, int> Blocks;
        int nextBlock = 0;
        std::map<Value *, Use *> NoMoreUses;

    public:
        Generator()
        {
        }

        // Helper function that uses the Blocks DS to get the blockID used in labeling basic blocks
        //
        // @param with_prefix (bool, default = true) : if you set this to false, you won't get the __ prefix before a block label.
        std::string getBlockId(BasicBlock *B, bool with_prefix = true)
        {
            auto search = Blocks.find(B);
            if (search == Blocks.end())
            {
                nextBlock++;
                Blocks.insert(std::pair<BasicBlock *, int>(B, nextBlock - 1));

                if (!with_prefix)
                    return std::to_string(nextBlock - 1);
                return addBlockPrefix(std::to_string(nextBlock - 1));
            }
            else
            {
                if (!with_prefix)
                    return std::to_string(search->second);
                return addBlockPrefix(std::to_string(search->second));
            }
        }

        // Handle a LLVM Branch Instruction
        void handleBranchInstruction(BranchInst *Branch)
        {
            BasicBlock *jmpTrue = Branch->getSuccessor(0);
            std::string blockId = getBlockId(dyn_cast<BasicBlock>(Branch->getParent()), false);
            // For conditional branches, we need to check the value of the conditional, which we should have already seen and should have been set to a value.
            if (Branch->isConditional())
            {
                Value *V = Branch->getCondition();

                jmpTrue = Branch->getSuccessor(0);
                BasicBlock *jmpFalse = Branch->getSuccessor(1);

                std::string condCheck = Mem.getLocationFor(V, true);

                Builder.cmp("$1", condCheck);
                // Always indicate which block we are coming from before we exit a block
                Builder.move("$" + blockId, "%rbx");

                Mem.remove(condCheck);

                Builder.jxx(CmpInst::ICMP_EQ, getBlockId(jmpTrue));
                Builder.jmp(getBlockId(jmpFalse));
            }
            // If it is not a conditional, we just branch.
            else
            {
                // Always indicate which block we are coming from before we exit a block
                Builder.move("$" + blockId, "%rbx");
                Builder.jmp(getBlockId(jmpTrue));
            }
        }

        // Handle an LLVM Call Instruction
        void handleCallInstruction(CallInst *Call)
        {
            Mem.push();
            Builder.push("%rdi");

            int prior_temp = Mem.temporary;

            // Push all of our registers that we are still using.
            for (int i = 0; i < prior_temp; i++)
            {
                Mem.push();
                Builder.push(registers[i]);
            }

            // Set our argument if we have one.
            auto AIter = Call->arg_begin();
            if (AIter != Call->arg_end())
            {
                std::string loc = Mem.getLocationFor(*AIter, true);
                Builder.move(loc, "%rdi");
            }

            std::string resLoc = Mem.getLocationFor(Call);

            Builder.call(Call->getCalledFunction());
            // Move our result into the location we know.
            Builder.move("%rax", resLoc);

            // Pop back all of our registers
            for (int i = prior_temp - 1; i >= 0; i--)
            {
                Mem.pop();
                Builder.pop(registers[i]);
            }

            Mem.pop();
            Builder.pop("%rdi");
        }

        // Handle LLVM Return Instruction
        void handleReturnInstruction(ReturnInst *Ret)
        {
            // Load value into register
            if (Value *Res = Ret->getOperand(0))
            {
                std::string loc = Mem.getLocationFor(Res, true);
                Builder.move(loc, "%rax");
            }

            // Pop all of the static registers that should be fixed (these were pushed at the beginning)
            //
            // Make sure we get them in reverse order here
            for (int i = STATIC_REGISTERS - 1; i >= 0; i--)
            {
                auto reg = function_static_registers[i];
                Mem.pop();
                Builder.pop(reg);
            }

            Mem.pop();
            Builder.pop("%rbp");
            Builder.ret();
        }

        void handleCompareInstruction(CmpInst *Cmp)
        {
            Value *Op0 = Cmp->getOperand(0);
            Value *Op1 = Cmp->getOperand(1);

            std::string _loc0 = Mem.getLocationFor(Op0, true);
            std::string loc0 = Mem.getLocationFor(Op0);
            // We move in the literal into an actual location, so that we can compare it
            Builder.move(_loc0, loc0);

            std::string loc1 = Mem.getLocationFor(Op1, true);

            // Setup block labels for each block
            std::string trueBlock = addBlockPrefix(std::to_string(nextBlock));
            std::string falseBlock = addBlockPrefix(std::to_string(nextBlock + 1));
            std::string postBlock = addBlockPrefix(std::to_string(nextBlock + 2));

            nextBlock += 3;

            CmpInst::Predicate op = Cmp->getPredicate();

            // This location will store the value $0 if false, $1 if true
            std::string loc = Mem.getLocationFor(Cmp);

            // Make our comparison
            Builder.cmp(loc1, loc0);

            // Jump based on predicate to the true Block
            Builder.jxx(op, trueBlock);

            // Otherwise we continue into the false block (I guess this doesn't actually need a label...)
            Builder.label(falseBlock);
            Builder.move("$0", loc);
            Builder.jmp(postBlock);

            // True Block
            Builder.label(trueBlock);
            Builder.move("$1", loc);

            // Once done, continue to Post Block
            Builder.label(postBlock);
        }

        // Handle LLVM PHI Node
        void handlePHINode(PHINode *PHI)
        {
            // Count of incoming blocks
            int incoming_blocks = PHI->getNumIncomingValues();

            // This location will hold the value of the PHI decision.
            std::string loc = Mem.getLocationFor(PHI);
            std::string postPhi = addBlockPrefix(std::to_string(nextBlock + incoming_blocks));

            std::map<int, std::string> blockMappings;
            // For each incoming block, give it a label so we can jump to it. This is simply a building a DS
            for (int incoming = 0; incoming < incoming_blocks; incoming++)
            {
                std::string from_block = addBlockPrefix(std::to_string(nextBlock + incoming));
                blockMappings.insert(std::make_pair(incoming, from_block));
            }
            nextBlock += (incoming_blocks + 1);

            // For each block
            // If the value in %rbx, which is the last basic block we exited, is equal to this blocks ID, then jump to that block's label.
            for (auto P : blockMappings)
            {
                BasicBlock *B = PHI->getIncomingBlock(P.first);
                Builder.cmp("$" + getBlockId(B, false), "%rbx");
                Builder.jxx(CmpInst::ICMP_EQ, P.second);
            }

            // Build each PHI option's block
            for (auto P : blockMappings)
            {
                // Label it
                Builder.label(P.second);
                auto placement = Mem.getLocationFor(PHI->getIncomingValue(P.first), true);

                // The placement is the value given to the PHI node if we come from this block
                // So let's set it to the PHI nodes value location
                Builder.move(placement, loc);

                // And finaly jump to the end.
                Builder.jmp(postPhi);
            }

            // Label to end..
            Builder.label(postPhi);
        }

        // Handle LLVM Arithmetic Instructions
        void
        handleRemainingInstruction(Instruction *I)
        {
            int op = I->getOpcode();

            Value *Op0 = I->getOperand(0);
            Value *Op1 = I->getOperand(1);

            std::string _loc0 = Mem.getLocationFor(Op0, true);
            std::string loc0 = Mem.getLocationFor(Op0);

            // If loc0 was in a register, push it's value cause we don't want to lose it.
            if (loc0[0] == '%')
            {
                Mem.push();
                Builder.push(loc0);
            }

            Builder.move(_loc0, loc0);

            std::string loc1 = Mem.getLocationFor(Op1, true);

            std::string resLoc = Mem.getLocationFor(I);

            if (op == Instruction::Add)
            {
                Builder.calc("add", loc1, loc0, resLoc);
            }
            else if (op == Instruction::Sub)
            {
                Builder.calc("sub", loc1, loc0, resLoc);
            }
            else if (op == Instruction::SDiv)
            {
                // Save our old value of %rax
                Mem.push();
                Builder.push("%rax");
                // save our old value of %rdx
                Mem.push();
                Builder.push("%rdx");
                // For division we need 0 to be in rdx
                Builder.move("$0", "%rdx");
                // %rax must be the numerator, so let's set it as such
                Builder.move(loc0, "%rax");

                std::string _loc1 = Mem.getLocationFor(Op1, true);
                std::string loc1 = Mem.getLocationFor(Op1, false, "%rdx");
                // Move in our denominator
                Builder.move(_loc1, loc1);

                // Perform division
                Builder.calc("div", loc1);
                // Return old %rdx, we don't care about the remainder
                Mem.pop();
                Builder.pop("%rdx");
                // Move our result into the proper location
                Builder.move("%rax", resLoc);
                // Return old %rax
                Mem.pop();
                Builder.pop("%rax");
            }
            else if (op == Instruction::Mul)
            {
                std::string _loc1 = Mem.getLocationFor(Op1, true);
                std::string loc1 = Mem.getLocationFor(Op1);
                Builder.move(_loc1, loc1);
                Builder.debug("----------------");
                // Multiply by %rax, so move one value in there
                Builder.move(loc0, "%rax");
                Builder.calc("mul", loc1);
                // move result into proper location
                Builder.move("%rax", resLoc);
                Builder.debug("----------------");
            }

            // Return old value back to proper location
            if (loc0[0] == '%')
            {
                Mem.pop();
                Builder.pop(loc0);
            }
        }

        // Process an LLVM block
        void processBlock(BasicBlock &B)
        {

            // Start new block
            Mem.startNewBlock(&B);

            // Label it
            Builder.label(getBlockId(&B));

            // Iterate over all instructions in block
            BasicBlock::iterator Iter = B.begin();
            while (Iter != B.end())
            {
                Instruction *I = &*Iter;

                // Label each instruction just for easier development
                Builder.label("INSTRUCTION_" + std::to_string(nextBlock));
                nextBlock++;

                if (ReturnInst *Ret = dyn_cast<ReturnInst>(I))
                {
                    handleReturnInstruction(Ret);
                }
                else if (BranchInst *Branch = dyn_cast<BranchInst>(I))
                {
                    handleBranchInstruction(Branch);
                }
                else if (CallInst *Call = dyn_cast<CallInst>(I))
                {
                    handleCallInstruction(Call);
                }
                else if (PHINode *Phi = dyn_cast<PHINode>(I))
                {
                    handlePHINode(Phi);
                }
                else if (CmpInst *Cmp = dyn_cast<CmpInst>(I))
                {
                    handleCompareInstruction(Cmp);
                }
                else
                {
                    handleRemainingInstruction(I);
                }

                ++Iter;
            }
        }

        // Process LLVM Function
        void processFunction(Function &F)
        {
            // Ignore llvm ones
            std::string name = F.getName();
            if (name.find("llvm") == 0)
            {
                return;
            }

            // Label it
            Builder.label(name);

            // Classic Function Setup
            Mem.push();
            Builder.push("%rbp");
            Builder.move("%rsp", "%rbp");

            for (auto reg : function_static_registers)
            {
                Mem.push();
                Builder.push(reg);
            }

            auto AIter = F.arg_begin();

            // Set argument to be in %rdi
            if (AIter != F.arg_end())
            {
                Mem.setLocation(&*AIter, "%rdi");
            }

            // Start it
            Mem.startNewFunction();

            // Process each block
            for (auto &B : F)
            {
                processBlock(B);
            }

            // Close it off properly
            while (Mem.stack_offset < 0)
            {
                Mem.pop();
                Builder.pop("%r8");
            }
        }

        // Process LLVM module
        void processModule(Module &M)
        {
            // Start out module
            Builder.start();

            // Process each function
            for (auto &F : M)
            {
                processFunction(F);
            }

            // Close off module
            Builder.close();
        }

        // Perform the actual generation to stdout
        void generate()
        {
            std::cout << Builder.assign();
        }
    };

    struct GeneratorPass : public ModulePass
    {
        static char ID;
        GeneratorPass() : ModulePass(ID) {}

        void getAnalysisUsage(AnalysisUsage &AU) const override
        {
            AU.setPreservesCFG();
            AU.addRequired<TargetLibraryInfoWrapperPass>();
        }

        bool runOnModule(Module &M) override
        {
            Generator generator;

            generator.processModule(M);

            generator.generate();

            return false;
        }
    };
};

// You can change the friendly and long names in RegisterPass to your own pass
// name.
char GeneratorPass::ID = 0;
static RegisterPass<GeneratorPass> X("generatorpass", "Assembly Generator Pass",
                                     false,  /* looks at CFG, true changed CFG */
                                     false); /* analysis pass, true means analysis needs to run again */

// Automatically enable the pass.
// http://adriansampson.net/blog/clangpass.html
static void registerGeneratorPass(const PassManagerBuilder &,
                                  legacy::PassManagerBase &PM)
{
    PM.add(new GeneratorPass());
};
static RegisterStandardPasses
    RegisterMyPass(PassManagerBuilder::EP_EarlyAsPossible,
                   registerGeneratorPass);
