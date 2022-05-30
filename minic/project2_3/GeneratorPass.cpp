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

#define MAX_REGISTERS 9
std::string registers[MAX_REGISTERS] = {
    "%rax",
    "%rcx",
    "%rsi",
    "%r10",
    "%r11",
    "%r12",
    "%r13",
    "%r14",
    "%r15"};

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

// Beginning of anonymous namespace. Keeping it anonymous prevents duplicate
// namespaces from occurring, especially when merging code into the LLVM
// pass directory (which we will not be doing.)
namespace
{

    struct X86Builder
    {
        std::vector<std::string> Instructions;

        void debug(std::string str)
        {
            Instructions.push_back("# " + str);
        }

        void start()
        {
            Instructions.push_back(".globl _start");
        }

        void close()
        {
            label("_start");
            call("main");
            move("%rax", "%rbx");
            move("$1", "%rax");
            Instructions.push_back("int $128");
        }

        void move(std::string from, std::string to)
        {

            std::string trueFrom = from;
            std::string trueTo = to;
            if (from[0] == '-')
            {
                trueFrom = "(%r8)";
                move("%rbp", "%r8");
                calc("sub", "$" + std::to_string(-stoi(from)), "%r8", "%r8");
            }
            if (to[0] == '-')
            {
                trueTo = "%r9";
            }
            if (from != to)
            {
                Instructions.push_back("mov " + trueFrom + ", " + trueTo);
            }
            if (to[0] == '-')
            {
                move("%rbp", "%r8");
                calc("sub", "$" + std::to_string(-stoi(to)), "%r8", "%r8");
                move("%r9", "(%r8)");
            }
        }
        void cmp(std::string a, std::string b)
        {
            Instructions.push_back("cmp " + a + ", " + b);
        }
        void push(std::string reg)
        {
            Instructions.push_back("push " + reg);
        }
        void pop(std::string reg)
        {
            Instructions.push_back("pop " + reg);
        }
        void ret()
        {
            Instructions.push_back("ret\n");
        }
        void jmp(std::string dest)
        {
            Instructions.push_back("jmp " + dest);
        }
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
        void call(Function *F)
        {
            std::string name = F->getName();
            call(name);
        }
        void call(std::string dest)
        {
            Instructions.push_back("call " + dest);
        }
        void label(std::string label)
        {
            Instructions.push_back(label + ":");
        }

        void calc(std::string op, std::string from, std::string to, std::string dest)
        {
            std::string trueFrom = from;
            std::string trueTo = to;
            if (from[0] == '-')
            {
                trueFrom = "%r8";
                move("%rbp", "%r8");
                calc("sub", "$" + std::to_string(-stoi(from)), "%r8", "%r8");
                move("(%r8)", "%r8");
            }
            if (to[0] == '-')
            {
                trueTo = "%r9";
                move("%rbp", "%r9");
                calc("sub", "$" + std::to_string(-stoi(to)), "%r9", "%r9");
                move("(%r9)", "%r9");
            }

            Instructions.push_back(op + " " + trueFrom + ", " + trueTo);

            if (to[0] == '-')
            {
                move("%rbp", "%r8");
                calc("sub", "$" + std::to_string(-stoi(to)), "%r8", "%r8");
                move("%r9", dest);
            }
            else
            {
                move(to, dest);
            }
        }
        void calc(std::string op, std::string to)
        {
            std::string trueTo = to;
            if (to[0] == '-')
            {
                trueTo = "%r8";
                move("%rbp", "%r8");
                calc("sub", "$" + std::to_string(-stoi(to)), "%r8", "%r8");
                move("(%r8)", "%r8");
            }
            Instructions.push_back(op + " " + trueTo);
        }

        std::string _replaceAll(std::string str, const std::string &from, const std::string &to)
        {
            size_t start_pos = 0;
            while ((start_pos = str.find(from, start_pos)) != std::string::npos)
            {
                str.replace(start_pos, from.length(), to);
                start_pos += to.length(); // Handles case where 'to' is a substring of 'from'
            }
            return str;
        }

        std::string assign(int registers_used)
        {
            assert(registers_used <= MAX_REGISTERS);

            std::stringstream stream;
            for (auto I : Instructions)
            {
                stream << I << "\n";
            }
            std::string res = stream.str();

            for (int i = registers_used; i >= 0; i--)
            {
                res = _replaceAll(res, "(" + std::to_string(i) + ")", registers[i]);
            }

            return res;
        }
    };

    struct Generator
    {
        X86Builder Builder;
        std::map<BasicBlock *, int> Blocks;
        int nextBlock = 0;
        std::map<Value *, Use *> NoMoreUses;

        /*

        Stuff For memory managment

        */

        // There needs to be some data structure here that maps values to locations
        std::map<Value *, std::string> DS;
        int registers_used = 0;
        int temporary = 0;
        BasicBlock *CurrentBlock;
        int stack_offset = 0;

        void push()
        {
            stack_offset -= 8;
        }
        void pop()
        {
            stack_offset += 8;
        }

        void
        startNewBlock(BasicBlock *B)
        {
            CurrentBlock = B;
        }

        void startNewFunction()
        {
            temporary = 0;
        }

        int registerStringToInt(std::string reg)
        {
            if (reg[0] == '%')
            {
                return -1;
            }
            return stoi(reg);
        }

        int getRegistersUsed()
        {
            return registers_used + 1;
        }

        std::string getNewLocation()
        {
            int next = temporary;
            for (int i = 0; i < temporary; i++)
            {
                bool found = false;
                for (auto P : DS)
                {
                    if (registerStringToInt(P.second) == i)
                        found = true;
                }
                if (!found)
                {
                    next = i;
                }
            }
            if (next == temporary)
                temporary++;

            if (next >= MAX_REGISTERS)
            {
                // There are no more registers, so we need to allocate space for this value on the stack...
                push();
                return std::to_string(stack_offset - 8);

                errs()
                    << "UNABLE TO SUPPORT MORE THAN " << MAX_REGISTERS << " REGISTERS AT THE CURRENT MOMENT\n";
                exit(EXIT_FAILURE);
            }
            registers_used = std::max(registers_used, next);

            return std::to_string(next);
        }

        std::string getLocationFor(Value *V, bool constant_allow = false)
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
                    Builder.debug("Found... " + P.second);
                    if (P.second[0] == '%')
                    {
                        return P.second;
                    }
                    else if (P.second[0] == '-')
                    {
                        return P.second;
                    }
                    Builder.debug("Before: In function " + P.second);
                    Builder.debug("Before: In function " + P.second);

                    return "(" + P.second + ")";
                }
            }

            std::string loc = getNewLocation();

            DS.insert(std::make_pair(V, loc));

            if (loc[0] == '-')
            {
                // We have a value that is on the stack...
                return loc;
            }
            else
            {
                return "(" + loc + ")";
            }
        }
        void setLocation(Value *V, std::string loc)
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

        /*

        End of Memory Stuff


        */

    public:
        Generator()
        {
        }

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

        void handleBranchInstruction(BranchInst *Branch)
        {
            BasicBlock *jmpTrue = Branch->getSuccessor(0);
            std::string blockId = getBlockId(dyn_cast<BasicBlock>(Branch->getParent()), false);
            if (Branch->isConditional())
            {
                Value *V = Branch->getCondition();

                jmpTrue = Branch->getSuccessor(0);
                BasicBlock *jmpFalse = Branch->getSuccessor(1);

                std::string condCheck = getLocationFor(V, true);

                Builder.cmp("$1", condCheck);
                Builder.move("$" + blockId, "%rbx");

                remove(condCheck);

                Builder.jxx(CmpInst::ICMP_EQ, getBlockId(jmpTrue));
                Builder.jmp(getBlockId(jmpFalse));
            }
            else
            {

                // Indicate which block we are coming from...
                Builder.move("$" + blockId, "%rbx");
                Builder.jmp(getBlockId(jmpTrue));
            }
        }

        void handleCallInstruction(CallInst *Call)
        {
            push();
            Builder.push("%rdi");

            int prior_temp = temporary;

            for (int i = 0; i < prior_temp; i++)
            {
                push();
                Builder.push("(" + std::to_string(i) + ")");
            }

            auto AIter = Call->arg_begin();
            if (AIter != Call->arg_end())
            {
                std::string loc = getLocationFor(*AIter, true);
                Builder.move(loc, "%rdi");
            }

            std::string resLoc = getLocationFor(Call);

            Builder.call(Call->getCalledFunction());
            Builder.move("%rax", resLoc);

            for (int i = prior_temp - 1; i >= 0; i--)
            {
                pop();
                Builder.pop("(" + std::to_string(i) + ")");
            }

            pop();
            Builder.pop("%rdi");
        }

        void handleReturnInstruction(ReturnInst *Ret)
        {
            // Load value into register
            if (Value *Res = Ret->getOperand(0))
            {
                std::string loc = getLocationFor(Res, true);
                Builder.move(loc, "%rax");
            }

            for (int i = STATIC_REGISTERS - 1; i >= 0; i--)
            {
                auto reg = function_static_registers[i];
                pop();
                Builder.pop(reg);
            }

            pop();
            Builder.pop("%rbp");
            Builder.ret();
        }

        void handleCompareInstruction(CmpInst *Cmp)
        {
            Value *Op0 = Cmp->getOperand(0);
            Value *Op1 = Cmp->getOperand(1);

            std::string _loc0 = getLocationFor(Op0, true);
            std::string loc0 = getLocationFor(Op0);
            Builder.debug("oof");
            Builder.move(_loc0, loc0);

            std::string loc1 = getLocationFor(Op1, true);

            std::string trueBlock = addBlockPrefix(std::to_string(nextBlock));
            std::string falseBlock = addBlockPrefix(std::to_string(nextBlock + 1));
            std::string postBlock = addBlockPrefix(std::to_string(nextBlock + 2));

            nextBlock += 3;

            Builder.cmp(loc1, loc0);

            CmpInst::Predicate op = Cmp->getPredicate();

            std::string loc = getLocationFor(Cmp);

            Builder.jxx(op, trueBlock);

            Builder.label(falseBlock);
            Builder.move("$0", loc);
            Builder.jmp(postBlock);

            Builder.label(trueBlock);
            Builder.move("$1", loc);

            Builder.label(postBlock);
        }

        void handlePHINode(PHINode *PHI)
        {

            // We should have the block that we arrived from in %rbx
            int incoming_blocks = PHI->getNumIncomingValues();
            std::string loc = getLocationFor(PHI);
            std::string postPhi = addBlockPrefix(std::to_string(nextBlock + incoming_blocks));

            std::map<int, std::string> blockMappings;
            for (int incoming = 0; incoming < incoming_blocks; incoming++)
            {
                std::string from_block = addBlockPrefix(std::to_string(nextBlock + incoming));
                blockMappings.insert(std::make_pair(incoming, from_block));
            }
            nextBlock += (incoming_blocks + 1);
            for (auto P : blockMappings)
            {
                BasicBlock *B = PHI->getIncomingBlock(P.first);
                Builder.cmp("$" + getBlockId(B, false), "%rbx");
                Builder.jxx(CmpInst::ICMP_EQ, P.second);
            }

            for (auto P : blockMappings)
            {
                Builder.label(P.second);
                auto placement = getLocationFor(PHI->getIncomingValue(P.first), true);

                Builder.debug("oof2");
                Builder.move(placement, loc);
                Builder.jmp(postPhi);
            }

            Builder.label(postPhi);
        }

        void
        handleRemainingInstruction(Instruction *I)
        {
            int op = I->getOpcode();

            Value *Op0 = I->getOperand(0);
            Value *Op1 = I->getOperand(1);

            std::string _loc0 = getLocationFor(Op0, true);
            std::string loc0 = getLocationFor(Op0);

            if (loc0[0] == '%')
            {
                push();
                Builder.push(loc0);
            }

            Builder.move(_loc0, loc0);

            std::string loc1 = getLocationFor(Op1, true);

            Builder.debug("Before Before: " + loc1);

            std::string resLoc = getLocationFor(I);

            Builder.debug("Before: " + resLoc);
            Builder.debug("Before: " + loc1);

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
                push();
                Builder.push("%rax");
                push();
                Builder.push("%rdx");
                Builder.move("$0", "%rdx");
                Builder.move(loc0, "%rax");

                std::string _loc1 = getLocationFor(Op1, true);
                std::string loc1 = getLocationFor(Op1);
                Builder.move(_loc1, loc1);

                Builder.calc("div", loc1);
                pop();
                Builder.pop("%rdx");
                Builder.move("%rax", resLoc);
                pop();
                Builder.pop("%rax");
            }
            else if (op == Instruction::Mul)
            {
                std::string _loc1 = getLocationFor(Op1, true);
                std::string loc1 = getLocationFor(Op1);
                Builder.move(_loc1, loc1);
                Builder.move(loc0, "%rax");
                Builder.calc("mul", loc1);
                Builder.move("%rax", resLoc);
            }

            if (loc0[0] == '%')
            {
                pop();
                Builder.pop(loc0);
            }
        }

        void processBlock(BasicBlock &B)
        {

            startNewBlock(&B);

            Builder.label(getBlockId(&B));

            BasicBlock::iterator Iter = B.begin();
            Instruction *Last;
            while (Iter != B.end())
            {
                Instruction *I = &*Iter;
                Last = I;

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

        void processFunction(Function &F)
        {
            std::string name = F.getName();
            if (name.find("llvm") == 0)
            {
                return;
            }

            Builder.label(name);
            push();
            Builder.push("%rbp");
            Builder.move("%rsp", "%rbp");

            for (auto reg : function_static_registers)
            {
                push();
                Builder.push(reg);
            }

            auto AIter = F.arg_begin();

            if (AIter != F.arg_end())
            {
                setLocation(&*AIter, "%rdi");
            }

            startNewFunction();

            for (auto &B : F)
            {
                processBlock(B);
            }

            while (stack_offset < 0)
            {
                pop();
                Builder.pop("%r8");
            }
        }

        void processModule(Module &M)
        {
            Builder.start();

            for (auto &F : M)
            {
                processFunction(F);
            }
            Builder.close();
        }

        void generate()
        {
            std::cout << Builder.assign(getRegistersUsed());
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
