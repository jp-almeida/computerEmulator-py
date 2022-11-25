goto main
wb 0
 
in_out ww 100 #input e output
out ww 0 #guardar input
d ww 1 #numero que esta sendo multiplicado por ele mesmo

main      setX d
          setY d
          goto multip

multip    multXY 
          movX out #guarda o valor da multiplicacao em in_out
          setY in_out 

          #verifica se achou o numero desejado
          setX in_out
          subX out
          jzX final #se são iguais, finaliza

          #verifica se é maior
          setX out
          isGreaterXY
          jzX inc #se é menor, continua
          #caso contrario, diminui D (para fazer o chão da raiz quadrada)
          setX d
          sub1X
          movX in_out
          halt

inc       setY d
          add1Y
          movY d
          setX d
          goto main

final     setX d
          movX in_out
          halt