goto main
wb 0

in_out ww 2022 #input e output
cem ww 100
qrtcents ww 400
dois ww 2

#verificar se é divisivel por 400
main            setX in_out
                setY qrtcents
                divXY
                jzK biss
                goto div4

#verificar se é divisivel por 4
div4            setX in_out
                andX dois
                jzK biss
                goto nao_biss

#verificar se é divisivel por 100
div100          setX in_out
                setY cem
                divXY
                jzK nao_biss
                goto biss

biss            set1X
                goto fim

nao_biss        set0X
                goto fim

fim             movX in_out
                halt