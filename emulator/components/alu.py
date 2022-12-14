"""
f0 | f1 | enA | enB | invA | inc
0    1     1     0     0      0     ->   A
0    1     0     1     0      0     ->   B
0    1     1     0     1      0     ->   ¬A
1    0     1     1     0      0     ->   ¬B 
1    1     1     1     0      0     ->   A + B
1    1     1     1     0      1     ->   A + B + 1
1    1     1     0     0      1     ->    A + 1
1    1     0     1     0      1     ->   B + 1
1    1     1     1     1      1     ->   B - A
1    1     0     1     1      0     ->   B-1
1    1     1     0     1      1     ->   -A
0    0     1     1     0      0     ->   A and B
0    1     1     1     0      0     ->   A or B
0    1     0     0     0      0     ->   0
1    1     0     0     0      1     ->   1
1    1     0     0     1      0     ->   -1
"""


class ALU:
    def __init__(self) -> None:
        self.N = 0  # não é zero
        self.Z = 1  # é zero

    @staticmethod
    def _parse_operation(operation: int) -> tuple:
        """Divide a operação de acordo com os bits de controle da arquitetura (sll8, sra1, f0, f1, enA, enB, invA, inc)
        Args:
            operation (int): Bits de controle
        Returns:
            tuple: Operação dividida
        """
        return (
            (operation & 0b11000000) >> 6,  # shift_bits
            (operation & 0b00110000) >> 4,  # f0,f1
            (operation & 0b00001000) >> 3,  # enA
            (operation & 0b00000100) >> 2,  # enB
            (operation & 0b00000010) >> 1,  # invA
            operation & 0b00000001,  # inc
        )

    @staticmethod
    def _parse_operation2(operation: int) -> tuple:

        return (
            (operation & 0b11000000) >> 6,  # shift_bits
            (operation & 0b00111111),  # control bits
        )

    def operation(self, control_bits: int, a: int, b: int) -> int:
        """Instruções para a operação da ULA
        Args:
            control_bits (int): bits de controle de acordo com a arquitetura (sll8, sra1, f0, f1, enA, enB, invA, inc)
            a (int): valor A
            b (int): valor B
        Returns:
            int: Resultado da operação
        """
        # shift_bits, op, en_a, en_b, inv_a, inc = self._parse_operation(control_bits)
        shift_bits, control_bits = self._parse_operation2(control_bits)

        if control_bits == 0b011000:
            res = a
        elif control_bits == 0b010100:
            res = b
        elif control_bits == 0b011010:
            res = ~a
        elif control_bits == 0b101100:
            res = ~b
        elif control_bits == 0b111100:
            res = a + b
        elif control_bits == 0b111101:
            res = a + b + 1
        elif control_bits == 0b111001:
            res = a + 1
        elif control_bits == 0b110101:
            res = b + 1
        elif control_bits == 0b111111:
            res = b - a
        elif control_bits == 0b110110:
            res = b - 1
        elif control_bits == 0b111011:
            res = -a
        elif control_bits == 0b001100:
            res = a & b
        elif control_bits == 0b011100:
            res = a | b
        elif control_bits == 0b010000:
            res = 0
        elif control_bits == 0b110001:
            res = 1
        elif control_bits == 0b110010:
            res = -1
        else:
            raise ValueError("Invalid ALU input ", control_bits)

        # atualiza N e Z
        self.N = int(bool(res))
        self.Z = int(not res)

        if shift_bits == 0b11:  # soma com 256
            res = res << 8
        elif shift_bits:  # divisão ou multiplicação por 2
            res = res << 1 if shift_bits == 0b01 else res >> 1

        return res
