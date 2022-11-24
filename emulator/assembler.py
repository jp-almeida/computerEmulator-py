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

        cpu_base = CPUBase()
        self.instruction_set = cpu_base._ops_dict

        self.inst_args_1 = cpu_base._ops_args[1]  # instruções com 1 argumento
        self.inst_args_0 = cpu_base._ops_args[0]  # intruções com nenhum argumento
        self.inst_move = cpu_base._ops_move  # recebem como argumento um marcador
        # todas as instruções
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

    def _encode_1_arg_ops(self, inst: str, ops: list) -> list:
        """
        Transforma em binário as instruções que exigem um argumento (adição, subtração etc)
        """
        if len(ops) > 0 and self._is_name(ops[0]):
            return [self.instruction_set[inst], ops[0]]

        raise ValueError("Invalid input ", ops)

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

    def _encode_instruction(self, instruction: str, ops: list) -> list[int]:
        """
        Retorna a instrução dada em binário
        """
        # if instruction == "goto":
        #     return self._encode_goto(ops)
        if instruction == "wb":
            return self._encode_wb(ops)
        elif instruction == "ww":
            return self._encode_ww(ops)
        elif instruction in self.inst_args_1:  # operações com 1 argumento
            return self._encode_1_arg_ops(instruction, ops)
        elif instruction in self.inst_args_0:  # operações com nenhum argumento
            return [self.instruction_set[instruction]]
        else:
            return []

    def _line_to_bin(self, line) -> list:
        """
        Converte a linha inteira de instrução para binário
        """
        return (
            self._encode_instruction(line[0], line[1:])
            if self._is_instruction(line[0])
            else self._encode_instruction(
                line[1], line[2:]
            )  # casos que tem um marcador antes
        )

    def _lines_to_bin(self) -> None:
        """
        Converte todas as linhas para binário
        """
        for line in self.lines:
            if not (line_bin := self._line_to_bin(line)):
                raise SyntaxError(f"Line {line}")  # self.lines.index(line) + 1)
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
        Conta os bytes desde o início até a linha dada.
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

                if self._is_name(line[i]):  # type: ignore
                    line[i] = self._get_name_byte(line[i]) // (  # type: ignore
                        4
                        if line[i - 1]  # type: ignore
                        in [
                            self.instruction_set[op]
                            for op in self.inst_args_1
                            if op not in self.inst_move
                        ]
                        else 1
                    )

    def _load_tokens(self, file: IOBase) -> None:
        """
        Trata as strings tokens para encaixar em um padrão e ignorar comentários
        """
        for line in file.readlines():
            l = str(line).split("#")[0]  # ignora comentários de linha

            tokens = [t for t in l.replace("\n", "").replace(",", "").split(" ") if t]

            if tokens:
                self.lines.append(tokens)

    def _write_file(self) -> None:
        """Escreve no arquivo binário"""
        byte_arr = [0]
        for line in self.lines_bin:
            for byte in line:
                byte_arr.append(byte)  # type: ignore

            with open(self.output_file, "wb") as out:
                out.write(bytearray(byte_arr))

    def execute(self) -> None:
        """Executa o assembler"""

        with open(self.source_file, "r") as src:
            self._load_tokens(src)  # carrega os tokens

        self._find_line_for_names()  # salva os nomes
        self._lines_to_bin()  # converte todas as linhas para binário
        self._resolve_names()
        self._write_file()
