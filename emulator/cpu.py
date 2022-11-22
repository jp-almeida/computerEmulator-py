from array import array
from typing import Optional

from .components import ALU, Bus, Registers
from .memory import Memory


class CPU:
    """Emulates a CPU"""

    def __init__(self) -> None:
        self._regs = Registers()
        self._alu = ALU()
        self._bus = Bus()
        self.firmware = array("L", [0]) * 512
        self._memory = Memory()
        self._last_inst_idx = 0
        self._control()

    def read_image(self, img: str) -> None:
        """Reads a .bin file
        Args:
            img (str): path to the file
        """
        byte_address = 0
        with open(img, "rb") as disk:
            while byte := disk.read(1):
                self._memory.write_byte(byte_address, int.from_bytes(byte, "little"))
                byte_address += 1

    def _read_registers(self, register_number: int) -> None:
        self._bus.BUS_A = self._regs.H
        self._bus.BUS_B = self._regs.get_reg(register_number)

    def _write_registers(self, register_bits: int) -> None:
        self._regs.write_reg(register_bits, self._bus.BUS_C)

    def _alu_operation(self, control_bits: int) -> None:
        if not control_bits:
            return
        self._bus.BUS_C = self._alu.operation(
            control_bits, self._bus.BUS_A, self._bus.BUS_B
        )

    def _next_instruction(self, next_instruction: int, jam: int) -> None:
        if jam == 0b000:
            self._regs.MPC = next_instruction
            return

        if jam & 0b001:
            next_instruction |= self._alu.Z << 8
        elif jam & 0b010:
            next_instruction |= self._alu.N << 8
        elif jam & 0b100:
            next_instruction |= self._regs.MBR

        self._regs.MPC = next_instruction

    def _memory_io(self, mem_bits: int) -> None:
        if mem_bits & 0b001:
            self._regs.MBR = self._memory.read_byte(self._regs.PC)
        elif mem_bits & 0b010:
            self._regs.MDR = self._memory.read_word(self._regs.MAR)
        elif mem_bits & 0b100:
            self._memory.write_word(self._regs.MAR, self._regs.MDR)

    def _step(self) -> bool:
        """
        Executa cada passo
        Retorna:
          bool -> se ainda existe passo a ser executado ou não
        """
        self._regs.MIR = self.firmware[self._regs.MPC]

        if self._regs.MIR == 0:
            return False
        nxt, jam, alu, w_regs, mem, r_regs, _ = self._parse_instruction(self._regs.MIR)

        self._read_registers(r_regs)
        self._alu_operation(alu)
        self._write_registers(w_regs)
        self._memory_io(mem)
        self._next_instruction(nxt, jam)

        return True

    @staticmethod
    def _parse_instruction(instruction: int) -> tuple:
        return (
            (instruction & 0b111111111_000_00_000000_0000000_000_000_000) >> 27, #next instruction
            (instruction & 0b000000000_111_00_000000_0000000_000_000_000) >> 24, #jam
            (instruction & 0b000000000_000_11_111111_0000000_000_000_000) >> 16, #alu
            (instruction & 0b000000000_000_00_000000_1111111_000_000_000) >> 9, #w_regs
            (instruction & 0b000000000_000_00_000000_0000000_111_000_000) >> 6, #mem
            (instruction & 0b000000000_000_00_000000_0000000_000_111_000) >> 3, #r_regs
            (instruction & 0b000000000_000_00_000000_0000000_000_000_111),
        )

    def make_instruction(self, instruction, next_decimal: Optional[int] = None) -> int:
        """
        Recebe a próxima instrução em decimal e o restante da instrução em binário
        e concatena as duas
        """
        next_decimal = self._last_inst_idx + 1 if next_decimal is None else next_decimal
        return (next_decimal << 27) + instruction
      
    def execute(self) -> int:
        """
        Execução
        Retorna:
            int: Número de passos
        """
        ticks = 0
        while self._step():
            ticks += 1
        return ticks

    def __str__(self) -> str:
        output = {}
        idx = 0
        for data in self.firmware:
            if data:
                output[str(idx)] = data
            idx += 1

        return str(output)

    def _main_op(self) -> None:
        # main: PC <- PC + 1; MBR <- read_byte(PC); GOTO MBR
        self.firmware[0] = 0b000000000_100_00_110101_001000_001_001

    def _add_op(self) -> None:
        """
        add x, v
        Adiciona v em x 
        X = X + mem[address]
        """
        #2: PC <- PC + 1; MBR <- read_byte(PC); GOTO 3
        self.firmware[2] = 0b000000011_000_00_110101_0010000_001_001_000 
        #3: MAR <- MBR; read_word; GOTO 4
        self.firmware[3] = 0b000000011_000_00_010100_1000000_010_010_000 
        #5: X <- X + MDR; GOTO MAIN;
        self.firmware[4] = 0b000000000_000_00_111100_0001000_000_011_100  
    
    def _add_y(self) -> None:
        """
        add y, v
        Adiciona v em y 
        Y = Y + mem[address]
        """
        #17: PC <- PC + 1; MBR <- read_byte(PC); GOTO 18
        self.firmware[17] = 0b000010010_000_00_110101_0010000_001_001_000 
        #18: MAR <- MBR; read_word; GOTO 20   
        self.firmware[18] = 0b000010100_000_00_010100_1000000_010_010_000 
        #20: Y <- Y + MDR; GOTO MAIN;    
        self.firmware[20] = 0b000000000_000_00_111100_0000100_000_100_100 
    
  def _mov_op(self) -> None:
        """
        mov x, v
        Guarda o valor de x em v
        mem[address] = X
        """
        # mem[address] = X
        ##6: PC <- PC + 1; fetch; GOTO 7
        self.firmware[6] = 0b000000111_000_00_110101_0010000_001_001_000 
        ##7: MAR <- MBR; GOTO 8                            
        self.firmware[7] = 0b000001000_000_00_010100_1000000_000_010_000
        ##8: MDR <- X; write; GOTO 0  
        self.firmware[8] = 0b000000000_000_00_010100_0100000_100_011_000

    def _goto_op(self) -> None:
        """
        goto <address>
        Vai para a intrução com nome <address>
        """
        ##9: PC <- PC + 1; fetch; GOTO 10
        self.firmware[9] = 0b000001010_000_00_110101_0010000_001_001_000
        ##10: PC <- MBR; fetch; GOTO MBR
        self.firmware[10] = 0b000000000_100_00_010100_0010000_001_010_000

    def _jz_op(self) -> None:
        # if X = 0 then goto address
        ## 15: X <- X; IF ALU = 0 GOTO 272(100010000) ELSE GOTO 16(000010000)
        # self.firmware[15] = 0b000010000_001_00_010100_000100_000_011
        ## 16: PC <- PC + 1; GOTO 0
        # self.firmware[16] = 0b000000000_000_00_110101_001000_000_001
        ## 272: GOTO 13
        # self.firmware[272] = 0b000001101_000_00_000000_000000_000_000
      
        #if X = 0 goto address
        #11 X <- X; IF ALU = 0 GOTO 268 (100001100) ELSE GOTO 12 (000001100);
        self.firmware[11]  = 0b000001100_001_00_010100_0001000_000_011_000 
        #12 PC <- PC + 1; GOTO MAIN;
        self.firmware[12]  = 0b000000000_000_00_110101_0010000_000_001_000 
        # 268: GOTO 9
        self.firmware[268] = 0b000001101_000_00_000000_0000000_000_000_000 
      
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
      
        #13: PC <- PC + 1; fetch;
        self.firmware[13] = 0b000001110_000_00_110101_0010000_001_001_000 
        #14: MAR <- MBR; read; GOTO 16;    
        self.firmware[14] = 0b000010000_000_00_010100_1000000_010_010_000 
        #16: X <- X - MDR; GOTO MAIN;    
        self.firmware[16] = 0b000000000_000_00_111111_0001000_000_011_100 

    def _mul_xy(self) -> None:
        #H = X * Y (MULTIPLICAÇÃO)         mnemônico sugerido mult
        #21: H <- 0; GOTO 22
        self.firmware[21] =0b000010110_000_00_010000_0000010_000_000_000
        #22: IF ALU=0 Goto 279 ;ELSE Goto 23
        self.firmware[22]= 0b000010111_001_00_010100_0000000_000_011_111
        #279: GOTO MAIN
        self.firmware[279]=0b000000000_000_00_110101_0000000_001_001_000 
        #23: IF ALU=0 Goto 280 ;ELSE Goto 24
        self.firmware[23]= 0b000011000_001_00_010100_0000000_000_100_111
        #280: GOTO MAIN    
        self.firmware[280]=0b000000000_000_00_110101_0000000_001_001_000
        #24: H<- H + X; GOTO 23     
        self.firmware[24]= 0b000011001_000_00_111100_0000010_000_011_000
        #25: Y <- Y - 1; GOTO 24    
        self.firmware[25] =0b000011010_000_00_110110_0000100_000_100_111
        #26: IF ALU = 0 GOTO 278;ELSE GOTO 24    
        self.firmware[26] =0b000011000_001_00_010100_0000000_000_100_111
        #282: GOTO MAIN    
        self.firmware[282]=0b000000000_000_00_110101_0000000_001_001_000

    def _div_xy(self) -> None:
        #H= X/Y (DIVISÃO)         mnemônico sugerido div
        #27: H<-0
        self.firmware[27]= 0b000011100_000_00_010000_0000010_000_000_000
        #28: IF Y=0 GOTO 285; ELSE GOTO 29             
        self.firmware[28]= 0b000011101_001_00_010100_0000000_000_100_111    
        #285: GOTO HALT              
        self.firmware[285]=0b011111111_000_00_110101_0000000_001_001_000
        #29: IF X=0 GOTO 286; ELSE GOTO 30            
        self.firmware[29]= 0b000011110_001_00_010100_0000000_000_011_111 
        #286: GOTO MAIN            
        self.firmware[286]=0b000000000_000_00_110101_0000000_001_001_000
        #30: K<-0           
        self.firmware[30]= 0b000011111_000_00_010000_0000001_000_000_111
        #31: K<-K+1            
        self.firmware[31]= 0b000100000_000_00_111001_0000001_000_000_011
        #32: IF Y-K=0 GOTO 289;ELSE GOTO 33            
        self.firmware[32]= 0b000100001_001_00_111111_0000000_000_100_011
        #289: GOTO 35; X<- X-Y            
        self.firmware[289]=0b000100011_000_00_111111_0001000_000_011_010
        #33: IF (X-K)=0 GOTO 289 ;ELSE GOTO 31            
        self.firmware[33]= 0b000011111_001_00_111111_0000000_000_011_011
        #287: GOTO MAIN            
        self.firmware[287]=0b000000000_000_00_110101_0000000_001_001_000
        #35: H <- H+1; GOTO            
        self.firmware[35]= 0b000011101_000_00_111001_0000010_000_111_000

    def _mem_H(self) -> None:
        #mem[address] = H
        #36: PC <- PC + 1; fetch; GOTO 37
        self.firmware[36] = 0b000100101_000_00_110101_0010000_001_001_000 
        #37: MAR <- MBR; GOTO 38            
        self.firmware[37] = 0b000100110_000_00_010100_1000000_000_010_000 
        #38: MDR <- X; write; GOTO MAIN            
        self.firmware[38] = 0b000000000_000_00_011000_0100000_100_111_000 
                    
    def _x_set(self) -> None:
        #X = mem[address]         mnemônico sugerido set
        #39: PC <- PC + 1; MBR <- read_byte(PC); GOTO 40
        self.firmware[39] = 0b000101000_000_00_110101_0010000_001_001_000 
        #40: MAR <- MBR; read_word; GOTO 41           
        self.firmware[40] = 0b000101001_000_00_010100_1000000_010_010_000 
        #41: X <- MDR; GOTO MAIN            
        self.firmware[41] = 0b000000000_000_00_010100_0001000_000_000_111 

    def _y_mem(self) -> None:
        #Y = mem[address]
        #42: PC <- PC + 1; MBR <- read_byte(PC); GOTO 43
        self.firmware[42] = 0b000101011_000_00_110101_0010000_001_001_000 
        #43: MAR <- MBR; read_word; GOTO 44            
        self.firmware[43] = 0b000101100_000_00_010100_1000000_010_010_000 
        #44: Y <- MDR; GOTO MAIN            
        self.firmware[44] = 0b000000000_000_00_010100_0000100_000_000_111 
                    
    def _mem_y(self) -> None:
        #mem[address] = Y
        #45: PC <- PC + 1; fetch; GOTO 34
        self.firmware[45] = 0b000101110_000_00_110101_0010000_001_001_000 
        #46: MAR <- MBR; GOTO 35            
        self.firmware[46] = 0b000101111_000_00_010100_1000000_000_010_000 
        #47: MDR <- X; write; GOTO MAIN            
        self.firmware[47] = 0b000000000_000_00_010100_0100000_100_100_111 

    def _x_desl(self) -> None:
        # X = X(deslocado para a direita)
        #48: X<-X deslocado
        self.firmware[48] =0b0000000000_001_00_101000_0010000_000_111_11
                        

    def _add1_op(self) -> None:
        ##49: X <- 1 + X; GOTO 0    
        self.firmware[49] = 0b000000000_000_00_111001_0001000_000_011_000

    def _sub1_op(self) -> None:
        ##50: H <- 1; goto 19
        self.firmware[50] = 0b000010011_000_00_110001_0000010_000_000_000
        ##51: X <- X - H; goto 0
        self.firmware[51] = 0b000000000_000_00_111111_0001000_000_011_000

    def _set1_op(self) -> None:
        ##52: X <- 1; goto 0
        self.firmware[52] = 0b000000000_000_00_110001_0001000_000_011_000

    def _set0_op(self) -> None:
        ##53: X <- 0; goto 0
        self.firmware[53] = 0b000000000_000_00_010000_0001000_000_011_000

    def _set_1_op(self) -> None:  # TODO: Not working
        ##54: X <- -1; goto 0
        self.firmware[54] = 0b000000000_000_00_110010_0001000_000_011_000

    def _div_op(self) -> None:  # TODO: some problems
        ##55: X <- X/2; goto 0
        self.firmware[55] = 0b000000000_000_10_011000_0001000_000_011_000

    def _mul_op(self) -> None:
        ##56: X <- X*2; goto 0
        self.firmware[56] = 0b000000000_000_01_011000_0001000_000_011_000

    def _halt(self) -> None:
        """Halt instruction"""
        self.firmware[255] = 0b000000000_000_00_000000_0000000_000_000_000

    def _control(self) -> None:
        # C => MAR, MDR, PC, X, Y, H
        # B => 000 = MDR, 001 = PC, 010 = MBR, 011 = x, 100 = Y
        self._main_op()

        self._add_op()  # X = X + mem[address]
        self._sub_op()  # X = X - mem[address]
      
        # 🛑🛑 coloquei as operações adicionadas aqui, mas tá sem os 'op' no final do nome e também não sei nome melhor pra elas k
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
        self._add1_op()
        self._sub1_op()
        self._set1_op()
        self._set0_op()
        self._set_1_op()
        self._div_op()
        self._mul_op()
        self._jz_op()  # if X = 0 then goto address

        self._halt()
