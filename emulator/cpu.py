from array import array
from typing import Optional

from emulator.cpu_base import CPUBase

from .components import ALU, Bus, Registers
from .memory import Memory


class CPU(CPUBase):
    """Emulates a CPU"""

    def __init__(self) -> None:
        super().__init__()
        self._regs = Registers()
        self._alu = ALU()
        self._bus = Bus()
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

    def execute(self) -> int:
        """
        Execução da CPU
        Retorna:
            int: Número de passos
        """
        ticks = 0
        while self._step():
            ticks += 1
        return ticks

    def _read_registers(self, regist_B: int, regist_A: int) -> None:
        self._bus.BUS_A = self._regs.get_reg(regist_A)
        self._bus.BUS_B = self._regs.get_reg(regist_B)

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
        self._regs.MIR = int(self.firmware[self._regs.MPC])

        if self._regs.MIR == 0:
            return False
        nxt, jam, alu, w_regs, mem, r_regsB, r_regsA = self._parse_instruction(
            self._regs.MIR
        )

        self._read_registers(r_regsB, r_regsA)
        self._alu_operation(alu)
        self._write_registers(w_regs)
        self._memory_io(mem)
        self._next_instruction(nxt, jam)

        return True

    @staticmethod
    def _parse_instruction(instruction: int) -> tuple:
        instruction = int(instruction)
        return (
            (instruction & 0b111111111_000_00_000000_0000000_000_000_000)
            >> 27,  # next instruction
            (instruction & 0b000000000_111_00_000000_0000000_000_000_000) >> 24,  # jam
            (instruction & 0b000000000_000_11_111111_0000000_000_000_000) >> 16,  # alu
            (instruction & 0b000000000_000_00_000000_1111111_000_000_000)
            >> 9,  # w_regs
            (instruction & 0b000000000_000_00_000000_0000000_111_000_000) >> 6,  # mem
            (instruction & 0b000000000_000_00_000000_0000000_000_111_000)
            >> 3,  # r_regs
            (instruction & 0b000000000_000_00_000000_0000000_000_000_111),
        )

    def __str__(self) -> str:
        output = {}
        idx = 0
        for data in self.firmware:
            if data:
                output[str(idx)] = data
            idx += 1

        return str(output)
