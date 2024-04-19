from enum import Enum, unique

@unique
class Position(Enum):
    INSTRUCTION = 1  
    FUNCTION = 2
    LABEL = 3  
    VARIABLE = 4 


@unique
class RegisterType(Enum):
    IP = "IP"  
    BR = "BR"  
    AC = "ACC"  
    PS = "PS"  
    SP = "SP"  
    AR = "AR"  
    IR = "IR"


@unique
class InstructionType(Enum):

    ADD = "+"
    SUB = "-"
    CMP = "if"
    DIV = "/"
    MUL = "*"
    LD = '@'
    ST = '!'
    PUSH = "PUSH"
    POP = "POP"
    DO = "DO"
    LOOP = "LOOP"
    LEAVE = "LEAVE"
    HLT = ";"
    OUTPUT = "."
    IF = "IF"
    MULTI = "@+!"


MATH_INSTRUCTION = (
    InstructionType.ADD, InstructionType.SUB, InstructionType.CMP, InstructionType.DIV,
    InstructionType.MUL)


DATA_INSTRUCTION = (InstructionType.LD, InstructionType.ST, InstructionType.OUTPUT)


STACK_INSTRUCTION = (InstructionType.POP, InstructionType.PUSH)


JUMP_INSTRUCTION = (
    InstructionType.DO, InstructionType.LOOP, InstructionType.LEAVE)


NO_ARGUMENT = (
    InstructionType.PUSH, InstructionType.POP, InstructionType.HLT,InstructionType.DO, InstructionType.LOOP, InstructionType.LEAVE)

