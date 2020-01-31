"""CPU functionality."""

import sys

LDI = 0b10000010 # LDI
HLT = 0b00000001 # HLT
PRN = 0b01000111 # PRN R0
MUL = 0b10100010 # MUL R0,R1
PUSH = 0b01000101 # PUSH R0
POP = 0b01000110 # POP R0
CALL = 0b01010000 # CALL R1
RET = 0b00010001 # RET
ADD = 0b10100000 # ADD R0,R0
# new-------
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.sp = 7
        self.reg[self.sp] = 0xF4
        self.fl = 0 # only the equal flag currently
        self.branchtable = {
            LDI: self.handle_ldi,
            PRN: self.handle_prn,
            MUL: self.handle_mul,
            PUSH: self.handle_push,
            POP: self.handle_pop,
            CALL: self.handle_call,
            RET: self.handle_ret,
            ADD: self.handle_add,
            CMP: self.handle_cmp,
            JMP: self.handle_jmp,
            JEQ: self.handle_jeq,
            JNE: self.handle_jne
        }

    def load(self, filename):
        """Load a program into memory."""
        try:
            address = 0
            with open(filename) as f:
                for line in f:
                    comment_split = line.split('#')
                    num = comment_split[0].strip()

                    if num == "":
                        continue

                    value = int(num, 2)

                    self.ram[address] = value
                    address += 1
            # print(self.ram)

        except FileNotFoundError:
            print(f'{sys.argv[0]}: {filename} not found')
            sys.exit(2)

    # Memory Address Register (MAR) -------?
    def ram_read(self, mar):
        # print(mar) #debug
        return self.ram[mar]

    # Memory Data Register (MDR) ----------?
    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'CMP':
            value_A = self.reg[reg_a]
            value_B = self.reg[reg_b]
            if value_A == value_B:
                self.flag = 1
            else:
                self.flag = 0 

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

# --------------------------------------Handler functions-------------
    def handle_ldi(self):
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)

        self.reg[operand_a] = operand_b
        self.pc += 3

    def handle_prn(self):
        operand_a = self.ram_read(self.pc+1)

        print(self.reg[operand_a])
        self.pc += 2

    def handle_mul(self):
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)

        self.alu('MUL', operand_a, operand_b)

        self.pc += 3

    def handle_add(self):
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)

        self.alu('ADD', operand_a, operand_b)

        self.pc += 3

    def handle_push(self):
        operand_a = self.ram_read(self.pc+1)
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], self.reg[operand_a])

        self.pc += 2

    def handle_pop(self):
        operand_a = self.ram_read(self.pc+1)
        value = self.ram_read(self.reg[self.sp])
        self.reg[operand_a] = value
        self.reg[self.sp] += 1

        self.pc += 2

    def handle_call(self):
        operand_a = self.ram_read(self.pc+1) #the reg with the address
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], self.pc+2)
        self.pc = self.reg[operand_a]


    def handle_ret(self):
        value = self.ram_read(self.reg[self.sp])

        self.reg[self.sp] += 1

        self.pc = value

    def handle_cmp(self):
        operand_a = self.ram_read(self.pc+1)
        operand_b = self.ram_read(self.pc+2)

        self.alu('CMP', operand_a, operand_b)

        self.pc += 3

    def handle_jmp(self):
        operand_a = self.ram_read(self.pc+1)
        self.pc = self.reg[operand_a]

    def handle_jeq(self):
        if self.flag: # is 1
            self.handle_jmp()
        else:
            self.pc += 2

    def handle_jne(self):
        if not self.flag:
            self.handle_jmp()
        else:
            self.pc += 2

#------------------------------------------RUN()------------------------------
    def run(self):
        """Run the CPU."""

        HLT = 0b00000001 # HLT

        running = True

        while running:
            ir = self.ram_read(self.pc)
            if ir == HLT:
                running = False
                self.pc += 1
            elif ir != HLT:
                self.branchtable[ir]()