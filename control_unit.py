from __future__ import annotations

from datapath import DataPath
from isa import Instruction
from mc import ALU, IO, MEMORY, MUX, Halt, Latch, opcode_to_mpc


class ControlUnit:
    microprogram_memory: list = None
    mpc: int = None
    instruction_decoder: int = None

    ports: dict[int] = None

    datapath: DataPath = None

    _tick: int = None
    _ir: Instruction = None

    mux_mpc: MUX = None
    mux_pc: MUX = None
    mux_jmp_type: MUX = None

    def __init__(self, microprogram: list, datapath: DataPath):
        self.datapath = datapath
        self.microprogram_memory = microprogram
        self._tick = 0
        self.mpc = 0
        self.ports = []
        self.instruction_decoder = 0

    def tick(self):
        self._tick += 1

    def current_tick(self):
        return self._tick

    # MUX Value

    def signal_mux_jmp_type(self):
        if self.mux_jmp_type == MUX.JMP_TYPE_ZERO:
            if self.datapath.get_zero():
                return MUX.PC_ADDR
            else:
                return MUX.PC_INC
        elif self.mux_jmp_type == MUX.JMP_TYPE_MPC:
            return self.mux_pc
        else:
            raise ValueError("Unknown mux_jmp_type signal: " + self.mux_jmp_type)

    def signal_mux_mpc(self):
        if self.mux_mpc == MUX.MPC_INC:
            return self.mpc + 1
        elif self.mux_mpc == MUX.MPC_OPCODE:
            return opcode_to_mpc(self._ir.opcode)
        elif self.mux_mpc == MUX.MPC_ZERO:
            return 0
        else:
            raise ValueError("Unknown mux_mpc signal: " + self.mux_mpc)

    def signal_mux_pc(self):
        self.mux_pc = self.signal_mux_jmp_type()
        if self.mux_pc == MUX.PC_INC:
            if self.mux_jmp_type == MUX.JMP_TYPE_ZERO:
                return self.datapath._pc
            else:
                return self.datapath._pc + 1
        elif self.mux_pc == MUX.PC_ADDR:
            return self.microprogram_memory[self.datapath._pc].arg.value
        elif self.mux_pc == MUX.PC_RET:
            return self.datapath.return_stack[self.datapath.return_stack_pointer]
        else:
            raise ValueError("Unknown mux_pc signal: " + self.mux_pc)

    # MUX

    def select_signal_pc(self, sel: MUX):
        self.mux_pc = sel

    def select_signal_mpc(self, sel: MUX):
        self.mux_mpc = sel

    def select_signal_jmp_type(self, sel: MUX):
        self.mux_jmp_type = sel

    # Latch

    def signal_latch_pc(self):
        self.datapath._pc = self.signal_mux_pc()

    def signal_latch_mpc(self):
        self.mpc = self.signal_mux_mpc()

    def signal_latch_ir(self):
        self._ir = self.microprogram_memory[self.datapath._pc]

    def dispatch_micro_instruction(self, microcode: list):
        self.mux_jmp_type = MUX.JMP_TYPE_MPC

        for signal in microcode:
            if signal in [MUX.MPC_INC, MUX.MPC_OPCODE, MUX.MPC_ZERO]:
                self.select_signal_mpc(signal)
            elif signal in [MUX.TOS_ALU, MUX.TOS_RETURN_STACK, MUX.TOS_IN, MUX.TOS_MEMORY, MUX.TOS_IMM]:
                if signal is MUX.TOS_IMM:
                    self.datapath.immediate_value = self.microprogram_memory[self.datapath._pc].arg.value
                self.datapath.select_signal_tos(signal)
            elif signal in [MUX.RS_PC, MUX.RS_TOS]:
                self.datapath.select_signal_return_stack(signal)
            elif signal in [MUX.RSP_DEC, MUX.RSP_INC]:
                self.datapath.select_signal_return_stack_pointer(signal)
            elif signal in [MUX.PC_ADDR, MUX.PC_INC, MUX.PC_RET]:
                self.select_signal_pc(signal)
            elif signal in [MUX.SP_DEC, MUX.SP_INC, MUX.SP_DOUBLE_DEC]:
                self.datapath.select_signal_stack_pointer(signal)
            elif signal in [MUX.JMP_TYPE_MPC, MUX.JMP_TYPE_ZERO]:
                self.select_signal_jmp_type(signal)
            elif signal in [ALU.DIV, ALU.EQ, ALU.GR, ALU.LS, ALU.SUB, ALU.ADD, ALU.MUL]:
                self.datapath.select_signal_alu_operation(signal)
            elif isinstance(signal, Halt):
                raise StopIteration("Halt!")
            else:
                match signal:
                    case Latch.PC:
                        self.signal_latch_pc()
                    case Latch.MPC:
                        self.signal_latch_mpc()
                    case Latch.IR:
                        self.signal_latch_ir()
                    case Latch.TOP:
                        self.datapath.signal_latch_top()
                    case Latch.NEXT:
                        self.datapath.signal_latch_next()
                    case Latch.RSP:
                        self.datapath.signal_latch_return_stack_pointer()
                    case Latch.RS:
                        self.datapath.signal_latch_return_stack()
                    case Latch.SP:
                        self.datapath.signal_latch_stack_pointer()
                    case IO.IN:
                        self.datapath.signal_input(self.datapath.stack[self.datapath.stack_pointer])
                    case IO.OUT:
                        self.datapath.signal_output(
                            self.datapath.return_stack[self.datapath.return_stack_pointer],
                            self.datapath.stack[self.datapath.stack_pointer],
                        )
                    case MEMORY.RD:
                        self.datapath.signal_memory_read(self.datapath.stack[self.datapath.stack_pointer])
                    case MEMORY.WR:
                        self.datapath.signal_memory_write(
                            self.datapath.stack[self.datapath.stack_pointer - 1],
                            self.datapath.stack[self.datapath.stack_pointer],
                        )
                    case _:
                        pass
        self.tick()

    def __repr__(self):
        state = (
            f"[{self.datapath._pc}: {self._ir.opcode if self._ir is not None else 'NO_OPCODE' }] TICK: {self.current_tick()} MPC: {self.mpc} "
            f"IR: {self._ir} TOP: {self.datapath.stack[self.datapath.stack_pointer]} "
            f"NEXT: {self.datapath.stack[self.datapath.stack_pointer-1]} "
            f"RS: {self.datapath.return_stack[self.datapath.return_stack_pointer]} SP: {self.datapath.stack_pointer} "
            f"RSP: {self.datapath.return_stack_pointer}"
        )

        return state
