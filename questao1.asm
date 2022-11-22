goto main
wb 0

r ww 0 #output
a ww 400 #input
um ww 1

main add x, a 
    jz x, biss #em_caso_de_a_ser_zero
    goto loop

loop sub1 x #um
    jz x, resp #nao_bissexto
    sub1 x #dois
    jz x, resp #nao_bissexto
    sub1 x #tres
    jz x, resp #nao_bissexto
    sub1 x #quatro
    jz x, biss #bissexto
    goto loop

biss set1 x #bissexto
    goto resp

resp mov x, r
    halt