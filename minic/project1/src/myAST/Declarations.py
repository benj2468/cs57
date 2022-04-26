from Scope import Scope
from myAST.AST import ASTDeclNode, ASTDataType, INDENT_STR
from typing import List


# A variable declaration. (eg. "int a;")
class ASTVarDeclNode(ASTDeclNode):
    def __init__(self, is_extern: bool, data_type: ASTDataType, name: str) -> None:
        # Whether the variable is extern
        self.is_extern = is_extern
        # The type of the variable
        self.data_type = data_type
        # The name of the variable
        self.name = name

    def print(self, indentation_level: int = 0) -> None:
        print(
            f"{INDENT_STR * indentation_level}VarDecl. {'extern ' * self.is_extern}{self.data_type} {self.name}"
        )

    def gen(self):
        ty = self.data_type.gen()
        return f"""
        ({{
            // Create an alloca for this variable.
            llvm::AllocaInst *Alloca = Builder->CreateAlloca({ty}, 0, "{self.name}");

            // Add arguments to variable symbol table.
            NamedValues["{self.name}"] = Alloca;
        }})
        """


# A function declaration (eg. "int main(void);" or "extern int square(int);")
class ASTFuncDeclNode(ASTDeclNode):
    def __init__(
        self,
        is_extern: bool,
        return_type: ASTDataType,
        name: str,
        params: List[ASTDataType],
    ) -> None:
        # Whether the function is extern
        self.is_extern = is_extern
        # The return type of the function
        self.return_type = return_type
        # The name of the function
        self.name = name
        # The type of the parameter to the function
        self.params = params
        # Note that parameter names don't matter in C function declarations because all arguments are positional.
        # Thus, we don't store that info in the AST.

    def print(self, indentation_level: int = 0) -> None:
        print(
            f"{INDENT_STR * indentation_level}FuncDecl. {'extern' * self.is_extern} {self.return_type} {self.name}({', '.join(map(str, self.params))})"
        )

    def gen(self):
        types = [ty.gen() for ty in self.params]
        return_ty = self.return_type.gen()
        linkage = (
            "Function::ExternalLinkage"
            if self.is_extern
            else "Function::InternalLinkage"
        )
        return f"""
        ({{
            std::vector<Type*> Args{{{', '.join(types) if len(types) > 1 else f"{types[0]},"}}};

            FunctionType *FT = FunctionType::get({return_ty}, Args, false);

            Function *F = Function::Create(FT, {linkage}, "{self.name}", TheModule.get());

            F;
        }})
        """
