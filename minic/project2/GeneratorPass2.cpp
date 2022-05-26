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
//#include "llvm/Pass.h"
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

using namespace llvm;

// Change the DEBUG_TYPE define to the friendly name of your pass
#define DEBUG_TYPE "generatorpass2"

#define STATIC_REGISTERS 5
std::string function_static_registers[STATIC_REGISTERS] = {"%rbx", "%r12", "%r13", "%r14", "%r15"};

std::string addBlockPrefix(std::string blockId)
{
    return "__" + blockId;
}

// Beginning of anonymous namespace. Keeping it anonymous prevents duplicate
// namespaces from occurring, especially when merging code into the LLVM
// pass directory (which we will not be doing.)
namespace
{

    struct X86Builder
    {
        std::vector<std::string> Instructions;

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
            if (from != to)
            {
                Instructions.push_back("mov " + from + ", " + to);
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
                Instructions.push_back("jeq " + dest);
            }
            else if (pred == CmpInst::ICMP_SGT)
            {
                Instructions.push_back("jg " + dest);
            }
            else if (pred == CmpInst::ICMP_SGE)
            {
                Instructions.push_back("jg " + dest);
                Instructions.push_back("jeq " + dest);
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

        void calc(std::string op, std::string locA, std::string locB)
        {
            Instructions.push_back(op + " " + locA + ", " + locB);
        }
        void calc(std::string op, std::string locA)
        {
            Instructions.push_back(op + " " + locA);
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
            std::string registers[8];
            registers[0] = "%r8";
            registers[1] = "%r9";
            registers[2] = "%r10";
            registers[3] = "%r11";
            registers[4] = "%r12";
            registers[5] = "%r13";
            registers[6] = "%r14";
            registers[7] = "%r15";
            // This will loop back and assign registers... for now lets just send it all

            std::stringstream stream;
            for (auto I : Instructions)
            {
                stream << I << "\n";
            }

            std::string res = stream.str();

            if (registers_used < 8)
            {
                for (int i = 0; i < 8; i++)
                {
                    res = _replaceAll(res, "%_" + std::to_string(i), registers[i]);
                }
            }

            return res;
        }
    };

    struct Memory
    {
        // There needs to be some data structure here that maps values to locations
        std::map<Value *, std::string> DS;
        int temporary = 0;

        std::string getNewLocation()
        {
            temporary++;
            return std::to_string(temporary - 1);
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
                    if (P.second[0] == '%')
                    {
                        return P.second;
                    }
                    return "%_" + P.second;
                }
            }
            std::string loc = getNewLocation();

            auto P = std::make_pair(V, loc);
            DS.insert(P);

            return "%_" + P.second;
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
    };

    struct Generator
    {
        X86Builder Builder;
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

        void handleBranchInstruction(BranchInst *Branch)
        {
            BasicBlock *jmpTrue = Branch->getSuccessor(0);
            if (Branch->isConditional())
            {
                Value *V = Branch->getCondition();

                jmpTrue = Branch->getSuccessor(1);
                BasicBlock *jmpFalse = Branch->getSuccessor(0);

                // Indicate which block we are coming from put into %rbx
                Builder.push("%rbx");

                Builder.move("$" + getBlockId(dyn_cast<BasicBlock>(Branch->getParent()), false), "%rbx");

                std::string condCheck = Mem.getLocationFor(V, true);

                Builder.cmp("$1", condCheck);

                Mem.remove(condCheck);

                Builder.jxx(CmpInst::ICMP_EQ, getBlockId(jmpTrue));
                Builder.jmp(getBlockId(jmpFalse));
            }
            else
            {

                // Indicate which block we are coming from...
                Builder.push("%rbx");
                Builder.move("$" + getBlockId(dyn_cast<BasicBlock>(Branch->getParent()), false), "%rbx");
                Builder.jmp(getBlockId(jmpTrue));
            }
        }

        void handleCallInstruction(CallInst *Call)
        {
            Builder.push("%rdi");

            auto AIter = Call->arg_begin();
            if (AIter != Call->arg_end())
            {
                std::string loc = Mem.getLocationFor(*AIter, true);
                Builder.move(loc, "%rdi");
            }

            std::string resLoc = Mem.getLocationFor(Call);

            Builder.call(Call->getCalledFunction());
            Builder.move("%rax", resLoc);

            Builder.pop("%rdi");
        }

        void handleReturnInstruction(ReturnInst *Ret)
        {
            // Load value into register
            if (Value *Res = Ret->getOperand(0))
            {
                std::string loc = Mem.getLocationFor(Res);
                Builder.move(loc, "%rax");
            }

            for (int i = STATIC_REGISTERS - 1; i >= 0; i--)
            {
                auto reg = function_static_registers[i];
                Builder.pop(reg);
            }

            Builder.pop("%rbp");
            Builder.ret();
        }

        void handleCompareInstruction(CmpInst *Cmp)
        {
            Value *Op0 = Cmp->getOperand(0);
            Value *Op1 = Cmp->getOperand(1);

            std::string loc0 = Mem.getLocationFor(Op0, true);
            std::string loc1 = Mem.getLocationFor(Op1);

            std::string trueBlock = addBlockPrefix(std::to_string(nextBlock));
            std::string falseBlock = addBlockPrefix(std::to_string(nextBlock + 1));
            std::string postBlock = addBlockPrefix(std::to_string(nextBlock + 2));

            nextBlock += 3;

            Builder.cmp(loc0, loc1);

            CmpInst::Predicate op = Cmp->getPredicate();

            std::string loc = Mem.getLocationFor(Cmp);

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
            BasicBlock *B0 = PHI->getIncomingBlock(0);
            BasicBlock *B1 = PHI->getIncomingBlock(1);

            std::string fromB0Block = addBlockPrefix(std::to_string(nextBlock));
            std::string fromB1Block = addBlockPrefix(std::to_string(nextBlock + 1));
            std::string postPhi = addBlockPrefix(std::to_string(nextBlock + 2));

            Builder.cmp("$" + getBlockId(B0, false), "%rbx");

            Builder.pop("%rbx");

            Builder.jxx(CmpInst::ICMP_EQ, fromB0Block);

            std::string loc = Mem.getLocationFor(PHI);

            if (B1)
            {
                Builder.label(fromB1Block);

                auto placement = Mem.getLocationFor(PHI->getIncomingValue(1), true);

                Builder.move(placement, loc);
                Builder.jmp(postPhi);
            }

            auto placement = Mem.getLocationFor(PHI->getIncomingValue(0), true);
            Builder.label(fromB0Block);

            Builder.move(placement, loc);

            Builder.label(postPhi);

            nextBlock += 3;
        }

        void handleRemainingInstruction(Instruction *I)
        {
            int op = I->getOpcode();

            Value *Op0 = I->getOperand(0);
            Value *Op1 = I->getOperand(1);

            std::string _loc0 = Mem.getLocationFor(Op0, true);
            std::string loc0 = Mem.getLocationFor(Op0);

            Builder.push(loc0);

            Builder.move(_loc0, loc0);

            std::string loc1 = Mem.getLocationFor(Op1, true);

            std::string resLoc = Mem.getLocationFor(I);

            if (op == Instruction::Add)
            {
                Builder.calc("add", loc1, loc0);
                Builder.move(loc0, resLoc);
            }
            else if (op == Instruction::Sub)
            {
                Builder.calc("sub", loc1, loc0);
                Builder.move(loc0, resLoc);
            }
            else if (op == Instruction::SDiv)
            {
                Builder.push("%rdx");
                Builder.move("$0", "%rdx");
                Builder.move(loc0, "%rax");
                Builder.calc("div", loc1);
                Builder.pop("%rdx");
                Builder.move("%rax", resLoc);
            }
            else if (op == Instruction::Mul)
            {
                std::string _loc1 = Mem.getLocationFor(Op1, true);
                std::string loc1 = Mem.getLocationFor(Op1);
                Builder.move(_loc1, loc1);
                Builder.move(loc0, "%rax");
                Builder.calc("mul", loc1);
                Builder.move("%rax", resLoc);
            }

            Builder.pop(loc0);
        }

        void processBlock(BasicBlock &B)
        {
            Builder.label(getBlockId(&B));

            BasicBlock::iterator Iter = B.begin();
            if (!isa<PHINode>(&*Iter))
            {
                Builder.pop("%rbx");
            }
            Instruction *Last;
            while (Iter != B.end())
            {
                Instruction *I = &*Iter;
                Last = I;

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
            if (!isa<BranchInst>(Last) && !isa<ReturnInst>(Last))
            {
                Builder.push("%rbx");
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
            Builder.push("%rbp");
            Builder.move("%rsp", "%rbp");
            Builder.push("%rbx");

            for (auto reg : function_static_registers)
            {
                Builder.push(reg);
            }

            auto AIter = F.arg_begin();

            if (AIter != F.arg_end())
            {
                Mem.setLocation(&*AIter, "%rdi");
            }

            for (auto &B : F)
            {
                processBlock(B);
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
            std::cout << Builder.assign(Mem.temporary);
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
static RegisterPass<GeneratorPass> X("generatorpass2", "Assembly Generator Pass",
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
