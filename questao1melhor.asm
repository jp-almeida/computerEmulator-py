goto main
wb 0

r ww 0 #output
a ww 400 #input
v ww 0

main  add x, a 
      goto loop

loop  div x #dois
      mov x, v
      set0 x
      add x, v
      div x #quatro

      mul x
      mul x
      sub x, a
      jz x, biss #bissexto
      goto nbiss

biss  set1 x #bissexto
      goto resp

nbiss set0 x
      goto resp

resp mov x, r
    halt