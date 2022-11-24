goto main
wb 0

r ww 0 #output
a ww 400 #input
v ww 0

main  addX a 
      goto loop

loop  div2X #dois
      movX v
      set0X
      addX v
      div2X #quatro

      mul2X
      mul2X
      subX a
      jz biss #bissexto
      goto nbiss

biss  set1X #bissexto
      goto resp

nbiss set0X
      goto resp

resp movX r
    halt