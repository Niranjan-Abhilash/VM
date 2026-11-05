import sys
import time

OP_HALT = 0x00
OP_LOAD = 0x10
OP_MOV = 0x11
OP_PRINT = 0x15
OP_ADD = 0x20
OP_SUB = 0x21
OP_JMP = 0x25
OP_PUSH = 0x30
OP_POP = 0x31
OP_VIEW_STACK = 0x32
OP_SLEEP = 0x40
OP_VERBOSE = 0xFF

class VM:
    def __init__(self):
        self.registers = [0] * 16
        self.stack = [0] * 1024
        self.running = True
        self.sp = 0
        self.verbose = False

    def parse(self, line: str):
        line = line.strip()
        if not line.startswith('0x') or len(line) < 5:
            print("Skipping line[comment]: ", line)
            return None
        try:
            op_str = line[2:4]
            reg_str = line[4:5]
            param_str = line[5:]

            opcode = int(op_str, 16)
            reg = int(reg_str, 16)
            param = int(param_str, 16) if param_str else 0

            return {'opcode': opcode, 'reg': reg, 'param': param}
        except ValueError:
            print('ERROR: Failed to parse valid hex data from line: ', line)
            return None

    def execute(self, program: list):
        print("\n-------------Starting VM-------------\n")
        
        program = [self.parse(line) for line in program]
        program = [inst for inst in program if inst is not None]

        pc = 0
        self.running = True

        while self.running and pc < len(program):
            inst = program[pc]
            pc += 1
            opcode = inst['opcode']
            reg = inst['reg']
            param = inst['param']

            if opcode == OP_VERBOSE:
                self.verbose = not self.verbose
                print(f"Verbose is set to {self.verbose}")

            elif opcode == OP_LOAD:
                self.registers[reg] = param
                if self.verbose: print(f"[LOAD] Register R{reg} contains value: {param}") 

            elif opcode == OP_ADD:
                src_reg = param
                self.registers[reg] += self.registers[src_reg]
                if self.verbose: print(f"[ADD] Added R{src_reg} into R{reg}. New R{reg} value: {self.registers[reg]}") 
                
            elif opcode == OP_SUB:
                src_reg = param
                self.registers[reg] -= self.registers[src_reg]
                if self.verbose: print(f"[SUB] Subtracted R{src_reg} into R{reg}. New R{reg} value: {self.registers[reg]}")

            elif opcode == OP_MOV:
                src_reg = param
                self.registers[reg] = self.registers[src_reg]
                if self.verbose: print(f"[MOV] Mover value of R{src_reg} to R{reg}")
            
            elif opcode == OP_PRINT:
                print(f"[PRINT] Register R{reg} contains value: {self.registers[reg]}") 

            elif opcode == OP_JMP:
                pc = param
                if self.verbose: print(f"[JMP] Jumped to address: {param}") 

            elif opcode == OP_PUSH:
                self.stack[self.sp] = self.registers[reg]
                self.sp += 1
                # print(self.stack)
                if self.verbose: print(f"[STACK_PUSH] Pushed value of R{reg} to stack") 
            
            elif opcode == OP_POP:
                self.registers[reg] = self.stack[self.sp - 1] 
                self.sp -= 1
                self.stack[self.sp] = 0
                if self.verbose: print(f"[STACK_POP] Popped value of stack to R{reg}") 

            elif opcode == OP_VIEW_STACK:
                print([self.stack[x] for x in range(param)])


            elif opcode == OP_SLEEP:
                time.sleep(param)

            elif opcode == OP_HALT:
                self.running = False
                if self.verbose: print("[HALT] Halted VM") 
                
            else:
                print(f"Error: Unknown Opcode 0x{opcode:02X} encountered at instruction index {pc-1}")
                self.running = False

        print("\n-------------Terminated VM-------------\n")
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vm.py <filename>")
        sys.exit(1)
        
    filename = sys.argv[1]
    try:
        with open(filename, 'r') as f:
            file = f.readlines()
    except FileNotFoundError:
        print(f"ERROR: File '{filename}' not found.")
        sys.exit(1)

    vm = VM()
    vm.execute(file)

# OP_HALT = 0x00
# OP_LOAD = 0x10
# OP_ADD = 0x20
# OP_SUB = 0x30
# OP_PRINT = 0x40
