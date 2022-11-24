from array import array
from typing import Callable, Optional


class CPUBase:
    def __init__(self) -> None:
        self.firmware = (
            array("Q", [0]) * 512
        )  #'Q' e não "L" porque temos mais de 32 bits em cada instrução
        self._next_idx = 0
        self._goto_idx: Optional[int] = None  # índice da operação de GOTO

        # para o assembler:
        # armazena cada instrução e seu índice de início.
        self._ops_dict: dict[str, int] = {}
        # operações agrupadas pelo número de argumentos.
        self._ops_args: dict[int, list[str]] = {}
        self._ops_move: list[str] = []
        self._control()  # adiciona as instruções

    def _make_instruction(
        self,
        instruction: int,
        next_decimal: Optional[int] = None,
        increment: bool = True,
    ) -> int:
        """Recebe a próxima instrução em decimal e o restante da instrução em binário
        e concatena as duas

        Args:
            instruction (int): Instrução sem o início que indica o próximo passo
            next_decimal (Optional[int], optional): Próximo instrução. Caso None, considerará o número atual+1.
                Caso 0, não incrementará o _next_idx, uma vez que estará retornando à instrução 'main'
                Padrão é None.
            increment (bool, optional): Se irá incrementar o _next_idx. Padrão é True.

        Returns:
            int: Instrução completa
        """
        next_decimal = self._next_idx + 1 if next_decimal is None else next_decimal
        if increment and not next_decimal == 0:
            self._next_idx += 1
        return (next_decimal << 27) + instruction

    def _init_instruction(self, name: str, args: int = 0, move=False) -> None:
        """Chamada no início de toda instrução. Incrementa o último índice de instrução
        e guarda o valor no dicionário de instruções
        Args:
            name (str): Nome da nova instrução
            args (int, optional): Número de argumentos da instrução. Padrão é 0
            move(bool, optional): Indicação se a operação realiza algum deslocamento especial (ex: jz e goto). Padrão é False
        """
        self._next_idx += 1
        self._ops_dict[name] = self._next_idx

        if args in self._ops_args.keys():
            self._ops_args[args].append(name)
        else:
            self._ops_args[args] = [name]

        if move:
            self._ops_move.append(name)

    def _main(self) -> None:
        # main: PC <- PC + 1; MBR <- read_byte(PC); GOTO MBR
        self.firmware[0] = 0b000000000_100_00_110101_0010000_001_001_000
        self._next_idx += 1

    def _add_x(self) -> None:
        """
        addX v
        Adiciona v em x
        X = X + mem[address]
        """
        self._init_instruction("addX", 1)
        # PC <- PC + 1; MBR <- read_byte(PC); GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # MAR <- MBR; read_word; GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_010100_1000000_010_010_000
        )
        # X <- X + MDR; GOTO main;
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_111100_0001000_000_111_011, 0
        )

    def _add_y(self) -> None:
        """
        addY v
        Adiciona v em y
        Y = Y + mem[address]
        """
        self._init_instruction("addY", 1)
        # PC <- PC + 1; MBR <- read_byte(PC); GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # MAR <- MBR; read_word; GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_010100_1000000_010_010_000
        )
        # Y <- Y + MDR; GOTO main;
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_111100_0000100_000_111_100, 0
        )

    def _mov_x(self) -> None:
        """
        movX v
        Guarda o valor de x em v
        mem[address] = X
        """
        # PC <- PC + 1; fetch; GOTO next
        self._init_instruction("movX", 1)
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # MAR <- MBR; GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_010100_1000000_000_010_000
        )
        # MDR <- X; write; GOTO main
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_010100_0100000_100_011_000, 0
        )

    def _mov_y(self) -> None:
        # mem[address] = Y
        self._init_instruction("movY", 1)
        # 45: PC <- PC + 1; fetch; GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # 46: MAR <- MBR; GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_010100_1000000_000_010_000
        )
        # 47: MDR <- X; write; GOTO main
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_010100_0100000_100_100_111, 0
        )

    def _goto(self) -> None:
        """
        goto <address>
        Vai para a intrução com nome <address>
        """
        self._init_instruction("goto", 1, True)
        self._goto_idx = self._next_idx
        ##9: PC <- PC + 1; fetch; GOTO 10
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        ##10: PC <- MBR; fetch; GOTO MBR
        self.firmware[self._next_idx] = self._make_instruction(
            0b100_00_010100_0010000_001_010_000, 0
        )

    def _jz(self) -> None:
        # if X = 0 then goto address
        ## 15: X <- X; IF ALU = 0 GOTO 272(100010000) ELSE GOTO 16(000010000)
        # self.firmware[15] = 0b000010000_001_00_010100_000100_000_011
        ## 16: PC <- PC + 1; GOTO 0
        # self.firmware[16] = 0b000000000_000_00_110101_001000_000_001
        ## 272: GOTO 13
        # self.firmware[272] = 0b000001101_000_00_000000_000000_000_000

        # TODO: fazer jz para Y
        # TODO: fazer jz para K
        # TODO: Ainda não está funcionando

        # if X = 0 goto address
        self._init_instruction("jzX", 1, True)
        is_zero = self._next_idx + 257
        # 11 IF X = 0 GOTO is_zero ELSE GOTO next;
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b001_00_010100_0001000_000_011_000
        )

        # X != 0
        # 12 PC <- PC + 1; GOTO main;
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_110101_0010000_000_001_000, 0
        )

        # X = 0
        # is_zero: PC <- PC + 1; fetch; GOTO next
        self.firmware[is_zero] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000, is_zero + 1, False
        )

        # PC <- MBR; fetch; GOTO MBR;
        self.firmware[is_zero + 1] = self._make_instruction(
            0b100_00_010100_0010000_001_010_000, 0
        )

    def _sub_x(self) -> None:
        """
        subX v
        Subtrai v de x
        X = X - mem[address]
        """
        self._init_instruction("subX", 1)

        # PC <- PC + 1; fetch; goto next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # MAR <- MBR; read; GOTO next;
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_010100_1000000_010_010_000
        )
        # X <- X - MDR; GOTO MAIN;
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_111111_0001000_000_011_111, 0
        )

    def _sub_y(self) -> None:
        """
        subY v
        Subtrai v de Y
        Y = Y - mem[address]
        """
        self._init_instruction("subY", 1)

        # PC <- PC + 1; fetch; goto next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # MAR <- MBR; read; GOTO next;
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_010100_1000000_010_010_000
        )
        # Y <- Y - MDR; GOTO MAIN;
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_111111_0000100_000_100_111, 0
        )

    def _mul_xy(self) -> None:
        """
        multXY
        Multiplica os valores de X por Y
        Guarda o resultado em X
        """
        self._init_instruction("multXY")

        # Zera H (será usado para incrementar os valores)
        # 28: H <- 0; GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_010000_0000010_000_000_000
        )

        # Verificar se uma das parcelas(X ou Y) é 0 -> se for, o resultado será 0
        nxt = self._next_idx + 1
        # 29: IF X=0 Goto (nxt+256); ELSE Goto nxt
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b001_00_010100_0000000_000_011_000
        )
        # (nxt+256): X<-H fetch; GOTO main
        self.firmware[nxt + 256] = self._make_instruction(
            0b000_00_010100_0001000_000_101_000, 0
        )
        nxt = self._next_idx + 1
        # 30: IF Y=0 Goto (nxt + 256) ;ELSE Goto 24
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b001_00_010100_0000000_000_100_000
        )
        # 287: X<-H;fetch; GOTO main
        self.firmware[nxt + 256] = self._make_instruction(
            0b000_00_010100_0001000_000_101_000, 0
        )

        # A cada vez que somar X em H, diminuirá 1 de Y e verificará se este é 0
        # Repete o processo até ser 0
        mark = self._next_idx
        # 31: H<- H + X; GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_111100_0000010_000_011_101
        )
        # 32: Y <- Y - 1; GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_110110_0000100_000_100_000
        )
        nxt = self._next_idx + 1
        # 33: IF Y = 0 GOTO (next + 256); ELSE GOTO mark
        self.firmware[self._next_idx] = self._make_instruction(
            0b001_00_010100_0000000_000_100_000, mark, False
        )

        # (nxt+256): PC <- PC + 1; GOTO main
        # X <- H; GOTO main
        self.firmware[nxt + 256] = self._make_instruction(
            0b000_00_010100_0001000_000_101_000, 0
        )

    def _div_xy(self) -> None:
        """divXY
        Divide o valor de X por Y
        Escreve o resultado em X
        Para mais detalhes, consultar fluxograma
        """

        self._init_instruction("divXY")
        # Começa zerando H
        # 34: H<-0; GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_010000_0000010_000_000_000
        )

        # Verifica se a divisão é válida (denominador != 0)
        y_is_0 = self._next_idx + 257
        # 35: IF Y=0 GOTO y_is_0; ELSE GOTO nxt
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b001_00_010100_0000000_000_100_000
        )
        # y_is_0: fetch; GOTO halt (Divisão por 0 -> Encerra o programa)
        self.firmware[y_is_0] = self._make_instruction(
            0b000_00_110101_0000000_001_001_000, 255, False
        )

        # Zera K
        start = self._next_idx  # onde inicia cada divisão
        # 37: K<-0; GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_010000_0000001_000_000_000
        )

        # Verifica se o numerador é 0
        end = self._next_idx + 257
        start_div = self._next_idx  # onde inicia o loop de cada divisão
        # start_div: IF X=0 GOTO (end); ELSE GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b001_00_010100_0000000_000_011_000
        )
        # end: X<-H; fetch; GOTO main -> Encerra a operação de divisão. Nesse caso, os números são divisíveis
        self.firmware[end] = self._make_instruction(
            0b000_00_010100_0001000_001_101_000, 0
        )

        # Incrementa K em 1
        inc_K = self._next_idx
        # 38 inc_K: K<-K+1; GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_111001_0000001_000_000_110
        )

        # Verifica se K já alcançou Y. Caso tenha alcançado, diminui X
        inc_H = self._next_idx + 257
        # 39: IF Y-K=0 GOTO (y_k0);ELSE GOTO nxt
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b001_00_111111_0000000_000_100_110
        )

        # > K != Y
        # Verifica se K é X.
        # Caso não seja, continua a divisão (incrementando K)
        # Caso seja, encerra a divisão e isso indica que os números não são divisíveis
        x_equal_k = self._next_idx + 257
        # 40: IF (X-K)=0 GOTO 289; ELSE GOTO inc_K
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b001_00_111111_0000000_000_011_110, inc_K
        )

        # >> K = X -> Não divisível
        # fetch, GOTO end -> Encerra a operação de divisão
        self.firmware[x_equal_k] = self._make_instruction(
            0b000_00_110101_0000000_001_001_000, 0
        )

        # > K = Y
        # inc_H: H <- H+1; GOTO sub_XY
        self.firmware[inc_H] = self._make_instruction(
            0b000_00_111001_0000010_000_101_000,
        )

        # sub_XY: X <- X-Y; GOTO start
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_111111_0001000_000_011_100, start, False
        )

    def _mem_H(self) -> None:
        self._init_instruction("memH", 1)  # TODO: escolher um nome melhor
        # mem[address] = H
        # 36: PC <- PC + 1; fetch; GOTO next
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # 37: MAR <- MBR; GOTO next
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_010100_1000000_000_010_000
        )
        # 38: MDR <- X; write; GOTO main
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_011000_0100000_100_111_000, 0
        )

    def _set_x(self) -> None:
        # X = mem[address]
        self._init_instruction("setX", 1)
        # 39: PC <- PC + 1; MBR <- read_byte(PC); GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # 40: MAR <- MBR; read_word; GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_010100_1000000_010_010_000
        )
        # 41: X <- MDR; GOTO main
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_010100_0001000_000_111_000, 0
        )

    def _set_y(self) -> None:
        # Y = mem[address]
        # 42: PC <- PC + 1; MBR <- read_byte(PC); GOTO next
        self._init_instruction("setY", 1)
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_110101_0010000_001_001_000
        )
        # 43: MAR <- MBR; read_word; GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b000_00_010100_1000000_010_010_000
        )
        # 44: Y <- MDR; GOTO MAIN
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_010100_0000100_000_111_000, 0
        )

    def _x_desl(self) -> None:  # TODO: o mesmo da operação de multiplicação por 2?
        # X = X(deslocado para a direita)
        # 48: X<-X deslocado
        self.firmware[48] = 0b0000000000_001_00_101000_0010000_000_111_11

    def _add1_x(self) -> None:
        # TODO: testar
        # TODO: incrementar PC
        self._init_instruction("add1X")
        ##49: X <- 1 + X; GOTO main
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_111001_0001000_000_011_000, 0
        )

    def _sub1_x(self) -> None:
        # TODO: incrementar PC
        # TODO: testar
        self._init_instruction("sub1X")
        ##50: H <- 1; GOTO next
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_110001_0000010_000_000_000
        )
        ##51: X <- X - H; GOTO main
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_111111_0001000_000_011_000, 0
        )

    def _set1_x(self) -> None:
        # TODO: incrementar PC
        # TODO: testar
        self._init_instruction("set1X")
        ##52: X <- 1; GOTO main
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_110001_0001000_000_011_000, 0
        )

    def _set0_x(self) -> None:
        # TODO: incrementar PC
        # TODO: testar
        self._init_instruction("set0X")
        ##53: X <- 0; GOTO main
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_010000_0001000_000_011_000, 0
        )

    def _set_1_x(self) -> None:  # TODO: Not working
        # TODO: incrementar PC
        # TODO: testar
        self._init_instruction("set-1X")
        ##54: X <- -1; GOTO main
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_00_110010_0001000_000_011_000, 0
        )

    def _div2_x(self) -> None:  # TODO: some problems
        # TODO: incrementar PC
        # TODO: testar
        self._init_instruction("div2X")
        ##55: X <- X/2; GOTO main
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_10_011000_0001000_000_011_000, 0
        )

    def _mul2_x(self) -> None:
        # TODO: incrementar PC
        # TODO: testar
        self._init_instruction("mul2X")
        ##56: X <- X*2; GOTO main
        self.firmware[self._next_idx] = self._make_instruction(
            0b000_01_011000_0001000_000_011_000, 0
        )

    def _halt(self) -> None:
        """Halt instruction"""
        self._ops_dict["halt"] = 255
        self._ops_args[0].append("halt")
        self.firmware[255] = 0b000000000_000_00_000000_0000000_000_000_000

    def is_greater_xy(self) -> None:
        """
        isGreaterXY
        Verifica se X > Y. Caso positivo, aloca 1 em X. Caso negativo, 0.
        Se são iguais, dirá que é maior.
        """

        self._init_instruction("isGreaterXY")

        # Y <- Y-1; if ALU = 0 GOTO greater; ELSE GOTO next
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b001_00_110110_0000100_000_100_000
        )
        greater = self._next_idx + 256

        # X <- X-1; if ALU = 0 GOTO lower; ELSE GOTO previous
        self.firmware[self._next_idx - 1] = self._make_instruction(
            0b001_00_110110_0001000_000_011_000, self._next_idx - 1
        )
        lower = self._next_idx + 256

        # lower: X <- 0; GOTO main
        self.firmware[lower] = self._make_instruction(
            0b000_00_010000_0001000_000_000_011, 0
        )
        # greater: X <- 1; GOTO main
        self.firmware[greater] = self._make_instruction(
            0b000_00_110001_0001000_000_000_011, 0
        )

    def _control(self) -> None:
        """Adiciona todas as operações ao firmware da CPU"""
        # C => MAR, MDR, PC, X, Y, H
        # A,B => 111 = MDR, 001 = PC, 010 = MBR, 011 = x, 100 = Y
        self._main()
        self._jz()  # if X = 0 then goto address
        self._goto()  # goto address

        self._add_x()  # X = X + mem[address]
        self._add_y()  # Y = Y + mem[address]

        self._sub_x()  # X = X - mem[address]
        self._sub_y()  # Y = Y - mem[address]

        self._set_x()  # X = mem[address]
        self._set_y()  # Y = mem[address]

        self._mov_y()  # mem[address] = Y
        self._mov_x()  # mem[address] = X

        self._mul_xy()
        self._div_xy()
        # self._mem_H()

        # self._x_desl()

        # self._add1_x()  # x = x+1
        # self._sub1_x()  # x = x-1
        # self._set1_x()  # x = 1
        # self._set0_x()  # x = 0
        # self._set_1_x()  # x = -1
        # self._div2_x()  # divisão por 2
        # self._mul2_x()  # multiplicação por 2

        self._halt()  # halt

        self.is_greater_xy()
