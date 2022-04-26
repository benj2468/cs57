from enum import Enum
from typing import List, Tuple
from typing_extensions import Self

from Scope import Scope

### COSC57 AST class for Python
### By Ben Kallus
### Fully type checked by mypy; formatted with black.
### If you are cool, you will run your code through mypy and black when you use this library.
#
# 19 Apr 2022  bjk  Creation
# 24 Apr 2022  jpb  Released v1 for class
# 25 Apr 2022  bjc  Updated to handle multiple parameters to functions
# 26 Apr 2022  bjc  Refactored added codegen
#


INDENT_STR = "|   "

# Abstract class from which all node classes in the AST derive.
class ASTNode:
    def print(self, indentation_level: int = 0):
        assert False


# Abstract class from which all statements derive.
# A statement is (informally) anything that could sit on its own in a block.
class ASTStmtNode(ASTNode):
    pass


# Abstract class from which all expressions derive.
# An expression is a term, a function call, or expressions combined with appropriate operators.
class ASTExprNode(ASTStmtNode):
    pass


# Abstract class from which variable and function declarations derive.
class ASTDeclNode(ASTStmtNode):
    pass


# An assignment (eg. "a = 1;")
class ASTAsgnNode(ASTStmtNode):
    def __init__(self, lhs: str, rhs: ASTExprNode) -> None:
        # The left-hand side of the assignment
        self.lhs = lhs
        # The right-hand side of the assignment
        self.rhs = rhs

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}Asgn. {self.lhs} =")
        self.rhs.print(indentation_level + 1)

    def gen(self) -> str:
        rhs = self.rhs.gen()
        return f"""
        llvm::Value *Val = {rhs};
        if (Val) {{
            // Look up the name.
            llvm::Value *Variable = NamedValues["{self.lhs}"];
            if (!Variable)
                LogErrorV("Unknown variable name");

            Builder->CreateStore(Val, Variable);
        }}
        """


# A block (eg. "{ int a; a = 10 + b; exit(1); return will_never_get_here; }")
class ASTBlockNode(ASTStmtNode):
    def __init__(self, stmt_list: List[ASTStmtNode]) -> None:
        # The statements that make up the block
        self.stmt_list = stmt_list

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}Block.")
        for stmt in self.stmt_list:
            stmt.print(indentation_level + 1)

    def gen(self) -> str:
        res = "({"
        for stmt in self.stmt_list:
            res += stmt.gen() + ";"
        res += "})"
        return res


# Enum's __str__ will spit out its class name by default.
# This class fixes that problem.
class MyEnum(Enum):
    def __str__(self):
        return self._name_


# Relational operators
class ASTROpType(MyEnum):
    LT = 0  # <
    GT = 1  # >
    LEQ = 2  # <=
    GEQ = 3  # >=
    EQ = 4  # ==
    NEQ = 5  # !=


# Binary operators
class ASTBOpType(MyEnum):
    ADD = 0  # +
    SUB = 1  # -
    DIV = 2  # /
    MUL = 3  # *


# Unary operators
class ASTUOpType(MyEnum):
    POS = 0  # +
    NEG = 1  # -


# The types in miniC
class ASTDataType(MyEnum):
    VOID_T = 0
    INT_T = 1
    FLOAT_T = 2
    BOOL_T = 3
    STR_T = 4

    def gen(self) -> str:
        if self == ASTDataType.VOID_T:
            return "llvm::Type::getVoidTy(*TheContext)"
        elif self == ASTDataType.INT_T:
            return "llvm::Type::getInt32Ty(*TheContext)"
        elif self == ASTDataType.FLOAT_T:
            return "llvm::Type::getFloatTy(*TheContext)"
        elif self == ASTDataType.BOOL_T:
            return "llvm::Type::getInt1Ty(*TheContext)"

    def from_str(s) -> Self:
        if s == "void":
            return ASTDataType.VOID_T
        elif s == "int":
            return ASTDataType.INT_T
        elif s == "float":
            return ASTDataType.FLOAT_T
        elif s == "bool":
            return ASTDataType.BOOL_T
        elif s == "str":
            return ASTDataType.STR_T


# A function definition (eg. "int the_identity_fn(int n) { return n; }")
class ASTFuncDefNode(ASTNode):
    def __init__(
        self,
        return_type: ASTDataType,
        name: str,
        params: List[Tuple[ASTDataType, str]],
        body: ASTBlockNode,
    ) -> None:
        # The return type of the function
        self.return_type = return_type
        # The name of the function
        self.name = name
        # The parameter type of the function
        self.params = params
        # The function body
        self.body = body

    def print(self, indentation_level: int = 0) -> None:
        print(
            f"{INDENT_STR * indentation_level}FuncDef. {self.return_type} {self.name}({', '.join([f'{str(x[0])} {x[1]}' for x in self.params])})"
        )
        self.body.print(indentation_level + 1)

    def gen(self) -> str:
        types = [ty[0].gen() for ty in self.params]
        return_ty = self.return_type.gen()

        body = self.body.gen()

        args = ", ".join(types) if len(types) > 1 else f"{types[0]},"
        arg_names = (
            ", ".join([f'"{p[1]}"' for p in self.params])
            if len(self.params) > 1
            else f'"{self.params[0][1]}",'
        )

        return f"""
        ({{
            std::vector<llvm::Type*> Args{{{args}}};
            std::vector<std::string> ArgNames{{{arg_names}}};

            llvm::FunctionType *FT = llvm::FunctionType::get({return_ty}, Args, false);

            llvm::Function *TheFunction = llvm::Function::Create(FT, llvm::Function::InternalLinkage, "{self.name}", TheModule.get());

            // Set names for all arguments.
            unsigned int Idx = 0;
            for (auto &Arg : TheFunction->args()) {{
                Arg.setName(ArgNames[Idx]);
                Idx+=1;
            }}

            llvm::BasicBlock *BB = llvm::BasicBlock::Create(*TheContext, "entry", TheFunction);
            Builder->SetInsertPoint(BB);

            // Record the function arguments in the NamedValues map.
            NamedValues.clear();
            for (auto &Arg : TheFunction->args()) {{
                // Create an alloca for this variable.
                llvm::AllocaInst *Alloca = CreateEntryBlockAlloca(TheFunction, Arg.getName().str(), {return_ty});

                // Store the initial value into the alloca.
                Builder->CreateStore(&Arg, Alloca);

                // Add arguments to variable symbol table.
                NamedValues[Arg.getName().str()] = Alloca;
            }}

            // build the function's body
            llvm::Value *BodyValue = {body};
            if (BodyValue) {{
                TheFunction;
            }} else {{
                // Error reading body, remove function.
                TheFunction->eraseFromParent();
                nullptr;
            }};
        }})
        """


# A root node of an AST. You should have one of these per compilation unit.
class ASTRootNode(ASTNode):
    def __init__(
        self,
        file_name: str,
        decls: List[ASTDeclNode],
        asgns: List[ASTAsgnNode],
        funcs: List[ASTFuncDefNode],
    ) -> None:
        self.file_name = file_name
        # List of function and variable declarations.
        # Must be at the top of the file.
        self.decls = decls
        # List of variable assignments for global variables.
        # Must be after declarations and before functions in the file.
        self.asgns = asgns
        # List of function definitions.
        # Must be at the end of the file.
        self.funcs = funcs

    def print(self, indentation_level: int = 0) -> None:
        print(f"{INDENT_STR * indentation_level}Root.")
        if self.asgns != []:
            print(f"{INDENT_STR * indentation_level}Assignments:")
        for asgn in self.asgns:
            asgn.print(indentation_level + 1)
        if self.decls != []:
            print(f"{INDENT_STR * indentation_level}Declarations:")
        for decl in self.decls:
            decl.print(indentation_level + 1)
        if self.funcs != []:
            print(f"{INDENT_STR * indentation_level}Functions:")
        for func in self.funcs:
            func.print(indentation_level + 1)

    def gen(self) -> str:

        main = ""

        for decl in self.decls:
            main += f"{decl.gen()};"
        for asgns in self.asgns:
            main += f"{asgns.gen()};"
        for func in self.funcs:
            main += f"{func.gen()};"

        return f"""
#include "llvm/ADT/APFloat.h"
#include "llvm/ADT/STLExtras.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/DerivedTypes.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Type.h"
#include "llvm/IR/Verifier.h"
#include "llvm/Support/TargetSelect.h"
#include "llvm/Target/TargetMachine.h"
#include "llvm/Transforms/InstCombine/InstCombine.h"
#include "llvm/Transforms/Scalar.h"
#include "llvm/Transforms/Scalar/GVN.h"
#include "llvm/Transforms/Utils.h"
#include <algorithm>
#include <cassert>
#include <cctype>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <memory>
#include <string>
#include <utility>
#include <vector>

        static std::unique_ptr<llvm::LLVMContext> TheContext;
        static std::unique_ptr<llvm::Module> TheModule;
        static std::unique_ptr<llvm::IRBuilder<>> Builder;
        static std::map<std::string, llvm::AllocaInst *> NamedValues;
        static llvm::ExitOnError ExitOnErr;

        static llvm::AllocaInst *CreateEntryBlockAlloca(llvm::Function *TheFunction,
                                          const std::string &VarName, llvm::Type *ty) {{
            llvm::IRBuilder<> TmpB(&TheFunction->getEntryBlock(),
                            TheFunction->getEntryBlock().begin());
            return TmpB.CreateAlloca(ty, 0, VarName.c_str());
        }}

        llvm::Value *LogErrorV(const char *Str) {{
            fprintf(stderr, \"Error: %s\\n\", Str);
            return nullptr;
        }}

        static void InitializeModule() {{
            // Open a new context and module.
            TheContext = std::make_unique<llvm::LLVMContext>();
            TheModule = std::make_unique<llvm::Module>("{self.file_name}", *TheContext);

            // Create a new builder for the module.
            Builder = std::make_unique<llvm::IRBuilder<>>(*TheContext);
        }}

        llvm::Function *getFunction(std::string Name) {{
            // First, see if the function has already been added to the current module.
            if (auto *F = TheModule->getFunction(Name))
                return F;

            // If no existing prototype exists, return null.
            return nullptr;
        }}

        int main() {{
            InitializeModule();

            {main}

            // Print out all of the generated code.
            TheModule->print(llvm::errs(), nullptr);

            return 0;
        }}


        """


if __name__ == "__main__":
    print("This file isn't meant to be run on its own.")
