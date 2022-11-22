goto main
wb 0
 
r ww 0 #output
a ww 100 #input->numero_para_achar_a_raiz_quadrada
c ww 1 #contagem_multiplicacao
d ww 1 #numero_que_esta_sendo_multiplicado_por_ele_mesmo
g ww 0 #resultado_de_cada_multiplicacao

main add x, a
     mov x, r
     jz x, final #eh_zero
     sub1 x
     jz x, final #eh_um

     #começar_multiplicando_2_por_ele_mesmo
     set0 x
     add1 x
     add1 x
     mov x, d
     goto mult

#multiplica_um_numero_por_ele_mesmo
mult add x, d
     mov x, g
     
     #incrementa_o_num_de_parcelas
     set0 x
     add x, c
     add1 x
     mov x, c
     
     #verifica_se_o_num_de_parcelas_eh_o_esperado
     sub x, d
     jz x, comp #multiplicou_tudo_(verificar_se_achou_o_numero)
    
     #continua_a_multiplicacao
     set0 x
     add x, g
     goto mult

#ir_para_o_proximo_numero
prox add x, d
     add1 x
     mov x, d
     
     #zera_as_parcelas_e_o_resultado_da_multiplicacao
     set0 x
     mov x, c
     mov x, g
     
     goto mult

#verifica_se_achou_o_numero_esperado
comp add x, g
    sub x, a
    jz x, final
    set0 x
    goto prox #vai_para_o_prox_numero

final add x, d
    mov x, r
    halt