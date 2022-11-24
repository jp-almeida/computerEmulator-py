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

    def operation(self, control_bits: int, a: int, b: int) -> int:
        """Instruções para a operação da ULA
        Args:
            control_bits (int): bits de controle de acordo com a arquitetura (sll8, sra1, f0, f1, enA, enB, invA, inc)
            a (int): valor A
            b (int): valor B
        Returns:
            int: Resultado da operação
        """
        shift_bits, op, en_a, en_b, inv_a, inc = self._parse_operation(control_bits)

        if op == 0b01:
            res = ((-a if inv_a else a) if en_a else 0) | (b if en_b else 0)
        elif op == 0b11:  # soma
            res = (
                ((-a if inv_a else a) if en_a else 0)
                + (b if en_b else 0)
                + (-inc if inv_a and not en_a else (0 if inv_a and en_a else inc))
            )
        elif en_a and en_b:
            res = a & b if op == 0b00 else ~b
        else:
            raise ValueError("Invalid ALU input ", control_bits)

        if control_bits == 0b110010:
            res = -1

        # atualiza N e Z
        self.N = int(bool(res))
        self.Z = int(not res)

        if shift_bits == 0b11:  # soma com 256
            res = res << 8
        elif shift_bits:  # divisão ou multiplicação por 2
            res = res << 1 if shift_bits == 0b01 else res >> 1

        return res
