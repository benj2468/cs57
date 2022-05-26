//
// LLVM Function Dead Code Elimination Pass
//
// Parts taken from skeleton Copyright (c) 2015 Adrian Sampson at
// https://github.com/sampsyo/llvm-pass-skeleton/blob/master/skeleton/Skeleton.cpp
// License file included in directory.
//
// 01 May 2022  jpb   Creation from foundational works shown.
//
//
// 11 May 2022  bjc   Project 2
//
#include "llvm/ADT/Statistic.h"
#include "llvm/Pass.h"
#include "llvm/IR/InstIterator.h"
#include "llvm/IR/NoFolder.h"
#include "llvm/IR/Type.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/InstrTypes.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"
#include "llvm/Analysis/TargetLibraryInfo.h"
#include <iostream>
#include <fstream>
#include <sstream>

using namespace llvm;

// Change the DEBUG_TYPE define to the friendly name of your pass
#define DEBUG_TYPE "generatorpass"

int placeholder = 0;

#define STATIC_REGISTERS 5
std::string function_static_registers[STATIC_REGISTERS] = {"%rbx", "%r12", "%r13", "%r14", "%r15"};

std::string _hexToMemoryLoc(long hex)
{
    std::stringstream stream;
    stream << "("
           << "0x" << std::hex << hex << ")";
    return stream.str();
}

std::string addBlockPrefix(std::string blockId)
{
    return "__" + blockId;
}

// Beginning of anonymous namespace. Keeping it anonymous prevents duplicate
// namespaces from occurring, especially when merging code into the LLVM
// pass directory (which we will not be doing.)
namespace
{

    struct MemorySlot
    {
        std::string name;
        Value *value;

    public:
        MemorySlot(std::string n, Value *V)
        {
            name = n;
            value = V;
        }

        bool isEmpty()
        {
            return value == nullptr;
        }

        void clear()
        {
            value = nullptr;
        }

        bool isValue(Value *V)
        {
            return value == V;
        }

        void replace(Value *V)
        {
            value = V;
        }

        bool isRegister()
        {
            return name[0] == '%';
        }
    };

    struct Memory
    {
        std::vector<MemorySlot> Slots;
        std::string registers[12];

        Memory()
        {
            registers[0] = "%rax";
            registers[1] = "%rbx";
            registers[2] = "%rcx";
            registers[3] = "%rdx";
            registers[4] = "%r8";
            registers[5] = "%r9";
            registers[6] = "%r10";
            registers[7] = "%r11";
            registers[8] = "%r12";
            registers[9] = "%r13";
            registers[10] = "%r14";
            registers[11] = "%r15";
        }

        // If there is a value in a register, return it
        // Otherwise, return nullptr
        Value *
        getValueAt(std::string loc)
        {
            for (auto S : Slots)
            {
                if (S.name == loc)
                {
                    return S.value;
                }
            }
            return nullptr;
        }

        bool hasValue(std::string loc)
        {
            for (auto S : Slots)
            {
                if (S.name == loc)
                {
                    return true;
                }
            }
            return false;
        }

        std::string getLocOf(Value *V)
        {
            int index = 0;
            for (auto S : Slots)
            {
                if (S.value == V)
                {
                    return S.name;
                }
                index++;
            }

            // If there is some value we have not seen yet, we should set asside some memory for it, use a placeholder

            MemorySlot S("_" + std::to_string(placeholder), V);
            Slots.push_back(S);
            placeholder++;

            return S.name;
        }

        // Gets a free register
        // What do we do if there is no free register?
        std::string getNewLocation()
        {
            // This is the biggest function we need to figure out now I beleive...
            for (auto r : registers)
            {
                if (!hasValue(r))
                {
                    return r;
                }
            }

            // int oldestRegister = 0;
            // for (auto S : Slots)
            // {
            //     if (S.isRegister() && S.name != "%rdi")
            //     {
            //         // If this value is not going to be used again... then we don't need to do this...
            //         std::cout << "Could not "
            //         exit(EXIT_FAILURE);
            //     }
            //     oldestRegister++;
            // }
            placeholder++;
            return "_" + std::to_string(placeholder - 1);
        }

        // Move value from one location to another
        void move(std::string from, std::string to)
        {

            if (from == to)
            {
                return;
            }

            std::cout << "mov"
                      << " " << from << ", " << to
                      << "\n";

            Value *atFrom = getValueAt(from);

            MemorySlot S(to, atFrom);
            Slots.push_back(S);
        }

        // Put V into register reg
        // If V is a constant, don't store it somewhere else
        // If it is not a constant, it should already be stored somewhere...
        std::string put(Value *V, bool free_constant = false)
        {

            // If it is a constant, lets put it into a location....
            if (ConstantInt *CI = dyn_cast<ConstantInt>(V))
            {
                if (free_constant)
                {
                    return "$" + std::to_string(CI->getSExtValue());
                }
                std::string location = getNewLocation();
                std::cout << "mov"
                          << " "
                          << "$" << std::to_string(CI->getSExtValue()) << ", " << location << "\n";
                // Put the value into that location...

                MemorySlot S(location, CI);
                Slots.push_back(S);

                return location;
            }
            std::string res = getLocOf(V);

            return res;
        }

        std::string putNew(Value *V)
        {
            errs() << "Adding a new instruction" << *V << "\n";
            for (auto S : Slots)
            {
                if (S.value == V)
                {

                    errs() << "This instruction already exists...\n";
                    return S.name;
                }
            }
            std::string loc = getNewLocation();
            MemorySlot S(loc, V);
            Slots.push_back(S);

            return loc;
        }

        // Update the value at a location in memory
        void updateLocationValue(std::string loc, Value *V)
        {
            MemorySlot S(loc, V);
            Slots.push_back(S);
        }

        // Copy the value, which should be stored already into another location
        std::string copy(Value *V, bool free_constant = false)
        {
            std::string newLocation = getNewLocation();
            std::string location = put(V, free_constant);

            move(location, newLocation);

            return newLocation;
        }
        std::string copy(std::string location)
        {
            std::string newLocation = getNewLocation();

            move(location, newLocation);

            return newLocation;
        }

        // Clear a register, and store the values in the register somewhere else in memory
        void clear(std::string loc)
        {

            copy(loc);

            int i = 0;
            for (auto slot : Slots)
            {
                if (slot.name == loc)
                {
                    Slots.erase(Slots.begin() + i);

                    std::cout << "mov"
                              << " "
                              << "$0"
                              << ", " << loc
                              << "\n";
                    break;
                }
                i++;
            }
        }

        void erase(std::string loc)
        {
            int i = 0;

            for (auto slot : Slots)
            {
                if (slot.name == loc)
                {
                    Slots.erase(Slots.begin() + i);
                    break;
                }
                i++;
            }
        }
    };

    struct Generator
    {
        Memory Mem;
        std::map<BasicBlock *, int> Blocks;
        int nextBlock = 0;

    public:
        Generator() {}

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

        void handleReturnInstruction(ReturnInst *Ret)
        {
            // Load value into register
            if (Value *Res = Ret->getOperand(0))
            {
                Mem.move(Mem.put(Res, true), "%rax");
            }

            for (int i = STATIC_REGISTERS - 1; i >= 0; i--)
            {
                auto reg = function_static_registers[i];
                std::cout << "pop"
                          << " " << reg << "\n";
            }

            std::cout << "pop %rbp\n";

            std::cout << "ret"
                      << "\n";
        }

        void handleBranchInstruction(BranchInst *Branch)
        {
            BasicBlock *jmpTrue = Branch->getSuccessor(0);
            if (Branch->isConditional())
            {
                Value *V = Branch->getCondition();

                jmpTrue = Branch->getSuccessor(1);
                BasicBlock *jmpFalse = Branch->getSuccessor(0);

                // Indicate which block we are coming from put into %rbx
                Mem.clear("%rbx");
                std::cout << "mov"
                          << " $" << getBlockId(dyn_cast<BasicBlock>(Branch->getParent()), false) << ", "
                          << "%rbx"
                          << "\n";

                std::string condCheck = Mem.put(V, true);

                std::cout << "cmp"
                          << " "
                          << "$1"
                          << ", "
                          << condCheck
                          << "\n";

                Mem.erase(condCheck);

                std::cout
                    << "je"
                    << " " << getBlockId(jmpTrue) << "\n";
                std::cout << "jmp"
                          << " " << getBlockId(jmpFalse) << "\n";
            }
            else
            {

                // Indicate which block we are coming from...
                Mem.clear("%rbx");
                std::cout << "mov"
                          << " $" << getBlockId(dyn_cast<BasicBlock>(Branch->getParent()), false) << ", "
                          << "%rbx"
                          << "\n";

                std::cout << "jmp"
                          << " " << getBlockId(jmpTrue) << "\n";
            }
        }

        void handleCallInstruction(CallInst *Call)
        {
            Mem.clear("%rax");
            Mem.copy("%rdi");

            auto AIter = Call->arg_begin();
            if (AIter != Call->arg_end())
            {
                Mem.move(Mem.put(*AIter, true), "%rdi");
            }

            std::string resLoc = Mem.putNew(Call);

            std::cout << "call"
                      << " ";
            Function *Func = Call->getCalledFunction();
            std::cout << Func->getName().str();
            std::cout << "\n";

            Mem.move("%rax", resLoc);
        }

        void handleCompareInstruction(CmpInst *Cmp)
        {
            Value *Op0 = Cmp->getOperand(0);
            Value *Op1 = Cmp->getOperand(1);

            std::string loc0 = Mem.put(Op0, true);
            std::string loc1 = Mem.put(Op1);

            std::string trueBlock = addBlockPrefix(std::to_string(nextBlock));
            std::string falseBlock = addBlockPrefix(std::to_string(nextBlock + 1));
            std::string postBlock = addBlockPrefix(std::to_string(nextBlock + 2));

            nextBlock += 3;

            std::cout << "cmp"
                      << " " << loc0 << ", " << loc1 << "\n";

            CmpInst::Predicate op = Cmp->getPredicate();

            std::string loc = Mem.putNew(Cmp);

            if (op == CmpInst::ICMP_EQ)
            {
                std::cout << "je"
                          << " " << trueBlock << "\n";
            }
            else if (op == CmpInst::ICMP_NE)
            {
                std::cout << "jne"
                          << " " << trueBlock << "\n";
            }
            else if (op == CmpInst::ICMP_SLT)
            {
                std::cout << "jl"
                          << " " << trueBlock << "\n";
            }
            else if (op == CmpInst::ICMP_SLE)
            {
                std::cout << "jt"
                          << " " << trueBlock << "\n";
                std::cout << "je"
                          << " " << trueBlock << "\n";
            }
            else if (op == CmpInst::ICMP_SGT)
            {
                std::cout << "jg"
                          << " " << trueBlock << "\n";
            }
            else if (op == CmpInst::ICMP_SGE)
            {
                std::cout << "jg"
                          << " " << trueBlock << "\n";
                std::cout << "je"
                          << " " << trueBlock << "\n";
            }

            std::cout << falseBlock << ":"
                      << "\n";
            std::cout << "mov $0"
                      << ", " << loc << "\n";
            std::cout << "jmp"
                      << " " << postBlock << "\n";

            std::cout
                << trueBlock << ":"
                << "\n";
            std::cout << "mov $1"
                      << ", " << loc << "\n";

            std::cout << postBlock << ":\n";
        }

        void handlePHINode(PHINode *PHI)
        {

            // We should have the block that we arrived from in %rbx
            BasicBlock *B0 = PHI->getIncomingBlock(0);
            BasicBlock *B1 = PHI->getIncomingBlock(1);

            std::string fromB0Block = addBlockPrefix(std::to_string(nextBlock));
            std::string fromB1Block = addBlockPrefix(std::to_string(nextBlock + 1));
            std::string postPhi = addBlockPrefix(std::to_string(nextBlock + 2));

            std::cout << "cmp"
                      << " "
                      << "$" << getBlockId(B0, false) << ", "
                      << "%rbx"
                      << "\n";
            Mem.erase("%rbx");

            std::cout
                << "je"
                << " " << fromB0Block << "\n";

            std::string loc = Mem.putNew(PHI);

            if (B1)
            {
                std::cout << fromB1Block << ":"
                          << "\n";
                auto placement = Mem.put(PHI->getIncomingValue(1), true);
                std::cout << "mov"
                          << " " << placement
                          << ", " << loc << "\n";
                std::cout << "jmp"
                          << " " << postPhi << "\n";
            }

            std::cout << fromB0Block << ":"
                      << "\n";

            auto placement = Mem.put(PHI->getIncomingValue(0), true);
            std::cout << "mov"
                      << " " << placement
                      << ", " << loc << "\n";

            std::cout << postPhi << ":\n";

            nextBlock += 3;
        }

        void handleRemainingInstruction(Instruction *I)
        {
            int op = I->getOpcode();

            Value *Op0 = I->getOperand(0);
            Value *Op1 = I->getOperand(1);

            std::string loc0 = Mem.copy(Op0, true);
            std::string loc1 = Mem.put(Op1, true);

            std::string resLoc = Mem.putNew(I);

            if (op == Instruction::Add)
            {
                std::cout << "add"
                          << " " << loc1 << ", " << loc0 << "\n";
                Mem.move(loc0, resLoc);
            }
            else if (op == Instruction::Sub)
            {
                std::cout << "sub"
                          << " " << loc1 << ", " << loc0 << "\n";
                Mem.move(loc0, resLoc);
            }
            else if (op == Instruction::SDiv)
            {
                Mem.clear("%rdx");
                Mem.move(loc0, "%rax");
                std::cout << "div"
                          << " " << loc1 << "\n";
                Mem.move("%rax", resLoc);
            }
            else if (op == Instruction::Mul)
            {
                std::string loc1 = Mem.put(Op1);
                Mem.move(loc0, "%rax");
                std::cout << "mul"
                          << " " << loc1 << "\n";
                Mem.move("%rax", resLoc);
            }
        }

        void processBlock(BasicBlock &B)
        {
            std::cout << getBlockId(&B);
            std::cout << ":"
                      << "\n";

            BasicBlock::iterator Iter = B.begin();
            while (Iter != B.end())
            {
                Instruction *I = &*Iter;

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
            std::cout << "\n\n";
        }

        void blockLiveliness(BasicBlock *B, std::map<Value *, std::vector<Value *>> Live)
        {
            std::vector<Value *> alive;
            for (auto IIter = B->rbegin(); IIter == B->rend(); ++IIter)
            {
                Instruction *I = &*IIter;

                std::vector<Value *> curr(alive);

                // remove ones that die, and add ones that are born (see lectures for how to do this)

                alive = curr;
            }
        }

        void processFunction(Function &F)
        {
            std::string name = F.getName();
            if (name.find("llvm") == 0)
            {
                return;
            }

            std::cout << name << ":"
                      << "\n";

            std::cout << "push %rbp\n";
            std::cout << "mov %rsp, %rbp\n";

            for (auto reg : function_static_registers)
            {
                std::cout << "push"
                          << " " << reg << "\n";
            }

            auto AIter = F.arg_begin();

            if (AIter != F.arg_end())
            {
                Mem.updateLocationValue("%rdi", &*AIter);
            }

            for (auto &B : F)
            {
                processBlock(B);
            }

            std::cout << "\n\n";
        }

        void processModule(Module &M)
        {
            std::cout << ".globl _start\n";
            // std::cout << "mov " << _hexToMemoryLoc(stack_location) << ", "
            //        << "%rsp\n";

            for (auto &F : M)
            {
                processFunction(F);
            }
            std::cout << "_start:\n"
                      << "call main\n"
                      << "mov %rax, %rbx\n"
                      << "mov $1, %rax\n"
                      << "int $128\n";
        }

        void generate()
        {
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
