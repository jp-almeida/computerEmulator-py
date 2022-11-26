goto main
wb 0

in_out ww 6
last ww 3 #ultimo numero primo encontrado
curr ww 5 #numero atual (que está sendo dividido)
div ww 3 #numero que está divindo
tres ww 3

            #verificar se é zero
main        setX in_out
            jzX end_init #zero
            
            #verificar se é um
            sub1X
            jzX end_init #um

            #verificar se é dois
            sub1X
            jzX end_init #dois

            #verificar se é tres
            sub1X
            jzX end_init #tres

            movX in_out
            setY tres
            setX curr
            goto loop
            

end_init halt

#vai para o proximo numero
prox_num    setX curr
            add1X
            add1X
            movX curr
            setY tres
            
            goto loop

#achou um primo
achou       setX curr
            movX last
            
            #verifica se achou todos os números
            setX in_out
            sub1X
            jzX end
            movX in_out
            
            goto prox_num

loop        divXY
            jzK prox_num
            setX curr

            #incrementa o denominador
            setY div
            add1Y 
            movY div

            #ve se chegou no maximo
            subXY
            jzX achou
            
            setX curr
            goto loop



end         setX last
            movX in_out
            halt