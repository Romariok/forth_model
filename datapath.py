from __future__ import annotations

import logging

from isa import MEMORY_SIZE, STACK_SIZE
from mc import ALU, MUX


class DataPath:
    stack_size: int = None
    stack: list[int] = None
    return_stack_size: int = None
    return_stack: list[int] = None
    input_value: str = None
    stack_pointer: int = None
    return_stack_pointer: int = None
    immediate_value: int = None
    memory_value: int = None
    _io: dict[int] = None
    _pc: int = None
    _bf: int = None

    memory: list = None
    memory_size: int = None

    alu_operation: ALU = None

    mux_tos: MUX = None
    mux_ret_stack: MUX = None
    mux_rsp: MUX = None
    mux_sp: MUX = None

    def __init__(self, input_buffer: list[str]):
        self.stack_size = STACK_SIZE
        self.return_stack_size = STACK_SIZE
        self.stack = [0] * STACK_SIZE
        self.return_stack = [0] * STACK_SIZE
        self.stack_pointer = -1
        self.return_stack_pointer = -1
        self.memory_size = MEMORY_SIZE
        self.memory = [0] * self.memory_size
        self._bf = 0
        self._io = {}
        self._pc = -1
        self._io[10] = input_buffer
        self._io[11] = []

    def fill_memory(self, memory: dict):
        for key in memory.keys():
            self.memory[int(key)] = memory[key]

    # MUX value

    def signal_mux_tos(self):
        if self.mux_tos == MUX.TOS_RETURN_STACK:
            return self.return_stack[self.return_stack_pointer]
        if self.mux_tos == MUX.TOS_MEMORY:
            return self.memory[self.stack[self.stack_pointer]]
        if self.mux_tos == MUX.TOS_ALU:
            return self.get_alu_operation()
        if self.mux_tos == MUX.TOS_IN:
            return ord(self.input_value)
        if self.mux_tos == MUX.TOS_IMM:
            return self.immediate_value
        raise ValueError("Unknown mux_tos signal: " + self.mux_tos)

    def get_alu_operation(self):  # noqa: C901
        left = self.stack[self.stack_pointer - 1]
        right = self.stack[self.stack_pointer]
        result = 0
        if self.alu_operation == ALU.DIV:
            result = left / right
        elif self.alu_operation == ALU.SUB:
            result = left - right
        elif self.alu_operation == ALU.ADD:
            result = left + right
        elif self.alu_operation == ALU.MUL:
            result = left * right
        elif self.alu_operation == ALU.EQ:
            if left == right:
                result = -1
            else:
                result = 0
        elif self.alu_operation == ALU.LS:
            if left < right:
                result = -1
            else:
                result = 0
        elif self.alu_operation == ALU.GR:
            if left > right:
                result = -1
            else:
                result = 0
        elif self.alu_operation == ALU.MOD:
            result = left % right
        else:
            raise ValueError("Unknown alu_operation signal: " + self.alu_operation)
        self._Z = result == 0

        return result

    def signal_mux_stack_pointer(self):
        if self.mux_sp == MUX.SP_INC:
            return self.stack_pointer + 1
        if self.mux_sp == MUX.SP_DEC:
            return self.stack_pointer - 1
        if self.mux_sp == MUX.SP_DOUBLE_DEC:
            return self.stack_pointer - 2
        raise ValueError("Unknown mux_stack_pointer signal: " + self.mux_sp)

    def signal_mux_return_stack_pointer(self):
        if self.mux_rsp == MUX.RSP_INC:
            return self.return_stack_pointer + 1
        if self.mux_rsp == MUX.RSP_DEC:
            return self.return_stack_pointer - 1
        raise ValueError("Unknown mux_return_stack_pointer signal: " + self.mux_rsp)

    def signal_mux_return_stack(self):
        if self.mux_ret_stack == MUX.RS_PC:
            return self._pc
        if self.mux_ret_stack == MUX.RS_TOS:
            return self.stack[self.stack_pointer]
        raise ValueError("Unknown mux_return_stack signal: " + self.mux_ret_stack)

    # MUX

    def select_signal_alu_operation(self, sel: MUX):
        self.alu_operation = sel

    def select_signal_return_stack(self, sel: MUX):
        self.mux_ret_stack = sel

    def select_signal_return_stack_pointer(self, sel: MUX):
        self.mux_rsp = sel

    def select_signal_tos(self, sel: MUX):
        self.mux_tos = sel

    def select_signal_stack_pointer(self, sel: MUX):
        self.mux_sp = sel

    # Latch
    def signal_latch_return_stack(self):
        self.return_stack[self.return_stack_pointer] = self.signal_mux_return_stack()

    def signal_latch_stack_pointer(self):
        self.stack_pointer = self.signal_mux_stack_pointer()
        assert -2 <= self.stack_pointer < self.stack_size, "Out of stack: " + str(self.stack_pointer)

    def signal_latch_return_stack_pointer(self):
        self.return_stack_pointer = self.signal_mux_return_stack_pointer()
        assert -2 <= self.return_stack_pointer < self.stack_size, "Out of return stack: " + str(
            self.return_stack_pointer
        )

    def signal_latch_top(self):
        self.stack[self.stack_pointer] = self.signal_mux_tos()

    def signal_latch_next(self):
        self.stack[self.stack_pointer - 1] = self.signal_mux_tos()

    #

    def signal_input(self, port: int):
        input_buffer = self._io[port]
        in_value = input_buffer[0]
        self.input_value = in_value
        if ord(in_value) == 0:
            in_value = ""
        self._io[port] = input_buffer[1:]
        logging.debug(f"INPUT: '{in_value}'")

    def signal_output(self, port: int, value: int):
        output_buffer = self._io[port] + [value]
        logging.debug(
            f"OUTPUT: {''.join(map(lambda x: chr(x) if x > 9 and x < 256 else str(x), self._io[port]))} << '{value}'"
        )
        self._io[port] = output_buffer

    def signal_memory_read(self, addr: int):
        self.memory_value = self.memory[addr]

    def signal_memory_write(self, addr: int, value: int):
        self.memory[addr] = value

    def get_zero(self):
        return self.stack[self.stack_pointer] == 0
