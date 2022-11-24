goto main
wb 0
 
r ww 0 #output
a ww 100 #input
d ww 0 #numero que esta sendo multiplicado por ele mesmo
g ww 0 #resultado de cada multiplicacao

main setX a
     setY d
     jz x, final #eh zero
     sub1X
     add1Y
     movY d
     jz x, final #eh um

     goto multip

multip add1Y
     movY d
     setX d
     multXY
     movX r
     comp

#verifica se achou o numero desejado
comp subX a
     jz x, final
     isGreaterXY
     
     jz x, multip #se nao eh maior, continua
     goto final

final setX d
    movX r
    halt


