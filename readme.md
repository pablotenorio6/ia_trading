## Description
Aplicacion de trading basada en un modelo de inteligencia artificial que analiza tendencias de
activos financieros intradiarios a partir de una serie de indicadores tecnicos, ejecutando 
automaticamente ordenes de compra con un Proffit Return y Stop Loss fijos y configurables.
### Philosophy

### Dependencies

### Market API
En principio Interactive Brothers 

Ejemplo: 

Si ejecutas una orden y la configuras con stop loss y take profit:

Orden de compra: 1 dolar mínimo (si estás en el plan fijo). \
Ejecución del stop loss o take profit (independientemente de cuál se active): 1 dolar.

Total: 2 dolares en comisiones minimo.

En base a dichas comisiones, podemos calcular el volúmen mínimo necesario por orden para que 
el retorno sea positivo de esta manera:
$$ Retorno = (V_o*OC*TP) - (V_o*OI*SL) - C$$
Siendo:

$V_o$ = Volumen unitario.

$OC$ = Porcentaje de ordenes correctas.

$OI$ = Porcentaje de ordenes incorrectas.

$TP$ = Take Proffit.

$SL$ = Stop Loss.

$C$ = Comisión total por orden.

De esta manera, si tenemos fijos los valores de Proffit y Stop Loss podemos
obtener el volumen mínimo necesario por orden para obtener beneficio, en a base 
nuestra estrategia.

Ejemplo:

Supongamos que tenemos fijos los valores de Take-Proffit a 1% y Stop-Loss a -0.4%.
Además, nuestra estrategia acierta un 75% de las veces que se ejecuta y tiene 2 dolares
de comisiones por orden.
$$ (V_o*OC*TP) = (V_o*OI*SL) + C$$
$$ V_o = \frac{C}{OC*TP-OI*SL}$$
$$ V_o = \frac{2}{0.75*0.01-0.25*0.004}$$
$$ V_o = 307,69$$ 


### Market analysis
La idea original es evaluar un activo con una volatilidad estable que permita obtener tendencias intradía del mercado
a partir de indicadores técnicos. Se han obtenido los últimos 4 años de datos (2020-2024) Coca-Cola (KO), en intervalos 
cinco minutales,  para las pruebas de entrenamiento y testeo. Para cada intervalo obtenemos el precio de cierre de la vela
cinco-minutal y su volumén.
#### 2020-2024 Coca-Cola Analysis
Analizemos en primer lugar la volatilidad de Coca-Cola para nuestro sample de datos filtrando el intervalo temporal
de cada día para las horas de mercado normal (10:00-16:00). La volatilidad producida en el pre y post-market no nos 
interesa, ya que tampoco vamos a poder operar en este espacio.


La volatilidad media diaría del activo para (2020-Actual), entendida como la diferencia del precio maximo y minimo del cierre de velas cinco minutales entre el precio medio diario, es de 0.97%. La desviación estándar es de 0.5%.

Es decir, un 66% de los días la volatilidad estará en el rango (0.47 %-1.47 %) durante el mercado nominal.

Suponiendo que tenemos fijo un take-proffit al 1%, mas de la mitad de los dias deberia saltar al menos una orden 
de compra.



### Deep Learning strategy 


### Data preparation


### TO-DO
Comparar los resultados de la ia con el dataframe real.

Evaluar como influye el intervalo temporal que ponemos como limite para encontrar el take proffit
Tener en cuenta que margenes necesitamos para no saturarnos de ordenes sin acabar (no tener fondos)
Esto dependera principalmente de los margenes de stop loss y proffit que tengamos, cuanto mas altos 
mas varianza habrá en los intervalos

Intervalos estandar cinco minutales por día: 80

Para un periodo de evaluación de la orden de 100 intervalo, proffit de 2% y un StopLoss del 0.4%, se tarda de media 32,64 intervalos en
canjear el proffit en ordenes acertadas y 20 intervalos en canjear el stop loss en ordenes erroneas.
Además, un 4% de las ordenes se excedían de los 100 intervalos de evaluación sin canjear stop loss o proffit.

Si subimos el intervalo de evaluación a 3 días (240 intervalos),  proffit de 2% y un StopLoss del 0.4%, se tarda de media 41.02 intervalos en
canjear el proffit en ordenes acertadas y 19.12 intervalos en canjear el stop loss en ordenes erroneas.
Además, un 0.064% de las ordenes se excedían de los 240 intervalos de evaluación sin canjear stop loss o proffit.

