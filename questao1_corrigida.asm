goto main
wb 0

in_out ww 401 #input e output
cem ww 100
qrtcents ww 400

#verificar se é divisivel por 400
main            setX in_out
                setY qrtcents
                divXY
                jzK biss #resto 0 : divisivel
                goto div4

#verificar se é divisivel por 4
div4            setX in_out
                div4X
                jzK biss
                goto nao_biss

#verificar se não é divisivel por 100
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