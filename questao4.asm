goto main
wb 0
 
r ww 0 #output
a ww 3 #input
d ww 1 #numero que esta sendo multiplicado por ele mesmo
last_d ww 0 #ultimo numero que foi multiplicado

main setX d
     setY d
     goto multip

multip    multXY 
          movX r #guarda o valor da multiplicacao em r
          setY a 

          #verifica se achou o numero desejado
          setX r
          subX a
          jzX final #se são iguais, finaliza

          #verifica se é maior
          setX r
          isGreaterXY
          jzX inc #se é menor, continua
          #caso contrario, diminui D (para fazer o chão da raiz quadrada)
          setX d
          sub1X
          movX r
          halt

inc       setY d
          add1Y
          movY d
          setX d
          goto main

final     setX d
          movX r
          halt