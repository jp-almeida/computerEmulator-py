goto main
wb 0

in_out ww 2022 #input e output
qtr ww 4
cem ww 100
qrtcents ww 400

#verificar se é divisivel por 400
main    setX in_out
        setY qrtcents
        divXY
        jzK biss
        goto div4

#verificar se é divisivel por 4
div4    setX in_out
        setY qtr
        divXY
        jzK biss
        goto nao_biss

#verificar se é divisivel por 100
div100  setX in_out
        setY qtr
        divXY
        jzK nao_biss
        goto biss

biss        set1X
            goto fim

nao_biss    set0X
            goto fim

fim               movX in_out
                  halt