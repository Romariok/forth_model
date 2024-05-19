from enum import Enum

from exceptions import UnknownOpcodeError
from isa import Opcode


class Latch(Enum):
    PC = 0
    TOP = 1
    NEXT = 2
    MPC = 3
    RSP = 4
    RS = 5
    IR = 6
    SP = 7


class Halt:
    pass


class IO:
    IN = 0
    OUT = 1


class ALU(Enum):
    ADD = 0
    DIV = 1
    SUB = 2
    MUL = 3
    MOD = 4
    LS = 5
    GR = 6
    EQ = 7


class MEMORY(Enum):
    WR = 0
    RD = 1


class MUX(Enum):
    TOS_ALU = 0
    TOS_RETURN_STACK = 1
    TOS_IN = 2
    TOS_MEMORY = 3
    TOS_IMM = 4

    RS_PC = 10
    RS_TOS = 11

    RSP_INC = 20
    RSP_DEC = 21

    PC_INC = 30
    PC_ADDR = 31
    PC_RET = 32

    MPC_INC = 40
    MPC_OPCODE = 41
    MPC_ZERO = 42

    SP_INC = 50
    SP_DEC = 51
    SP_DOUBLE_DEC = 52

    JMP_TYPE_ZERO = 60
    JMP_TYPE_MPC = 61


mc_memory = [
    # 0 instruction Fetch
    [MUX.MPC_INC, Latch.MPC, MUX.PC_INC, Latch.PC],
    [MUX.MPC_INC, Latch.MPC, Latch.IR],
    [MUX.MPC_OPCODE, Latch.MPC],
    # 3 NOP
    [MUX.MPC_ZERO, Latch.MPC],
    # 4 HALT
    [Halt()],
    # 5 JUMP
    [MUX.MPC_ZERO, Latch.MPC, MUX.PC_ADDR, Latch.PC],
    # 6 ZJUMP
    [MUX.MPC_ZERO, Latch.MPC, MUX.JMP_TYPE_ZERO, Latch.PC, MUX.SP_DEC, Latch.SP],
    # 7 CALL
    [MUX.MPC_INC, Latch.MPC, MUX.RSP_INC, Latch.RSP],
    [MUX.MPC_ZERO, Latch.MPC, MUX.RS_PC, Latch.RS, MUX.PC_ADDR, Latch.PC],
    # 9 RET
    [MUX.MPC_ZERO, Latch.MPC, MUX.PC_RET, Latch.PC, MUX.RSP_DEC, Latch.RSP],
    # 10 DROP
    [MUX.MPC_ZERO, Latch.MPC, MUX.SP_DEC, Latch.SP],
    # 11 ADD
    [MUX.MPC_ZERO, Latch.MPC, ALU.ADD, MUX.TOS_ALU, Latch.NEXT, MUX.SP_DEC, Latch.SP],
    # 12 SUB
    [MUX.MPC_ZERO, Latch.MPC, ALU.SUB, MUX.TOS_ALU, Latch.NEXT, MUX.SP_DEC, Latch.SP],
    # 13 DIV
    [MUX.MPC_ZERO, Latch.MPC, ALU.DIV, MUX.TOS_ALU, Latch.NEXT, MUX.SP_DEC, Latch.SP],
    # 14 MUL
    [MUX.MPC_ZERO, Latch.MPC, ALU.MUL, MUX.TOS_ALU, Latch.NEXT, MUX.SP_DEC, Latch.SP],
    # 15 EQ
    [MUX.MPC_ZERO, Latch.MPC, ALU.EQ, MUX.TOS_ALU, Latch.NEXT, MUX.SP_DEC, Latch.SP],
    # 16 LS
    [MUX.MPC_ZERO, Latch.MPC, ALU.LS, MUX.TOS_ALU, Latch.NEXT, MUX.SP_DEC, Latch.SP],
    # 17 GR
    [MUX.MPC_ZERO, Latch.MPC, ALU.GR, MUX.TOS_ALU, Latch.NEXT, MUX.SP_DEC, Latch.SP],
    # 18 DUP
    [
        MUX.MPC_INC,
        Latch.MPC,
        MUX.RS_TOS,
        MUX.RSP_INC,
        Latch.RSP,
        Latch.RS,
        MUX.SP_INC,
        Latch.SP,
    ],
    [MUX.MPC_ZERO, Latch.MPC, MUX.TOS_RETURN_STACK, Latch.TOP, MUX.RSP_DEC, Latch.RSP],
    # 20 POP
    [
        MUX.MPC_ZERO,
        Latch.MPC,
        MUX.RS_TOS,
        MUX.RSP_INC,
        Latch.RSP,
        Latch.RS,
        MUX.SP_DEC,
        Latch.SP,
    ],
    # 21 RPOP
    [
        MUX.MPC_ZERO,
        Latch.MPC,
        MUX.SP_INC,
        Latch.SP,
        MUX.TOS_RETURN_STACK,
        Latch.TOP,
        MUX.RSP_DEC,
        Latch.RSP,
    ],
    # 22 PUSH
    [MUX.MPC_INC, Latch.MPC, MUX.SP_INC, Latch.SP],
    [MUX.MPC_ZERO, Latch.MPC, MUX.TOS_IMM, Latch.TOP],
    # 24 READ
    [MUX.MPC_ZERO, Latch.MPC, IO.IN, MUX.TOS_IN, Latch.TOP],
    # 25 EMIT
    [
        MUX.MPC_INC,
        Latch.MPC,
        MUX.RSP_INC,
        Latch.RSP,
        MUX.RS_TOS,
        Latch.RS,
        MUX.SP_DEC,
        Latch.SP,
    ],
    [MUX.MPC_ZERO, Latch.MPC, IO.OUT, MUX.SP_DEC, Latch.SP, MUX.RSP_DEC, Latch.RSP],
    # 27 OVER
    [
        MUX.MPC_INC,
        Latch.MPC,
        MUX.SP_DEC,
        Latch.SP,
        MUX.RS_TOS,
        MUX.RSP_INC,
        Latch.RSP,
        Latch.RS,
    ],
    [
        MUX.MPC_INC,
        Latch.MPC,
        MUX.SP_INC,
        Latch.SP,
    ],
    [MUX.MPC_ZERO, Latch.MPC, MUX.SP_INC, Latch.SP, MUX.TOS_RETURN_STACK, Latch.TOP, MUX.RSP_DEC, Latch.RSP],
    # 30 LOAD
    [MUX.MPC_ZERO, Latch.MPC, MEMORY.RD, MUX.TOS_MEMORY, Latch.TOP],
    # 31 STORE
    [MUX.MPC_ZERO, Latch.MPC, MEMORY.WR, MUX.SP_DOUBLE_DEC, Latch.SP],
    # 32 SWAP
    [
        MUX.MPC_INC,
        Latch.MPC,
        MUX.RSP_INC,
        Latch.RSP,
        MUX.RS_TOS,
        Latch.RS,
        MUX.SP_DEC,
        Latch.SP,
    ],
    [
        MUX.MPC_INC,
        Latch.MPC,
        MUX.RS_TOS,
        MUX.RSP_INC,
        Latch.RSP,
        Latch.RS,
        MUX.SP_INC,
        Latch.SP,
    ],
    [MUX.MPC_INC, Latch.MPC, MUX.TOS_RETURN_STACK, Latch.TOP, MUX.RSP_DEC, Latch.RSP],
    [MUX.MPC_ZERO, Latch.MPC, MUX.TOS_RETURN_STACK, Latch.NEXT, MUX.RSP_DEC, Latch.RSP],
    # 36 MOD
    [MUX.MPC_ZERO, Latch.MPC, ALU.MOD, MUX.TOS_ALU, Latch.NEXT, MUX.SP_DEC, Latch.SP],
]


def opcode_to_mpc(opcode: Opcode) -> int:
    match opcode:
        case Opcode.NOP:
            return 3
        case Opcode.HALT:
            return 4
        case Opcode.JMP:
            return 5
        case Opcode.ZJMP:
            return 6
        case Opcode.CALL:
            return 7
        case Opcode.RET:
            return 9
        case Opcode.DROP:
            return 10
        case Opcode.ADD:
            return 11
        case Opcode.SUB:
            return 12
        case Opcode.DIV:
            return 13
        case Opcode.MUL:
            return 14
        case Opcode.EQ:
            return 15
        case Opcode.LS:
            return 16
        case Opcode.GR:
            return 17
        case Opcode.DUP:
            return 18
        case Opcode.POP:
            return 20
        case Opcode.RPOP:
            return 21
        case Opcode.PUSH:
            return 22
        case Opcode.READ:
            return 24
        case Opcode.EMIT:
            return 25
        case Opcode.OVER:
            return 27
        case Opcode.LOAD:
            return 30
        case Opcode.STORE:
            return 31
        case Opcode.SWAP:
            return 32
        case Opcode.MOD:
            return 36
        case _:
            raise UnknownOpcodeError(opcode)
