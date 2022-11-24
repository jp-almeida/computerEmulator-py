goto main
wb 0

r ww 0 #output
a ww 400 #input
v ww 0
qtr ww 4
cem www 100
qtrcent ww 400
true ww 1

main  setX a 
      #divisivel por 4
      setY qtr
      divXY
      movX v
      subX v
      jz x, divisivel100
      goto fim

divisivel100 setX a 
      setY cem
      divXY
      movX v
      subX v
      jz x, divisivel400
      goto fim

divisivel400 setX a 
      setY qtrcent
      divXY
      movX v
      subX v
      jz x, bissexto
      goto fim

bissexto setX true
      goto fim

fim halt