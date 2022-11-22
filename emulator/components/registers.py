class Registers:
    def __init__(self) -> None:
        self.MPC = 0
        self.MIR = 0
        self.MAR = 0 # | w: 0b1000000
        self.MDR = 0 # r: 0 | w: 0b0010000
        self.PC = 0  # r: 1 | w: 0b0010000
        self.MBR = 0
        self.X = 0
        self.Y = 0 #w: 0b0000100
        self.H = 0
        self.K   = 0
        self.N   = 0
        self.Z   = 1

    def get_reg(self, reg_num: int) -> int:
        """returns the value of a register (based on the given number)
        Args:
            reg_num (int): register's number
        Returns:
            int: register's value
        """
        return (
            [self.MDR, self.PC, self.MBR, self.X, self.Y, self.H][reg_num]
            if reg_num in range(5)
            else 0
        )

    def write_reg(self, reg_bits: int, value: int) -> None:
        """Writes the given value to a given register
        Args:
            reg_bits (int): Bits for the register (based on the microarchitecture)
            value (int): value to write
        """
        if reg_bits & 0b1000000:
            self.MAR = value
        elif reg_bits & 0b0100000:
            self.MDR = value
        elif reg_bits & 0b0010000:
            self.PC = value
        elif reg_bits & 0b0001000:
            self.X = value
        elif reg_bits & 0b0000100:
            self.Y = value
        elif reg_bits & 0b0000010:
            self.H = value
        elif reg_bits & 0b0000001:
            self.K = value

    def __str__(self):
        return f"""
MPC = {self.MPC}
MIR = {self.MIR}
MAR = {self.MAR}
MDR = {self.MDR}
PC = {self.PC}
MBR = {self.MBR}
X = {self.X}
Y = {self.Y}
H = {self.H}
K = {self.K}
N = {self.N}
Z = {self.Z}
"""
