import sys
from vm import VM
import argparse
from pathlib import Path



OPCODES = {
    'HALT': 0x00,
    'LOAD': 0x10,
    'MOV': 0x11,
    'PRINT': 0x15,
    'ADD': 0x20,
    'SUB': 0x21,
    'JMP': 0x25,
    'PUSH': 0x30,
    'POP': 0x31,
    'VIEW_STACK': 0x32,
    'SLEEP': 0x40,
    'VERBOSE': 0xFF
}
REGISTER_COUNTS = {
    'HALT': 0,
    'LOAD': 1,
    'MOV': 2,
    'PRINT': 1,
    'ADD': 2,
    'SUB': 2,
    'JMP': 0,
    'PUSH': 1,
    'POP': 1,
    'VIEW_STACK': 0,
    'SLEEP': 0,
    'VERBOSE': 0
}

def parse_number(operand: str) -> int:
    try:
        return int(operand, 0)
    except ValueError:
        raise ValueError(f"Invalid number: {operand}")

def parse_register(operand: str) -> int:
    if not operand.upper().startswith('R'):
        raise ValueError(f"Expected a register, got: {operand}")

    try:
        reg = int(operand[1:])
    except ValueError:
        raise ValueError(f"Invalid register: {operand}")

    if not 0 <= reg <= 15:
        raise ValueError(f"Register out of range: {operand}")

    return reg

def parse(line: str):
    line = line.strip()

    if not line or line.startswith('#'):
        return None

    parts = line.split(maxsplit=1)
    instr = parts[0].upper()

    if instr not in OPCODES:
        raise ValueError(f"Unknown instruction: {instr}")

    operands = (
        [operand.strip() for operand in parts[1].split(',')]
        if len(parts) > 1 else []
    )

    validate_operands(instr, operands)

    return instr, operands

def validate_operands(instr: str, operands: list):
    expected_counts = {
        'HALT': 0,
        'LOAD': 2,
        'MOV': 2,
        'PRINT': 1,
        'ADD': 2,
        'SUB': 2,
        'JMP': 1,
        'PUSH': 1,
        'POP': 1,
        'VIEW_STACK': 1,
        'SLEEP': 1,
        'VERBOSE': 0
    }

    if len(operands) != expected_counts[instr]:
        raise ValueError(
            f"{instr} expects {expected_counts[instr]} operands, "
            f"got {len(operands)}"
        )

    register_positions = {
        'LOAD': [0],
        'MOV': [0, 1],
        'PRINT': [0],
        'ADD': [0, 1],
        'SUB': [0, 1],
        'PUSH': [0],
        'POP': [0]
    }

    numeric_positions = {
        'LOAD': [1],
        'JMP': [0],
        'VIEW_STACK': [0],
        'SLEEP': [0]
    }

    for position in register_positions.get(instr, []):
        parse_register(operands[position])

    for position in numeric_positions.get(instr, []):
        parse_number(operands[position])

def encode(instr: str, operands: list) -> str:
    opcode = OPCODES[instr]

    if instr == 'HALT' or instr == 'VERBOSE':
        return f"0x{opcode:02X}000"

    if instr == 'LOAD':
        reg = parse_register(operands[0])
        value = parse_number(operands[1])
        return f"0x{opcode:02X}{reg:X}{value:X}"

    if instr in ('ADD', 'SUB', 'MOV'):
        reg = parse_register(operands[0])
        src = parse_register(operands[1])
        return f"0x{opcode:02X}{reg:X}{src:X}"

    if instr in ('PRINT', 'PUSH', 'POP'):
        reg = parse_register(operands[0])
        return f"0x{opcode:02X}{reg:X}0"

    if instr in ('JMP', 'VIEW_STACK', 'SLEEP'):
        value = parse_number(operands[0])
        return f"0x{opcode:02X}0{value:X}"

    raise ValueError(f"Cannot encode instruction: {instr}")

def assemble(lines: list[str]) -> list[str]:
    machine_code = []

    for line_number, line in enumerate(lines, start=1):
        try:
            parsed = parse(line)

            if parsed is None:
                continue

            instr, operands = parsed
            machine_code.append(encode(instr, operands))

        except ValueError as error:
            raise ValueError(f"Line {line_number}: {error}") from error

    return machine_code

def write_output(machine_code: list[str], filename: str):
    with open(filename, 'w') as f:
        f.write('\n'.join(machine_code))
        f.write('\n')


def main():
    parser = argparse.ArgumentParser(
        prog="vm",
        description="Assembler and virtual machine"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser(
        "build", help="Assemble an .asm file"
    )
    build_parser.add_argument("source", type=Path)
    build_parser.add_argument("-o", "--output", type=Path)

    run_parser = subparsers.add_parser(
        "run", help="Run an existing .hex file"
    )
    run_parser.add_argument("program", type=Path)

    build_run_parser = subparsers.add_parser(
        "build-run", help="Assemble and execute an .asm file"
    )
    build_run_parser.add_argument("source", type=Path)
    build_run_parser.add_argument("-o", "--output", type=Path)

    if len(sys.argv) > 1 and sys.argv[1].lower().endswith(".asm"):
        sys.argv.insert(1, "build-run")
    
    args = parser.parse_args()

    try:
        if args.command in ("build", "build-run"):
            lines = args.source.read_text().splitlines()
            machine_code = assemble(lines)

            output = args.output or args.source.with_suffix(".hex")
            write_output(machine_code, str(output))

            print(f"Assembly successful: {output}")

            if args.command == "build-run":
                VM().execute(machine_code)

        elif args.command == "run":
            machine_code = args.program.read_text().splitlines()
            VM().execute(machine_code)

    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
