goto main
wb 0                  
                           
in_out ww 6
c ww 0

main setX in_out
     jzX zero #se x for 0
     setY in_out
     goto loop

loop sub1Y
     jzY end
     movY c
     multXY
     setY c
     goto loop

zero set1X
     goto end

end  movX in_out
     halt