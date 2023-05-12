from dataclasses import dataclass
from typing import List
import numpy_financial as npf
import matplotlib.pyplot as plt


@dataclass
class WACC:
    """
        Se evalúan dos tipos de WACC
        Con acciones comunes:
            WACC = ((E/V) * K_e) + ((D/V) * K_d) * (1-T)
        Con acciones comunes y preferentes:
            WACC = ((E/V) * K_e) + ((P/V) * K_p) + ((D/V) * K_d) * (1-T)
    """
    acciones_comun_precio: int | float
    acciones_comun_cantidad: int
    prima_mercado: float
    tasa_impuestos: float
    tasa_libre_riesgo: float
    beta: float
    acciones_preferente_precio: int | float = None
    acciones_preferente_cantidad: int = None
    acciones_dividendo: int | float | None = None
    bonos_cantidad: List[int] | None = None
    bonos_precio_nominal: List[int | float] | None = None
    bonos_precio_mercado: List[int | float] | None = None
    bonos_rentabilidad_vencimiento: List[float] | None = None
    bonos_tir: float | None = None
    bonos_total_nominal_override: List[int | float] | None = None
    bonos_total_mercado_override: List[int | float] | None = None
    total_mercado_deuda_override: int | float | None = None

    def total_bonos_nominal(self) -> int | float | List[int | float]:
        if self.bonos_total_nominal_override is None:
            valores = []
            for cantidad, precio in zip(self.bonos_cantidad, self.bonos_precio_nominal):
                valores.append(cantidad * precio)
            return sum(valores)
        else:
            return sum(self.bonos_total_nominal_override)

    def total_bonos_mercado(self) -> int | float | List[int | float]:
        if self.bonos_total_mercado_override is None:
            valores = []
            for cantidad, precio in zip(self.bonos_cantidad, self.bonos_precio_mercado):
                valores.append(cantidad * precio)
            return sum(valores)
        else:
            return sum(self.bonos_total_mercado_override)

    def total_mercado_accion_comun(self) -> float:
        """ Valor E. Valor de mercado total de las acciones comunes """
        return self.acciones_comun_precio * self.acciones_comun_cantidad

    def total_mercado_accion_preferente(self) -> float:
        """ Valor P. Valor de mercado total de las acciones preferentes"""
        if self.acciones_preferente_precio is not None:
            return self.acciones_preferente_precio * self.acciones_preferente_cantidad
        else:
            return 0

    def total_mercado_deuda(self) -> float:
        """
            Valor D
            Valor de la deuda total
        """
        if self.total_mercado_deuda_override is not None:
            return self.total_mercado_deuda_override
        else:
            if self.bonos_total_mercado_override is not None:
                return sum(self.bonos_total_mercado_override)
            else:
                return self.total_bonos_mercado()

    def total_mercado_empresa(self) -> float:
        """
            Valor V
            Valor de la empresa en el mercado
        """
        return self.total_mercado_accion_comun() + self.total_mercado_accion_preferente() + self.total_mercado_deuda()

    def costo_patrimonio(self) -> float:
        """
            Valor K_e
            Tasa de rendimiento exigido por los accionistas
        """
        return self.tasa_libre_riesgo + (self.beta * self.prima_mercado)

    def costo_deuda(self) -> float:
        """
            Valor K_d
            Costo de la deuda
            Se puede calcular mediante dos formas: 1) La cartera de bonos y su rentabilidad al vencimiento
            o 2) el TIR de un bono de referencia
        """
        if self.bonos_rentabilidad_vencimiento is not None:
            valores = []
            for mercado, rentabilidad in zip(self.bonos_total_mercado_override, self.bonos_rentabilidad_vencimiento):
                valores.append(mercado * rentabilidad / self.total_mercado_deuda())
            return sum(valores)
        else:
            return self.bonos_tir

    def costo_acciones_preferentes(self):
        """
            Valor K_p
            Tasa de acciones preferentes
        """
        if self.acciones_preferente_precio is not None:
            return self.acciones_dividendo / self.acciones_preferente_precio
        else:
            return 0

    def escudo_fiscal(self) -> float:
        return 1 - self.tasa_impuestos

    def resultado(self) -> float:
        return ((self.total_mercado_accion_comun() / self.total_mercado_empresa()) * self.costo_patrimonio()) \
            + ((self.total_mercado_accion_preferente() / self.total_mercado_empresa()) * self.costo_acciones_preferentes()) \
            + ((self.total_mercado_deuda() / self.total_mercado_empresa()) * self.costo_deuda()) \
            * self.escudo_fiscal()

    def estructura_financiera(self):
        accion_comun = self.total_mercado_accion_comun()
        accion_preferente = self.total_mercado_accion_preferente()
        deuda = self.total_mercado_deuda()
        empresa = self.total_mercado_empresa()

        print(f'{"Estructura financiera":-^70}')
        print(f'Valor de mercado de las acciones comunes (E) ({accion_comun / empresa * 100:.2f}%): {accion_comun:,}')
        if self.total_mercado_accion_preferente() != 0:
            print(f'Valor de mercado de las acciones preferentes (P) ({accion_preferente / empresa * 100:.2f}%): {accion_preferente:,}')
        print(f'Valor de la deuda total (D) ({deuda / empresa * 100:.2f}%): {deuda:,}')
        print(f'Valor de mercado de la empresa (V): {empresa:,}')

    def presentacion(self):
        print(f'{"Resultados":-^70}')
        print(f'Costo del patrimonio (K_e): {self.costo_patrimonio() * 100:.2f}%')
        print(f'Costo de la deuda (K_d): {self.costo_deuda() * 100:.2f}%')
        if self.total_mercado_accion_preferente() != 0:
            print(f'Costo de las acciones preferentes (K_p): {self.costo_acciones_preferentes() * 100:.2f}%')
        print(f'Escudo fiscal: {self.escudo_fiscal() * 100:.2f}%')
        print(f'Valor WACC: {self.resultado() * 100:.2f}%')


@dataclass
class Bono:
    """
        Calcula el valor de un Bono de acuerdo a lo que se necesite
    """
    tasa_cupon: float
    valor_nominal: int | float
    periodos: int
    valor_mercado: int | float | None = None

    def tir(self) -> float:
        """
            Devuelve la Tasa Interna de Retorno de un Bono
            El monto del año 0, o de adquisición, es igual al valor por el cual se ha adquirido el bono.
            La secuencia es primero el valor negativo del mercado, el flujo de intereses
            y en el último periodo el valor nominal más la tasa cupón
        """
        flujo = [-self.valor_mercado]
        for _ in range(self.periodos - 1):
            flujo.append(self.valor_nominal * self.tasa_cupon)
        flujo.append(self.valor_nominal * (1 + self.tasa_cupon))
        return npf.irr(flujo)


@dataclass
class AccionComun:
    """
        Valúa una accción común
    """
    dividendo_esperado: float
    tasa_descuento: float
    tasa_crecimiento: float
    periodo: int = 1
    tasa_crecimiento_lista: List[float] | None = None

    def valor(self) -> float:
        """
            Fórmula principal para valorizar la acción
        """
        formula = self.dividendo_esperado * ((1 + self.tasa_crecimiento) ** self.periodo) / (self.tasa_descuento - self.tasa_crecimiento)
        return formula

    def ganancia_capital(self) -> float:
        valor_periodo_0 = self.valor()
        valor_periodo_1 = self.valor() * (1 + self.tasa_crecimiento)
        return valor_periodo_1 - valor_periodo_0

    def pronostico(self) -> List[float]:
        """
            Genera una lista pronóstico del valor de la acción
        """
        lista = []
        for tasa in self.tasa_crecimiento_lista:
            lista.append(self.dividendo_esperado * ((1 + self.tasa_crecimiento) ** self.periodo) / (self.tasa_descuento - tasa))
        return lista

    def grafico(self):
        x = self.pronostico()
        y = self.tasa_crecimiento_lista

        plt.plot(x, y, label='Valor')

        # personalización del gráfico
        plt.xlabel('Precio de la acción')
        plt.ylabel('Tasa de crecimientio')
        plt.title('Pronóstico de la acción')
        plt.legend()
        # mostrar el gráfico
        plt.show()

    @staticmethod
    def grafico_flujo(flujo: List[float]):
        """
            Esta función permite tomar un flujo y plotearlo
        """
        # datos del flujo de ingresos
        ingresos = flujo
        # índices de tiempo para cada punto de datos del flujo de ingresos
        tiempo = list(range(1, len(flujo)+1))

        # crear la gráfica de líneas
        plt.plot(tiempo, ingresos, linestyle='--', marker='o', color='blue')
        # etiquetar los ejes
        plt.xlabel('Año')
        plt.ylabel('Dividendo')
        plt.title('Flujo de los dividendos')

        # agregar etiquetas de valor a la gráfica
        for i, ingreso in enumerate(ingresos):
            plt.text(tiempo[i], ingreso, str(ingreso), ha='center', va='bottom', fontsize=16)
        # personalizar la apariencia de la gráfica
        plt.xticks(tiempo)
        plt.yticks(ingresos)
        plt.grid(True)
        # mostrar la gráfica
        plt.show()

    def presentacion(self):
        print(f'Valor de la acción (año {self.periodo-1}): {self.valor():.2f}')
        print(f'Pronóstico según las tasas de crecimiento: {self.pronostico()}')
        print(f'Ganancia de capital: {self.ganancia_capital():.2f}')
        self.grafico()


@dataclass
class FlujoCajaLibre:
    utilidad_operativa: List[float] = 0
    depreciacion_amortizacion: List[float] = 0
    capex: List[float] = 0
    cambio_capital_trabajo: List[float] = 0
    impuesto_renta: List[float] = 0
    tasa_crecimiento: float = 0
    tasa_descuento: float = 0
    fcl_override: List[float] | None = None

    def ebitda(self) -> List[float]:
        valores = []
        for utiope, depamor in zip(self.utilidad_operativa, self.depreciacion_amortizacion):
            valores.append(utiope + depamor)
        return valores

    def fcl(self) -> List[float]:
        if self.fcl_override is None:
            valores = []
            for ebitda, capex, cct, renta in zip(
                self.ebitda(), self.capex, self.cambio_capital_trabajo, self.impuesto_renta):
                valores.append(ebitda - capex - cct - renta)
            return self._fcl_correccion_npv(valores)
        else:
            return self._fcl_correccion_npv(self.fcl_override)

    def _fcl_correccion_npv(self, lista_fcl: List[float]) -> List[float]:
        """
            Esta función corrige la fórmula de npv de Numpi
            Si el primer valor es negativo (una inversión), se debe reemplazar con un cero
            Sino insertar un cero al comienzo
        """
        lista_fcl = lista_fcl.copy()
        if lista_fcl[0] < 0:
            lista_fcl[0] = 0
        else:
            lista_fcl.insert(0, 0)
        return lista_fcl

    def valor_residual(self) -> float:
        """
            Devuelve el valor a perpetuidad o valor continuo o valor residual del flc
            Las tasa de descuento puede ser el WACC también
        """
        return self.fcl()[-1] * (1 + self.tasa_crecimiento) / (self.tasa_descuento - self.tasa_crecimiento)

    def vna(self) -> float:
        """
            VNA de una empresa solo considerando los periodos del FCL
        """
        return npf.npv(rate=self.tasa_descuento, values=self.fcl())

    def vna_valor_residual(self) -> float:
        """
            VNA de una empresa considerando su valor residual
        """
        add_valor_residual = self.fcl().copy()
        add_valor_residual.append(self.valor_residual())
        return npf.npv(rate=self.tasa_descuento, values=add_valor_residual)

    def presentacion(self):
        vna = self.vna()
        vna_valor_residual = self.vna_valor_residual()
        vna_perpetuidad = vna_valor_residual - vna
        fcl = self.fcl()

        print(f'{"Resultados":-^70}')
        print(f'Flujo de caja libre: {fcl}')
        print(f'Valor residual (perpetuidad): {self.valor_residual():,}')
        print(f'Valor Presente del FCL: {vna:,}')
        print(f'Valor Presente del FCL (con el valor residual): {vna_valor_residual:,}')
        print(f'{"VNA del FCL":-^70}')
        print(f'Periodo Pronosticado ({len(fcl)-1} años) ({vna/vna_valor_residual * 100:.2f}%): {vna:,}')
        print(f'Perpetuidad (>{len(fcl)-1} años) ({vna_perpetuidad/vna_valor_residual * 100:.2f}%): {vna_perpetuidad:,}')
        print(f'Total: {vna_valor_residual:,}')
