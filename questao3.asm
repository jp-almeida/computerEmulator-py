goto main
wb 0

in_out ww 50
last ww 3 #ultimo numero primo encontrado
curr ww 5 #numero atual (que está sendo dividido)
div ww 3 #numero que está divindo
tres ww 3
dois ww 2

            
main        setX in_out
            sub1X #verificar se é dois
            jzX primeiro #dois

            #verificar se é tres
            sub1X
            jzX end #tres

            movX in_out
            setY tres
            setX curr
            goto loop

primeiro setX dois
        halt            

#vai para o proximo numero (que vai ser verificado se é primo ou não)
#é incrementado de 2 em 2 porque nenhum par é primo além do 2
prox_num    setX curr
            add2X
            movX curr
            setY tres
            
            goto loop

#achou um primo
achou       movX last #atualiza o último primo achado para o número atual
            
            #verifica se achou todos os números (diminui a contagem em 1)
            setX in_out
            sub1X
            jzX end
            movX in_out #atualiza a variavel da contagem
            
            goto prox_num

#loop principal: aumenta o denominador até igualar ao denominador ou até o resto ser 0
loop        divXY
            jzK prox_num #se o resto for 0, não é numero primo
            setX curr

            #incrementa o denominador
            add2Y
            movY div

            #ve se chegou no maximo (numerador = denominador)
            isEqualXY
            jzK achou
            
            goto loop

end         setX last
            movX in_out
            halt