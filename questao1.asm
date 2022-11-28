goto main
wb 0

in_out ww 401 #input e output
cem ww 100
dois ww 2
oito ww 8
vintcinc ww 25

#verificar se é divisivel por 400 (16 * 25)
#por 16
main            setX in_out
                #divisao por 16
                div16X
                jzK div400_cont #divisivel
                goto div4 #nao divisivel
#por 25
div400_cont     setY vintcinc
                divXY
                jzK biss
                goto div4


#verificar se é divisivel por 4
div4            setX in_out
                div4X
                jzK div100
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