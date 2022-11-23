from io import IOBase
from typing import Union
from .cpu_base import CPUBase


class Assembler:
    def __init__(self, source: str, output: str = "program.bin") -> None:
        self.source_file = source
        self.output_file = output
        self.lines: list[list[str]] = []
        self.lines_bin: list[list[Union[str, list]]] = []
        self.names: dict[str, int] = {}  # Nomes e seus valores correspondentes em bytes
        # TODO: adicionar as novas microinstruções
        self.instruction_set = {
            "add": 0x02,
            "sub": 0x06,
            "goto": 0x0D,
            "mov": 0x0A,
            "jz": 0x0F,
            "add1": 0x11,
            "sub1": 0x12,
            "set1": 20,
            "set0": 21,
            "set-1": 22,
            "div": 23,
            "mul": 24,
            "halt": 0xFF,
        }
        self.instructions = list(self.instruction_set.keys()) + ["wb", "ww"]

    def _is_instruction(self, token: str) -> bool:
        """
        Retorna se é uma instrução ou não
        """
        return token in self.instructions

    def _is_name(self, token: str) -> bool:
        """
        Retorna se é um nome ou não
        """
        return token in self.names.keys()

    def _encode_simple_ops(self, inst: str, ops: list) -> list:
        """
        Transforma as instruções mais simples em binário (adição, subtração etc)
        """
        if len(ops) > 1 and ops[0] == "x":
            if self._is_name(ops[1]):
                return [self.instruction_set[inst], ops[1]]
        raise ValueError("Invalid input ", ops)
        # TODO: Fazer para os novos registradores

    def _encode_goto(self, ops: list) -> list:
        """Encode da operação goto"""
        if len(ops) > 0 and self._is_name(ops[0]):
            return [self.instruction_set["goto"], ops[0]]
        else:
            raise ValueError("Invalid input ", ops)

    def _encode_wb(self, ops: list) -> list:
        """Encode da operação de escrever bytes"""
        if len(ops) > 0 and ops[0].isnumeric() and int(ops[0]) < 256:
            return [int(ops[0])]
        else:
            raise ValueError("Invalid input ", ops)

    def _encode_ww(self, ops: list) -> list:
        """
        Instrução de escrever em uma variável
        raises:
            ValueError -> Valor da variável excedeu 2^32 (valor máximo)
        """
        if len(ops) > 0 and ops[0].isnumeric():
            line_bin = []
            val = int(ops[0])

            if val < pow(2, 32):
                line_bin.append(val & 0xFF)
                line_bin.append((val & 0xFF00) >> 8)
                line_bin.append((val & 0xFF0000) >> 16)
                line_bin.append((val & 0xFF000000) >> 24)
                return line_bin
            else:
                raise ValueError("Number exceeded max value of 2^32")

        else:
            raise ValueError("Invalid input ", ops)

    def _encode_instruction(self, instruction: str, ops: list) -> list:
        """
        Retorna a instrução dada em binário
        """
        if instruction in ("add", "sub", "mov", "jz", "ms"):  # simple ops
            return self._encode_simple_ops(instruction, ops)
        elif instruction == "goto":
            return self._encode_goto(ops)
        elif instruction in (
            "halt",
            "add1",
            "sub1",
            "set1",
            "set0",
            "set-1",
            "div",
            "mul",
        ):
            return [self.instruction_set[instruction]]
        elif instruction == "wb":
            return self._encode_wb(ops)
        elif instruction == "ww":
            return self._encode_ww(ops)
        else:
            return []

    def _line_to_bin_step1(self, line) -> list:
        """
        Converte a linha inteira de instrução para binário
        """
        return (
            self._encode_instruction(line[0], line[1:])
            if self._is_instruction(line[0])
            else self._encode_instruction(line[1], line[2:])
        )

    def _lines_to_bin_step1(self) -> None:
        """
        Converte todas as linhas para binário
        """
        for line in self.lines:
            if not (line_bin := self._line_to_bin_step1(line)):
                raise SyntaxError("Line ", self.lines.index(line))
            self.lines_bin.append(line_bin)

    def _find_line_for_names(self) -> None:
        """
        Armazena todos os nomes no atributo self.names com a linha em que ele aparece
        """
        for idx, line in enumerate(self.lines):
            if line[0] not in self.instructions:
                self.names[line[0]] = idx

    def _count_bytes(self, line_number: int) -> int:
        """
        Conta os butes desde o início até a linha dada.
        É utilizado para achar os bytes dos nomes
        """
        line = 0
        byte = 1
        while line < line_number:
            byte += len(self.lines_bin[line])
            line += 1
        return byte

    def _get_name_byte(self, name: str) -> int:
        """Retorna o valor em bytes de um nome"""
        return self.names[name]

    def _resolve_names(self) -> None:
        for name in self.names.keys():
            self.names[name] = self._count_bytes(self.names[name])

        for line in self.lines_bin:
            for i in range(len(line)):
                if self._is_name(line[i]):
                    line[i] = self._get_name_byte(line[i]) // (
                        4
                        if line[i - 1]
                        in (self.instruction_set[op] for op in ["add", "sub", "mov"])
                        else 1
                    )

    def _load_tokens(self, file: IOBase) -> None:
        """
        Trata as strings tokens para encaixar em um padrão
        """
        # TODO: ignorar comentário com espaço
        for l in file:
            tokens = [
                t
                for t in str(l).replace("\n", "").replace(",", "").lower().split(" ")
                if t and t[0] != "#"  # ignora comentários
            ]
            if tokens:
                self.lines.append(tokens)

    def execute(self) -> None:
        """Executa o assembler"""

        with open(self.source_file, "r") as fsrc:
            self._load_tokens(fsrc)  # carrega os tokens
            self._find_line_for_names()  # salva os nomes

            self._lines_to_bin_step1()
            self._resolve_names()
            byte_arr = [0]

            for line in self.lines_bin:
                for byte in line:
                    byte_arr.append(byte)

            with open(self.output_file, "wb") as fdst:
                fdst.write(bytearray(byte_arr))