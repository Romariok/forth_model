from isa import Opcode


class UnknownOpcodeError(Exception):
   def __init__(self, opcode: Opcode):
      super().__init__("Unknown opcode: " + opcode)

class TokenTranslationError(Exception):
   def __init__(self, pos: int):
      super().__init__(f"Problems with {pos} term")

class BadAllocationSizeError(Exception):
   def __init__(self, pos: int):
      super().__init__("Incorrect allocate size at " + str(pos))
