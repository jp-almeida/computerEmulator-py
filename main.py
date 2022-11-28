from emulator import CPU, Assembler


def main():
    assembler = Assembler("questao1.asm")
    assembler.execute()

    cpu = CPU(True)
    cpu.read_image("program.bin")

    print("passos ", cpu.execute())
    print("--- registradores")
    print("X:", cpu._regs.X)
    print("Y:", cpu._regs.Y)
    print("K:", cpu._regs.K)
    print("H:", cpu._regs.H)
    print("--- variaveis")

    for num, var in enumerate(["in_out", "qtr", "cem"]):
        print(f"{var}: {cpu._memory._memory[num+1]}")


if __name__ == "__main__":
    main()
    # teste()
