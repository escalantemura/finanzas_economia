# Valuación de empresas mediante método WACC
## Sistema de ecuaciones
### Ecuación principal

$$
WACC = \left(\frac{E}{V} \times K_e\right) + \left(\frac{D}{V} \times K_d\right) \times (1-T)
$$

### Ecuación con acciones preferentes

$$
WACC = \left(\frac{E}{V} \times K_e\right) + \left(\frac{P}{V} \times K_p\right) + \left(\frac{D}{V} \times K_d\right) \times (1-T)
$$


### K_e, tasa de rendimiento exigido por los accionistas

$$
K_e = R_f + \beta \times (R_m - R_f)
$$

Donde:

* $R_f$ es la tasa libre de riesgo, es decir, el rendimiento que se puede obtener invirtiendo en un activo libre de riesgo, como los bonos del gobierno.
* $\beta$ es el coeficiente beta, que mide la sensibilidad del rendimiento de una acción a los cambios en el mercado en general. Se puede calcular utilizando herramientas financieras como el modelo CAPM (Capital Asset Pricing Model).
* $R_m$ es el rendimiento promedio del mercado de valores en general, que se puede medir utilizando un índice de mercado amplio como el S&P 500.

### K_d, costo de la deuda

$$
K_d = \frac{I}{V_d}
$$

Donde:

* $I$ es el costo anual de la deuda, que incluye el interés pagado sobre los préstamos y cualquier otro costo relacionado con la emisión de deuda.
* $V_d$ es el valor total de la deuda de la empresa.

Cabe destacar que el costo de la deuda es el costo más bajo de las tres fuentes principales de financiamiento, ya que la deuda se considera menos riesgosa que las acciones y las acciones preferentes, debido a que los intereses sobre la deuda deben pagarse antes de que se distribuyan los dividendos a los accionistas.

Es importante destacar que la fórmula del costo del capital común se basa en la teoría financiera moderna y supone que los inversores son racionales y diversificados. Además, es importante tener en cuenta que el costo del capital común suele ser más alto que el costo de la deuda y el costo de la participación preferente, ya que las acciones comunes son más riesgosas y no tienen un pago de dividendos garantizado como las otras dos fuentes de financiación.

### K_p, costo de la participación preferente

$$
K_p = \frac{D_p}{P_p}
$$

Donde:

* $D_p$ es el dividendo anual pagado por la empresa a los accionistas preferentes y
* $P_p$ es el precio de la acción preferente.

Cabe destacar que, en general, el costo de la participación preferente suele ser mayor que el costo de la deuda pero menor que el costo del capital común. Esto se debe a que las acciones preferentes tienen preferencia sobre las acciones comunes en términos de pagos de dividendos, lo que las hace menos riesgosas que las acciones comunes, pero a la vez no tienen derecho a voto y, por tanto, no participan en la toma de decisiones empresariales.


## Python
### Parámetros obligatorios
```python
acciones_comun_precio: float
acciones_comun_cantidad: int

prima_mercado: float
tasa_impuestos: float
tasa_libre_riesgo: float
beta: float
```

### Parámetros opcionales
```python
acciones_preferente_precio: float
acciones_preferente_cantidad: int
acciones_dividendo: float

bonos_cantidad: List[int]
bonos_precio_nominal: List[float]
bonos_precio_mercado: List[float]
bonos_rentabilidad_vencimiento: List[float]
bonos_tir: float

bonos_total_nominal_override: List[float]
bonos_total_mercado_override: List[float]
total_mercado_deuda_override: float
```

### Override
Esta función permite sobreescribir y evitar ciertos cálculos si los valores finales ya se tienen. Se listan los overrides y los parámetros que sobreescribe.
```python
bonos_total_nominal_override: List[float]

bonos_cantidad
bonos_precio_nominal
```
```python
bonos_total_mercado_override: List[float]

bonos_cantidad
bonos_precio_mercado
```
```python
total_mercado_deuda_override: float

bonos_cantidad
bonos_precio_mercado
total_mercado_deuda()
```


La TIR de los bonos (o cualquier otro ratio usado para evaluar su rentabilidad), puede ser reemplaza con la lista de rentabilidad al vencimiento de los bonos.
```python
bonos_tir -> bonos_rentabilidad_vencimiento
```

### Casos
#### Sin Override y con acciones comunes
Caso clásico con todas los parámetros principales completos, suponiendo que la empresa solo ha emitido acciones comunes y una cantidad de bonos con cierto precio, y que ya se ha calculado la TIR.

```python
WACC(
    acciones_comun_precio=32,
    acciones_comun_cantidad=1.13,
    prima_mercado=0.125,
    tasa_impuestos=0.35,
    tasa_libre_riesgo=0.0625,
    beta=1.1,
    
    bonos_cantidad=[120, 100, 120],
    bonos_precio_mercado=[12.3, 11, 10.1],
    bonos_tir=0.0645
)
```


#### Override y con acciones comunes y preferentes
Tanto como si la empresa emite o no acciones preferentes, se supone que siempre emitirá acciones comunes. Las acciones preferentes necesitan de un valor para el dividendo. En este caso, se ha hecho un overrida sobre el total_mercado_deuda() y se ha calculado la TIR de los bonos usando un bono de modelo.

```python
WACC(
    acciones_comun_precio=45,
    acciones_comun_cantidad=43_030_000,
    prima_mercado=0.105,
    tasa_impuestos=0.3,
    tasa_libre_riesgo=0.0525,
    beta=0.84,
    
    acciones_preferente_precio=50,
    acciones_preferente_cantidad=2_028_000,
    acciones_dividendo=3,
    
    total_mercado_deuda_override=205_107_000,
    bonos_tir=Bono(
                tasa_cupon=0.08,
                valor_nominal=1_000,
                valor_mercado=1_000,
                periodos=7*2
                ).tir()
)
```


#### Override bonos nominal y mercado y rentabilidad al vencimiento
Cuando se tienen ambos valores totales, tanto de los bonos nominales como su valor a mercado. Si no se considera la TIR, se debe reemplazar con la rentabilidad de los bonos al vencimiento.

```python
WACC(
    acciones_comun_precio=21,
    acciones_comun_cantidad=45,
    prima_mercado=0.1375,
    tasa_impuestos=0.34,
    tasa_libre_riesgo=0.0522,
    beta=1.78,
    
    bonos_total_nominal_override=[250, 300, 350],
    bonos_total_mercado_override=[240, 320, 345],
    bonos_rentabilidad_vencimiento=[0.058, 0.072, 0.0845]
)
```

# Flujo de caja libre
## Sistema de ecuaciones
### Ecuación principal


## Python
### Parámetros obligatorios
La tasa de descuento puede ser el WACC también.

```python
tasa_crecimiento: float = 0
tasa_descuento: float = 0
```

### Parámetros opcionales
fcl_override sobrescribe los demás parámetros opcionales.

```python
utilidad_operativa: List[float] = 0
depreciacion_amortizacion: List[float] = 0
capex: List[float] = 0
cambio_capital_trabajo: List[float] = 0
impuesto_renta: List[float] = 0

fcl_override: List[float]
```

### Casos
#### Sin override

```python
FlujoCajaLibre(
    tasa_crecimiento=0.03,
    tasa_descuento=0.157,
    
    utilidad_operativa=       [-63_006, 209_647, 209_647, 209_647, 209_647, 209_647],
    depreciacion_amortizacion=[207_331, 237_331, 267_331, 297_331, 327_331, 357_331],
    capex=                    [1_673_995, 240_000, 240_000, 240_000, 240_000, 240_000],
    cambio_capital_trabajo=   [36_441, 141_413, 0, 0, 0, 0],
    impuesto_renta=           [0, 12_544, 12_544, 12_544, 12_544, 12_544]
)
```

#### Override

```python
FlujoCajaLibre(
    tasa_crecimiento=0.0,
    tasa_descuento=0.12,
    
    fcl_override=[10_685, 12_638, 12_910, 12_809, 14_183, 11_774, 11_301, 11_379, 11_517, 11_651]
)
```

#### Función para loopear tasas de descuento
Para generar diversos escenarios se pueden cambiar las tasas de descuento.

```python
tasas = [0.134, 0.145, 0.157, 0.168, 0.179]
for tasa in tasas:
    flujo.tasa_descuento = tasa
    print(f'Tasa de descuento: {flujo.tasa_descuento * 100:.2f}')
    print(f'VNA: {flujo.vna():,}')
    print(f'VNA con perpetuidad: {flujo.vna_perpetuidad():,}')
    print()
```


# Valuación acciones comunes
## Sistema de ecuaciones
### Ecuación principal
$$
\frac{Dividendo \cdot (1+G)^t}{R-G}
$$

Donde:
* $t$ es el periodo (*1 -> Año presente (por defecto), 2 -> 1er año, 3 -> 2do año*)
* $R$ es la tasa de descuento o el retorno requerido, retorno del accionista.
* $G$ es la tasa de crecimiento del dividendo.

Parámetros opcionales:
* El parámetro lista_tasa_crecimiento se utiliza para hacer los pronósticos.


## Python
### Parámetros obligatorios
La tasa de descuento puede ser el WACC también.

```python
dividendo_esperado: float
tasa_descuento: float
tasa_crecimiento: float
```

### Parámetros opcionales
Por defecto se muestre el resultado del periodo 1. La tasa_crecimiento_lista se debe usar cuando se quiere hacer un pronóstico de la acción.

```python
periodo: int = 1
tasa_crecimiento_lista: List[float]
```


### Casos
#### Acción común con crecimiento regular

```python
AccionComun(
    dividendo_esperado=3,
    tasa_descuento=0.08,
    tasa_crecimiento=0.04,
)
```

#### Acción común con pronóstico de tasas de crecimiento

```python
AccionComun(
    dividendo_esperado=6,
    tasa_descuento=0.1,
    tasa_crecimiento=0.06,
    tasa_crecimiento_lista=[0.02, 0.03, 0.04, 0.05]
)
```

#### Acción común con crecimiento iregular
Se usa el VNA para calcular el precio de la acción presente. Debido a la complejidad de los casos, es mejor diseñar cada procedimiento según el caso.

Supongamos que una empresa de dividendos irregulares anuncia que pagará dividendos de USD2 por acción los dos primeros años, USD3 los dos años siguientes y de ahí los dividendos crecerán 4%; y que el retorno requerido es de r=8%

```python
import numpy_financial as npf

tasa_descuento = 0.08
accion = AccionComun(
    dividendo_esperado=3,
    tasa_descuento=tasa_descuento,
    tasa_crecimiento=0.04,
).valor()

# Flujo
flujo = [2, 2, 3, 3 + accion]

# Consola
print(f'Flujo: {flujo}')
print(f'Valor de la acción: {accion:.2f}')
print(f'Valor presente del flujo: {npf.npv(tasa_descuento, [0] + flujo):.2f}')
AccionComun.grafico_flujo(flujo=flujo)
```

# Valuación de empresas mediante método WACC
## Sistema de ecuaciones
### Ecuación principal

$$
ROI = \frac{BAIDT}{Valor\ contable\ del\ capital\ invertido}
$$

$$
BAIDT = \frac{Inversión\ Neta}{TIN}
$$

$$
Inversión\ Neta = Inversión\ Bruta - Amortizaciones
$$

$$
Tasa\ Inversión\ Neta = \frac{Inversión\ Bruta - Amortización}{Flujo\ de\ Caja}
$$

## Python
### Parámetros obligatorios

```python
inversion_bruta: float
amortizacion: float
flujo_caja: float
vcpi: float
```

### Parámetros opcionales

```python

```


### Casos
#### Sin override

```python
Roi(
    inversion_bruta=300_000,
    amortizacion=200_000,
    flujo_caja=100_000,
    vcpi=16_666_666
)
```