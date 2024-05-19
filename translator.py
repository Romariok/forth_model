from __future__ import annotations

import re
import sys

from exceptions import BadAllocationSizeError, TokenTranslationError
from isa import Arg, ArgType, Instruction, Opcode, Term, write_code

variables = {}
variable_current_address = 0
functions = {}
memory = {}


def clear_line(line) -> str:
    """Чистит строку от лишних пробелов и комментариев"""
    new_line = re.sub(r"\n", "", line)
    new_line = re.sub(r"\\.*", "", new_line)
    return new_line.replace('"', "").rstrip()


def is_str(value: str) -> bool:
    return bool(re.fullmatch(r"^\".*\"|\'.*\'$"))


def is_int(value: str) -> bool:
    return bool(re.fullmatch(r"^-?\d+$", value))


def is_math(value: str) -> bool:
    return len(value) == 1 and value in ["*", "/", "+", "-", "mod"]


def is_comparator_word(value: str) -> bool:
    return value in ["=", "<", "<=", ">", ">=", "<>"]


def is_word(value: str) -> bool:
    return bool(re.fullmatch(r"[a-zA-Z][a-zA-Z\\_0-9\"]*", value))


def is_def_word(value: str) -> bool:
    return value in [";", ":"]


def is_variable_operation(value: str) -> bool:
    return value in ["!", "@"]


def is_console_operation(value: str) -> bool:
    return value in ["read", "emit"]


def set_cycles(terms: list[Term]) -> None:
    """Проверяет валидность циклов"""
    blocks_loop = []
    blocks_until = []

    for term_index, term in enumerate(terms):
        match term.name:
            case "do":
                blocks_loop.append(term.number)
            case "loop":
                assert len(blocks_loop) > 0, "Unbalanced DO-LOOP at " + str(term.number)
                term.operand = blocks_loop.pop() - 1
            case "begin":
                blocks_until.append(term.number + 1)
            case "until":
                assert len(blocks_until) > 0, "Unbalanced BEGIN-UNTIL at " + str(term.number)
                term.operand = blocks_until.pop() - 1
            case _:
                continue
    assert len(blocks_loop) == 0 and len(blocks_until) == 0, "Unbalanced cycles"  # noqa: PT018


def set_functions(terms: list[Term]) -> None:
    """Проверяет валидность функций"""
    func_indexes = []

    for term_index, term in enumerate(terms):
        if term.name[0] == ":":
            assert len(func_indexes) == 0, f"Unclosed function at {term.number}"
            func_indexes.append(term.number - 1)
            func_name = terms[term_index + 1].name
            assert func_name not in functions, f"Duplicate function {func_name}"
            functions[func_name] = term.number + 1
            terms[term_index + 1].converted = True
        elif term.name == ";":
            assert len(func_indexes) >= 1, f"RET for unknown function at {term.number}"
            function_term = terms[func_indexes.pop()]
            function_term.operand = term.number
    assert len(func_indexes) == 0, "Unclosed function"


def line_to_term(pos: int, char_seq: str) -> [int, list[Term]]:
    """Переводит код в список токенов"""
    terms: list[Term] = []
    for code_char_seq in re.split(r"\s+", char_seq.strip()):
        pos += 1
        if (
            is_int(code_char_seq)
            or is_math(code_char_seq)
            or is_comparator_word(code_char_seq)
            or is_word(code_char_seq)
            or is_variable_operation(code_char_seq)
            or is_def_word(code_char_seq)
            or is_console_operation(code_char_seq)
        ):
            if len(terms) != 0 and terms[-1].name[:2] == '."':
                new_term_name = terms[-1].name + char_seq[char_seq.find(".") + 2 :] + '"'
                terms[-1].name = new_term_name
            else:
                terms.append(Term(pos, code_char_seq))
        elif char_seq[char_seq.find(".") : char_seq.find(".") + 2] == ". ":
            terms.append(Term(pos, '."'))
        else:
            raise TokenTranslationError(pos)
    return pos, terms


def split_to_terms(lines: list[str]) -> list[Term]:
    """Трансляция текста в последовательность токенов"""

    terms: list[Term] = []
    pos = 0
    for line_num, line in enumerate(lines, 1):
        quotes_split = re.split('"', clear_line(line))
        assert len(quotes_split) % 2 == 1  # их должно быть четное кол-во

        char_seq = clear_line(line)
        if len(char_seq.strip()) == 0:
            continue
        pos, part_terms = line_to_term(pos, char_seq)
        terms.extend(part_terms)

    return terms


def replace_variables_and_functions(terms: list[Term]):
    for term_index, term in enumerate(terms):
        if term.name in functions.keys() and not term.converted:
            term.operand = functions[term.name]
            term.name = "call"
        if term.name in variables and not term.converted:
            term.name = str(variables[term.name])


def set_variables(terms: list[Term]) -> None:
    """Проверяет валидность переменных"""
    global variable_current_address
    for term_index, term in enumerate(terms):
        if term.name == "variable":
            assert is_word(terms[term_index + 1].name), f"Unaccaptable variabel defenition at {term.number}"
            assert terms[term_index + 1].name not in variables, f"Variable already defined at {term.number}"
            variables[terms[term_index + 1].name] = variable_current_address
            variable_current_address += 1
            terms[term_index + 1].converted = True
            if term_index + 3 < len(terms) and terms[term_index + 3].name == "allocate":
                set_allocate(terms, term_index + 3)


def set_allocate(terms: list[Term], term_num: int) -> None:
    global variable_current_address
    term = terms[term_num]
    terms[term_num - 1].converted = True
    memory[variable_current_address - 1] = int(terms[term_num - 1].name)
    try:
        allocate_size = int(terms[term_num - 1].name) + 1
        assert 1 <= allocate_size <= 100, "Incorrect allocate size at " + str(term.word_number - 1)
        variable_current_address += allocate_size
    except ValueError:
        raise BadAllocationSizeError(term.word_number - 1) from None


def set_conditional(terms: list[Term]) -> None:
    """Проверяет валидность условных операторов"""
    blocks = []

    for term_index, term in enumerate(terms):
        if term.name == "if":
            blocks.append(term)
        elif term.name == "else":
            blocks.append(term)
        elif term.name == "then":
            assert len(blocks) > 0, "Unbalanced IF-ELSE-THEN at " + str(term.number)
            last_if = blocks.pop()
            if last_if.name == "else":
                last_else = last_if
                assert len(blocks) > 0, "Unbalanced IF-ELSE-THEN at " + str(term.number)
                last_if = blocks.pop()
                last_else.operand = term.number
                last_if.operand = last_else.number
            else:
                last_if.operand = term.number
    assert len(blocks) == 0, "Unbalanced IF-ELSE-THEN"


def code_correctness_check(terms: list[Term]):
    """Проверка формальной корректности кода"""
    set_variables(terms)
    set_functions(terms)
    set_cycles(terms)
    set_conditional(terms)
    replace_variables_and_functions(terms)


def fix_addresses(term_instructions: list[list[Instruction]]) -> list[Instruction]:
    final_instructions = []
    term_lens = [0]

    for instr_num, instruction in enumerate(term_instructions):
        term_lens.append(term_lens[instr_num] + len(instruction))

    for term_instruction in term_instructions:
        if term_instruction is not None:
            for instruction in term_instruction:
                for param_num, param in enumerate(instruction.arg):
                    if param.argtype is ArgType.ADD:
                        instruction.arg[param_num].value = term_lens[param.value] - 1
                        instruction.arg[param_num].argtype = ArgType.CONST
                final_instructions.append(instruction)

    return final_instructions


def term_to_instruction(term: Term) -> list(Instruction):
    """Переводит токен в инструкции"""
    instructions = {
        "-": [Instruction(Opcode.SUB, [])],
        "+": [Instruction(Opcode.ADD, [])],
        "/": [Instruction(Opcode.DIV, [])],
        "*": [Instruction(Opcode.MUL, [])],
        "=": [Instruction(Opcode.EQ, [])],
        "mod": [Instruction(Opcode.MOD, [])],
        ">": [Instruction(Opcode.GR, [])],
        "<": [Instruction(Opcode.LS, [])],
        "swap": [Instruction(Opcode.SWAP, [])],
        "drop": [Instruction(Opcode.DROP, [])],
        "dup": [Instruction(Opcode.DUP, [])],
        "over": [Instruction(Opcode.OVER, [])],
        "read": [Instruction(Opcode.READ, [])],
        "emit": [Instruction(Opcode.EMIT, [])],
        "variable": [],
        "allocate": [],
        "do": [
            Instruction(Opcode.POP, []),
            Instruction(Opcode.POP, []),
        ],
        "begin": [],
        "until": [Instruction(Opcode.ZJMP, [Arg(ArgType.UNDEFINED, None)])],
        "call": [Instruction(Opcode.CALL, [Arg(ArgType.UNDEFINED, None)])],
        ":": [Instruction(Opcode.JMP, [Arg(ArgType.UNDEFINED, None)])],
        ";": [Instruction(Opcode.RET, [])],
        "if": [Instruction(Opcode.ZJMP, [Arg(ArgType.UNDEFINED, None)]), Instruction(Opcode.DROP, [])],
        "else": [Instruction(Opcode.JMP, [Arg(ArgType.UNDEFINED, None)])],
        "then": [],
        "!": [Instruction(Opcode.STORE, [])],
        "@": [Instruction(Opcode.LOAD, [])],
        "loop": [
            Instruction(Opcode.RPOP, []),
            Instruction(Opcode.RPOP, []),
            Instruction(Opcode.PUSH, [Arg(ArgType.CONST, 1)]),
            Instruction(Opcode.ADD, []),
            Instruction(Opcode.OVER, []),
            Instruction(Opcode.OVER, []),
            Instruction(Opcode.LS, []),
            Instruction(Opcode.ZJMP, [Arg(ArgType.UNDEFINED, None)]),
            Instruction(Opcode.DROP, []),
            Instruction(Opcode.DROP, []),
        ],
        "i": [
            Instruction(Opcode.RPOP, []),
            Instruction(Opcode.RPOP, []),
            Instruction(Opcode.OVER, []),
            Instruction(Opcode.OVER, []),
            Instruction(Opcode.POP, []),
            Instruction(Opcode.POP, []),
            Instruction(Opcode.SWAP, []),
            Instruction(Opcode.DROP, []),
        ],
    }.get(term.name)
    if term.operand is not None and instructions is not None:
        for instruction in instructions:
            for param_num, param in enumerate(instruction.arg):
                if param.argtype == ArgType.UNDEFINED:
                    instruction.arg[param_num].value = term.operand
                    instruction.arg[param_num].argtype = ArgType.ADD

    if instructions is None:
        if term.name in functions or term.name in variables or term.converted:
            instructions = []
        else:
            instructions = [Instruction(Opcode.PUSH, [Arg(ArgType.CONST, term.name)])]

    return instructions


def terms_to_instructions(terms: list[Term]) -> list[Instruction]:
    instructions = list(map(term_to_instruction, terms))
    instructions = fix_addresses(instructions)
    return [*instructions, Instruction(Opcode.HALT, [])]


def translate(lines):
    terms = split_to_terms(lines)
    code_correctness_check(terms)

    instructions: list[Instruction] = []

    instructions = terms_to_instructions(terms)

    commands = []
    for index, instruction in enumerate(instructions):
        command = {
            "index": index,
            "command": instruction.opcode,
        }

        if len(instruction.arg):
            command["arg"] = int(instruction.arg[0].value)
        commands.append(command)
    return commands


def main(source, target):
    global variable_current_address, variables, memory, functions
    variables = {}
    variable_current_address = 0
    functions = {}
    memory = {}
    with open(source, encoding="utf-8") as f:
        source = f.read().splitlines()
    code = translate(source)

    write_code(target, code, memory)
    print("source LoC:", len(source), "code instr:", len(code))


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Invalid usage: python3 translator.py <source> <target>"
    main(sys.argv[1], sys.argv[2])
