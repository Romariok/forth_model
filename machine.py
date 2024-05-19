import logging
import sys

from control_unit import ControlUnit
from datapath import DataPath
from isa import read_code
from mc import mc_memory

TICK_LIMIT = 7000


def simulation(code: list, input_tokens: list, memory: dict):
    datapath = DataPath(input_tokens)
    datapath.fill_memory(memory)
    control_unit = ControlUnit(code, datapath)
    logging.debug(repr(control_unit))
    instructions = 0
    try:
        while control_unit.current_tick() < TICK_LIMIT:
            if control_unit.mpc == 0:
                instructions += 1
            control_unit.dispatch_micro_instruction(mc_memory[control_unit.mpc])
            logging.debug(repr(control_unit))
    except StopIteration:
        pass

    if control_unit.current_tick() == TICK_LIMIT:
        logging.warning("Tick Limit!")

    out = "".join(map(lambda x: chr(x) if x > 9 and x <= 255 else str(x), datapath._io[11]))
    logging.debug("OUTPUT: " + out)
    return out, instructions, control_unit.current_tick()


def main(code_file: str, input_file: str):
    code, memory = read_code(code_file)
    if input_file is None:
        input_tokens = []
    else:
        with open(input_file) as f:
            input_tokens = [*list(f.read()), chr(0)]
    output, instruction_counter, ticks = simulation(code, input_tokens, memory)
    print(f"instr_counter: {instruction_counter} ticks: {ticks}")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)

    assert len(sys.argv) <= 3, "Invalid usage: python3 machine.py <code_file> [<input_file>]"
    assert len(sys.argv) >= 2, "Invalid usage: python3 machine.py <code_file> [<input_file>]"
    if len(sys.argv) == 2:
        main(sys.argv[1], None)
    else:
        main(sys.argv[1], sys.argv[2])
