goto main
wb 0

in_out ww 11
last ww 3 #ultimo numero primo encontrado
curr ww 5 #numero atual (que está sendo dividido)
div ww 3 #numero que está divindo
tres ww 3

            #verificar se é zero
main        setX in_out
            jzX end_excep #zero
            
            #verificar se é um
            sub1X
            jzX end_excep #um

            #verificar se é dois
            sub1X
            jzX end_excep #dois

            #verificar se é tres
            sub1X
            jzX end_excep #tres

            movX in_out
            setY tres
            setX curr
            goto loop
            
#nos casos anormais (0,1,2 e 3), a saída será igual à entrada, então não precisa modificar nada
end_excep halt

#vai para o proximo numero (que vai ser verificado se é primo ou não)
#é incrementado de 2 em 2 porque nenhum par é primo além do 2
prox_num    setX curr
            add1X
            add1X
            movX curr
            setY tres
            
            goto loop

#achou um primo
achou       setX curr
            movX last #atualiza o último primo achado para o número atual
            
            #verifica se achou todos os números (diminui a contagem em 1)
            setX in_out
            sub1X
            jzX end
            movX in_out #atualiza a variavel da contagem
            
            goto prox_num

#loop principal: aumenta o denominador até igualar ao denominador ou o resto ser 0
#o denominador também será incrementado de dois em dois, uma vez que um numero ímpar não
#é divisível por um par
loop        divXY
            jzK prox_num #se o resto for 0, não é numero primo
            setX curr

            #incrementa o denominador
            setY div
            add1Y 

            #ve se chegou no maximo (numerador = denominador)
            subXY
            jzX achou

            #incrementa o denominador
            setY div
            add1Y 

            #ve se chegou no maximo (numerador = denominador)
            subXY
            jzX achou

            movY div
            setX curr
            goto loop

end         setX last
            movX in_out
            halt