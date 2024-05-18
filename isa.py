from __future__ import annotations

import json
from enum import Enum

STACK_SIZE = 1024
MEMORY_SIZE = 2048

class ArgType(str, Enum):
    CONST = "const"
    ADD = "add"
    UNDEFINED = "undefined"

    def __str__(self):
        return str(self.value)

class Arg:
    argType: ArgType

    value: int | None

    def __init__(self, argType: ArgType, value: int | None):
        self.argType = argType
        self.value = value

    def __str__(self):
        return f"{self.argType} {self.value}"


class Opcode(str, Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    EQ = "eq"
    GR = "gr"
    LS = "ls"
    SWAP = "swap"
    DROP = "drop"
    DUP = "dup"
    OVER = "over"
    READ = "read"
    EMIT = "emit"

    VARIABLE = "variable"
    LOAD = "load"
    STORE = "store"
    PUSH = "push"
    POP = "pop"
    RPOP = "rpop"
    JMP = "jmp"
    ZJMP = "zjmp"
    CALL = "call"
    RET = "ret"
    NOP = "nop"
    HALT = "halt"

    def __str__(self):
        return str(self.value)


class Term:
    """Описание выражения из исходного текста программы"""
    
    number: int
    "Позиция токена в программе"
    
    operand: int
    "Хранение дополнительного значения"
    
    name: str
    "Название команды"
    
    converted: bool
    "Нужно ли перевести в машинный код"
    
    def __init__(self, number: int, name: str):
        self.number = number
        self.operand = None
        self.name = name
        self.converted = False
    
    def __str__(self):
       return f"{self.number}  {self.name}"

class Instruction:
    """Описание инструкции процессора"""

    opcode: Opcode

    arg: list[Arg] | None

    def __init__(self, opcode: Opcode, arg: list[Arg] | None):
        self.opcode = opcode
        self.arg = arg
        
    def __str__(self):
        return f"{self.opcode} {self.arg}"

def write_code(filename: str, code: list[Instruction], memory):
    """Записать память и код из инструкций в файл."""
    ans = dict({"memory": memory, "code":code})
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(ans, file, indent=4, default=lambda o: o.__dict__)


def read_code(filename: str) -> list[Instruction]:
    """Прочесть машинный код из файла"""
    with open(filename, encoding="utf-8") as file:
        json_objects = json.loads(file.read())
    code: list[Instruction] = []
    memory = json_objects["memory"]
    for instruction_json in json_objects["code"]:

        opcode = Opcode(instruction_json["command"])
        arg = None
        try:
            if instruction_json["arg"] is not None:
                arg = Arg(ArgType.CONST, int(instruction_json["arg"]))
        except KeyError:
            pass
        code.append(Instruction(opcode, arg))
    return code, memory