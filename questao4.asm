goto main
wb 0
 
in_out ww 16 #input e output
out ww 0 #guardar input
d ww 1 #numero que esta sendo multiplicado por ele mesmo

main    setX in_out
        andX d #resto da divisao por 2
        jzX eh_par
        setX d
        setY d
        goto multip

eh_par  setX d
        add1X
        movX d
        setY d
        goto multip

multip    multXY 
          movX out #guarda o valor da multiplicacao em in_out
          
          #verifica se achou o numero desejado
          setX in_out
          subX out
          jzX final #se são iguais, finaliza

          #verifica se é maior
          setY in_out 
          setX out
          isGreaterXY
          jzX inc #se é menor, continua
          
          #caso contrario, diminui D (para o chão da raiz)
          setX d
          sub1X
          movX in_out
          halt

inc       setY d
          add1Y
          add1Y
          movY d
          setX d
          goto multip

final     setX d
          movX in_out
          halt