import logging
import sys
from datapath import DataPath
from control_unit import ControlUnit
from isa import read_code
from mc import mc_memory

TICK_LIMIT = 5000


def simulation(code: list, input_tokens: list):
    datapath = DataPath(input_tokens)
    control_unit = ControlUnit(code, datapath)
    logging.debug(repr(control_unit))
    instructions = 0
    try:
        while control_unit.current_tick() < TICK_LIMIT:
            if control_unit.mpc == 0:
                instructions += 1
            control_unit.dispatch_micro_instruction(mc_memory[control_unit.mpc])
            logging.debug(repr(control_unit))
            logging.debug(f"INPUT: {datapath._io[10]} OUTPUT: {datapath._io[11]}")
    except StopIteration:
        pass

    if control_unit.current_tick() == TICK_LIMIT:
        logging.warning("Tick Limit!")

    out = "".join(map(lambda x: str(x), datapath._io[11]))
    logging.debug("OUTPUT: "+ out)
    
    return out, instructions, control_unit.current_tick()


def main(code_file: str, input_file: str):
    code = read_code(code_file)

    with open(input_file, encoding="utf-8") as f:
        input_text = f.read().strip()
        if not input_text:
            input_tokens = []
        else:
            input_tokens = eval(input_text)

    output, instruction_counter, ticks = simulation(code, input_tokens)
    print(f"instr_counter: {instruction_counter} ticks: {ticks}")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)

    assert (
        len(sys.argv) == 3
    ), "Invalid usage: python3 machine.py <code_file> <input_file>"
    main(sys.argv[1], sys.argv[2])
