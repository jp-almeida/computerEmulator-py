1. Escreva um programa que pegue um valor "n" guardado na word 1 da memória e,
se n corresponder a um ano bissexto, guarde o valor 1 de volta na word 1 e, caso
contrário, guarde 0.
2. Escreva um programa que pegue um valor "n" guardado na word 1 da memória,
calcule o fatorial de "n" e guarde o resultado de volta na word 1.
3. Escreva um programa que pegue um valor "n" guardado na word 1 da memória,
calcule o "n-ésimo" número primo e guarde-o de volta na word 1.
4. Escreva um programa que pegue um valor "n" guardado na word 1 da memória,
calcule ⌊√n⌋ e guarde o resultado de volta na word 1.



**Ano bissexto**
1. Se o ano for uniformemente divisível por 4, vá para a etapa 2. Caso contrário, vá para a etapa 5.
2. Se o ano for uniformemente divisível por 100, vá para a etapa 3. Caso contrário, vá para a etapa 4.
3. Se o ano for uniformemente divisível por 400, vá para a etapa 4. Caso contrário, vá para a etapa 5.
4. O ano é bissexto (tem 366 dias).
5. O ano não é um ano bissexto (tem 365 dias).

Verificar se é divisivel
K <- X/Y
H <- X*Y
K-H = 0 -> divisível