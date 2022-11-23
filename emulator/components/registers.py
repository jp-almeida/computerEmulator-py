class Registers:
    def __init__(self) -> None:
        self.MPC = 0
        self.MIR = 0
        self.MAR = 0  # | w: 0b1000000
        self.MDR = 0  # r: 0 | w: 0b0010000
        self.PC = 0  # r: 1 | w: 0b0010000
        self.MBR = 0  # r: 2 | w:
        self.X = 0  # r: 3 | w: 0b0001000
        self.Y = 0  # r: 4 | w: 0b0000100
        self.H = 0  # r: 5 | w: 0b0000010
        self.K = 0  # r: 6 | w: 0b0000001
        self.N = 0
        self.Z = 1

    def get_reg(self, reg_num: int) -> int:
        """Retorna o valor do registro para o número dado
        Args:
            reg_num (int): número do registro
        Returns:
            int: valor do registro
        """
        # TODO: vê se precisa colocar outros números
        return (
            [self.MDR, self.PC, self.MBR, self.X, self.Y, self.H, self.K][reg_num]
            if reg_num in range(7)
            else 0
        )

    def write_reg(self, reg_bits: int, value: int) -> None:
        """Armazena o valor dado em um registro
        Args:
            reg_bits (int): Bits para o registro (baseado na microarquitetura)
            value (int): valor para armazenar
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
        """Converte a classe para string"""
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
