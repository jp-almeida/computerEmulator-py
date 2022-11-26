goto main
wb 0                  
                           
in_out ww 3
c ww 0
dois ww 1

main setX in_out
     jzX zero #se x for 0
     setY in_out
     sub1Y
    jzY end
     andY dois
    jzK loop_par
    goto loop_imp

loop_par movY c
     multEvenXY
     setY c
    sub1Y
    jzY end
     goto loop_imp

loop_imp movY c
     multXY
     setY c
sub1Y
    jzY end
     goto loop_par

zero set1X
     goto end

end  movX in_out
     halt