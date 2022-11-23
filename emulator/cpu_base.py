from array import array
from typing import Callable, Optional


class CPUBase:
    def __init__(self) -> None:
        self.firmware = (
            array("f", [0]) * 512
        )  #'f' e não L porque os números estavam dando maior que L
        self._last_inst_idx = 0
        self._ops_dict: dict[str, int] = {}
        self._goto_idx: Optional[
            int
        ] = None  # armazena cada instrução e seu índice de início. Útil para o assembler
        self._control()  # adiciona as instruções

    def _make_instruction(
        self, instruction: int, next_decimal: Optional[int] = None, increment=True
    ) -> int:
        """Recebe a próxima instrução em decimal e o restante da instrução em binário
        e concatena as duas

        Args:
            instruction (int): Instrução sem o início que indica o próximo passo
            next_decimal (Optional[int], optional): Próximo instrução. Caso None, considerará o número atual+1.
                Caso 0, não incrementará o _last_inst_idx, uma vez que estará retornando à instrução 'main'
                Padrão é None.
            increment (bool, optional): Se irá incrementar o _last_inst_idx. Padrão é True.

        Returns:
            int: Instrução completa
        """
        next_decimal = self._last_inst_idx + 1 if next_decimal is None else next_decimal
        if increment and not next_decimal == 0:
            self._last_inst_idx += 1
        return (next_decimal << 27) + instruction

    def _init_instruction(self, name: str) -> None:
        """Chamada no início de toda instrução. Incrementa o último índice de instrução
        e guarda o valor no dicionário de instruções
        Args:
            name (str): Nome da nova instrução
        """
        self._last_inst_idx += 1
        self._ops_dict[name] = self._last_inst_idx

    def _main_op(self) -> None:
        # main: PC <- PC + 1; MBR <- read_byte(PC); GOTO MBR
        self.firmware[
            self._last_inst_idx
        ] = 0b000000000_100_00_110101_0010000_001_001_000

    def _add_op(self) -> None:
        """
        add x, v
        Adiciona v em x
        X = X + mem[address]
        """
        self._init_instruction("add x")
        # PC <- PC + 1; MBR <- read_byte(PC); GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # MAR <- MBR; read_word; GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010100_1000000_010_010_000
        )
        # X <- X + MDR; GOTO MAIN;
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_111100_0001000_000_011_100, 0
        )

    def _add_y(self) -> None:
        """
        add y, v
        Adiciona v em y
        Y = Y + mem[address]
        """
        self._init_instruction("add y")
        # PC <- PC + 1; MBR <- read_byte(PC); GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # MAR <- MBR; read_word; GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010100_1000000_010_010_000
        )
        # Y <- Y + MDR; GOTO MAIN;
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_111100_0000100_000_100_100, 0
        )

    def _mov_op(self) -> None:
        """
        mov x, v
        Guarda o valor de x em v
        mem[address] = X
        """
        # PC <- PC + 1; fetch; GOTO next
        self._init_instruction("mov")
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # MAR <- MBR; GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010100_1000000_000_010_000
        )
        # MDR <- X; write; GOTO main
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010100_0100000_100_011_000, 0
        )

    def _goto_op(self) -> None:
        """
        goto <address>
        Vai para a intrução com nome <address>
        """
        self._init_instruction("goto")
        self._goto_idx = self._last_inst_idx
        ##9: PC <- PC + 1; fetch; GOTO 10
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        ##10: PC <- MBR; fetch; GOTO MBR
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b100_00_010100_0010000_001_010_000, 0
        )

    def _jz_op(self) -> None:
        # if X = 0 then goto address
        ## 15: X <- X; IF ALU = 0 GOTO 272(100010000) ELSE GOTO 16(000010000)
        # self.firmware[15] = 0b000010000_001_00_010100_000100_000_011
        ## 16: PC <- PC + 1; GOTO 0
        # self.firmware[16] = 0b000000000_000_00_110101_001000_000_001
        ## 272: GOTO 13
        # self.firmware[272] = 0b000001101_000_00_000000_000000_000_000

        # if X = 0 goto address

        self._init_instruction("jz")
        nxt = self._last_inst_idx + 1
        # 11 X <- X; IF ALU = 0 GOTO (next + 256) ELSE GOTO 12 next;
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b001_00_010100_0001000_000_011_000
        )
        # 12 PC <- PC + 1; GOTO MAIN;
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_110101_0010000_000_001_000, 0
        )

        if self._goto_idx is None:
            raise ValueError(f"'goto' operation must be defined before 'jz'")
        # 268: GOTO goto
        self.firmware[nxt + 256] = self._make_instruction(
            0b000_00_000000_0000000_000_000_000, self._goto_idx, False
        )

    def _sub_op(self) -> None:
        """
        sub x, v
        Subtrai v de x
        X = X - mem[address]
        """
        # X = X - mem[address]
        ##6: PC <- PC + 1; fetch; goto 7
        # self.firmware[6] = 0b000000111_000_00_110101_001000_001_001
        ##7: MAR <- MBR; read; goto 8
        # self.firmware[7] = 0b000001000_000_00_010100_100000_010_010
        ##8: H <- MDR; goto 9
        # self.firmware[8] = 0b000001001_000_00_010100_000001_000_000
        ##9: X <- X - H; goto 0
        # self.firmware[9] = 0b000000000_000_00_111111_000100_000_011
        self._init_instruction("sub x")

        # PC <- PC + 1; fetch; goto next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # MAR <- MBR; read; GOTO next;
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010100_1000000_010_010_000
        )
        # X <- X - MDR; GOTO MAIN;
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_111111_0001000_000_011_100, 0
        )

    def _mul_xy(self) -> None:
        # TODO: incrementar PC
        # H = X * Y (MULTIPLICAÇÃO)         mnemônico sugerido mult
        self._init_instruction("mult")
        # 21: H <- 0; GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010000_0000010_000_000_000
        )
        nxt = self._last_inst_idx + 1
        # 22: IF ALU=0 Goto nxt+256 ;ELSE Goto nxt
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b001_00_010100_0000000_000_011_111
        )
        # 279: GOTO MAIN
        self.firmware[nxt + 256] = self._make_instruction(
            0b000_00_110101_0000000_001_001_000, 0
        )
        # 23: IF ALU=0 Goto nxt + 256 ;ELSE Goto 24
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b001_00_010100_0000000_000_100_111
        )
        # 280: GOTO MAIN
        self.firmware[self._last_inst_idx + 256] = self._make_instruction(
            0b000_00_110101_0000000_001_001_000, 0
        )

        # 24: H<- H + X; GOTO back 1
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_111100_0000010_000_011_000, self._last_inst_idx
        )
        save = self._last_inst_idx
        # 25: Y <- Y - 1; GOTO save
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_110110_0000100_000_100_111, save
        )
        # 26: IF ALU = 0 GOTO (next + 256); ELSE GOTO save
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b001_00_010100_0000000_000_100_111, save
        )
        # 282: GOTO main
        self.firmware[
            self._last_inst_idx + 256
        ] = 0b000000000_000_00_110101_0000000_001_001_000

    def _div_xy(self) -> None:
        # TODO: terminar de refatorar
        # TODO: incrementar PC
        # H= X/Y (DIVISÃO)         mnemônico sugerido div

        self._init_instruction("div")

        # 27: H<-0; GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010000_0000010_000_000_000
        )

        nxt = self._last_inst_idx + 1
        # 28: IF Y=0 GOTO nxt+256; ELSE GOTO nxt
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b001_00_010100_0000000_000_100_111
        )
        # 285: GOTO halt (Divisão por 0)
        self.firmware[nxt + 256] = self._make_instruction(
            0b000_00_110101_0000000_001_001_000, 255
        )

        nxt = self._last_inst_idx + 1
        # 29: IF X=0 GOTO nxt + 256; ELSE GOTO nxt
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b001_00_010100_0000000_000_011_111
        )
        # 286: GOTO main
        self.firmware[nxt + 256] = self._make_instruction(
            0b000_00_110101_0000000_001_001_000, 0
        )

        # 30: K<-0; GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010000_0000001_000_000_111
        )

        # 31: K<-K+1; GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_111001_0000001_000_000_011
        )

        nxt = self._last_inst_idx + 1
        # 32: IF Y-K=0 GOTO (nxt+256);ELSE GOTO nxt
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b001_00_111111_0000000_000_100_011
        )

        # 33: IF (X-K)=0 GOTO 289 ;ELSE GOTO 31
        self.firmware[33] = 0b000011111_001_00_111111_0000000_000_011_011
        # 287: GOTO MAIN
        self.firmware[nxt + 256] = self._make_instruction(
            0b000_00_110101_0000000_001_001_000, 0
        )
        # 35: H <- H+1; GOTO 29
        self.firmware[35] = 0b000011101_000_00_111001_0000010_000_111_000

        # 289: GOTO 35; X<- X-Y
        self.firmware[nxt + 256] = self._make_instruction(
            0b000_00_111111_0001000_000_011_010, self._last_inst_idx, False
        )

    def _mem_H(self) -> None:
        self._init_instruction("memH")  # TODO: escolher um nome melhor
        # mem[address] = H
        # 36: PC <- PC + 1; fetch; GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # 37: MAR <- MBR; GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010100_1000000_000_010_000
        )
        # 38: MDR <- X; write; GOTO main
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_011000_0100000_100_111_000, 0
        )

    def _x_set(self) -> None:
        # X = mem[address]
        self._init_instruction("set x")
        # 39: PC <- PC + 1; MBR <- read_byte(PC); GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # 40: MAR <- MBR; read_word; GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010100_1000000_010_010_000
        )
        # 41: X <- MDR; GOTO main
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010100_0001000_000_000_111, 0
        )

    def _y_mem(self) -> None:
        # Y = mem[address]
        # 42: PC <- PC + 1; MBR <- read_byte(PC); GOTO next
        self._init_instruction("set y")
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # 43: MAR <- MBR; read_word; GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010100_1000000_010_010_000
        )
        # 44: Y <- MDR; GOTO MAIN
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010100_0000100_000_000_111, 0
        )

    def _mem_y(self) -> None:
        # mem[address] = Y
        self._init_instruction("mov y")
        # 45: PC <- PC + 1; fetch; GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # 46: MAR <- MBR; GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010100_1000000_000_010_000
        )
        # 47: MDR <- X; write; GOTO main
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010100_0100000_100_100_111, 0
        )

    def _x_desl(self) -> None:  # TODO: o mesmo da operação de multiplicação por 2?
        # X = X(deslocado para a direita)
        # 48: X<-X deslocado
        self.firmware[48] = 0b0000000000_001_00_101000_0010000_000_111_11

    def _add1_op(self) -> None:
        # TODO: incrementar PC
        self._init_instruction("add1 x")
        ##49: X <- 1 + X; GOTO main
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_111001_0001000_000_011_000, 0
        )

    def _sub1_op(self) -> None:
        # TODO: incrementar PC
        self._init_instruction("sub1 x")
        ##50: H <- 1; GOTO next
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_110001_0000010_000_000_000
        )
        ##51: X <- X - H; GOTO main
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_111111_0001000_000_011_000, 0
        )

    def _set1_op(self) -> None:
        # TODO: incrementar PC
        self._init_instruction("set1 x")
        ##52: X <- 1; GOTO main
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_110001_0001000_000_011_000, 0
        )

    def _set0_op(self) -> None:
        # TODO: incrementar PC
        self._init_instruction("set0 x")
        ##53: X <- 0; GOTO main
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_010000_0001000_000_011_000, 0
        )

    def _set_1_op(self) -> None:  # TODO: Not working
        # TODO: incrementar PC
        self._init_instruction("set-1 x")
        ##54: X <- -1; GOTO main
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_00_110010_0001000_000_011_000, 0
        )

    def _div_op(self) -> None:  # TODO: some problems
        # TODO: incrementar PC
        self._init_instruction("div2 x")
        ##55: X <- X/2; GOTO main
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_10_011000_0001000_000_011_000, 0
        )

    def _mul_op(self) -> None:
        # TODO: incrementar PC
        self._init_instruction("mul2 x")
        ##56: X <- X*2; GOTO main
        self.firmware[self._last_inst_idx] = self._make_instruction(
            0b000_01_011000_0001000_000_011_000, 0
        )

    def _halt(self) -> None:
        """Halt instruction"""
        self._ops_dict["halt"] = 255
        self.firmware[255] = 0b000000000_000_00_000000_0000000_000_000_000

    def _control(self) -> None:
        """Adiciona todas as operações ao firmware da CPU"""
        # C => MAR, MDR, PC, X, Y, H
        # B => 000 = MDR, 001 = PC, 010 = MBR, 011 = x, 100 = Y
        self._main_op()

        self._add_op()  # X = X + mem[address]
        self._sub_op()  # X = X - mem[address]

        self._add_y()
        self._mul_xy()
        self._div_xy()
        self._mem_H()
        self._x_set()
        self._y_mem()
        self._mem_y()
        self._x_desl()

        self._mov_op()  # mem[address] = X
        self._goto_op()  # goto address
        self._add1_op()  # x = x+1
        self._sub1_op()  # x = x-1
        self._set1_op()  # x = 1
        self._set0_op()  # x = 0
        self._set_1_op()  # x = -1
        self._div_op()  # divisão por 2
        self._mul_op()  # multiplacação por 2
        self._jz_op()  # if X = 0 then goto address

        self._halt()  # halt
