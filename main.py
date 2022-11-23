from emulator import CPU, Assembler, CPUBase


def main():
    assembler = Assembler("questao1melhor.asm")
    assembler.execute()

    cpu = CPU()
    cpu.read_image("program.bin")

    print("passos ", cpu.execute())
    print("x:", cpu._regs.X)
    print("a:", cpu._memory._memory[2])
    print("r:", cpu._memory._memory[1])


def teste():
    assembler = Assembler("teste.asm")
    print(assembler.instruction_set)
    assembler.execute()
    cpu = CPU()
    cpu.read_image("program.bin")
    print("passos ", cpu.execute())
    print("x:", cpu._regs.X)
    print("a:", cpu._memory._memory[1])


if __name__ == "__main__":
    # main()
    teste()
