from assembler import Assembler
from emulator import CPU

if __name__ == "__main__":
  assembler = Assembler("questao1melhor.asm")
  assembler.execute()

  cpu = CPU()
  cpu.read_image("program.bin")

  print("passos ", cpu.execute())
  print("x:", cpu._regs.X)
  print("a:", cpu._memory._memory[2])
  print("r:", cpu._memory._memory[1])
