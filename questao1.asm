goto main
wb 0

in_out ww 200000 #input e output
cem ww 100
dois ww 2
oito ww 8
vintcinc ww 25

#verificar se é divisivel por 400 (16 * 25)
#por 16
main            setX in_out
                andX oito #resto da divisão por 16
                jzK biss
                goto div400_cont
#por 25
div400_cont     div16X #divisao por 16
                #TODO: jzX nao_biss #menor que 16
                setY vintcinc
                divXY
                jzK div4
                goto nao_biss


#verificar se é divisivel por 4
div4            setX in_out
                andX dois
                jzK biss
                goto nao_biss

#verificar se é divisivel por 100 (4 * 25) -> basta ver se é por 25
div100          setX in_out
                div4X
                setY vintcinc
                divXY
                jzK nao_biss
                goto biss

biss            set1X
                goto fim

nao_biss        set0X
                goto fim

fim             movX in_out
                halt