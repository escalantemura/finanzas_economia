import json
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
import pandas as pd
from pydantic import BaseModel, validator
from tkinter.filedialog import askopenfilename


class Json(BaseModel):
    periodo: List[int]
    # Balance general
    # Activo
    cuentas_por_cobrar_comerciales_y_otras: List[float]
    efectivo_y_equivalentes: List[float]
    inventarios: List[float]
    propiedades_planta_equipo: List[float]
    activo_corriente: List[float]
    activo_no_corriente: List[float]
    activo_total: List[float]
    # Pasivo
    otras_provisiones: List[float]
    pasivo_corriente: List[float]
    pasivo_no_corriente: List[float]
    pasivo_total: List[float]
    # Patrimonio
    patrimonio: List[float]
    # Estado de resultados
    ventas: List[float]
    costo_de_ventas: List[float]
    gastos_financieros: List[float]
    utilidad_operativa: List[float]
    utilidad_antes_de_impuestos: List[float]
    utilidad_neta: List[float]

    @validator('periodo', each_item=True)
    def format_timestamp(cls, periodo):
        """
            Convierte para 'periodo' el Timestamp Epoch
            en milisegundos -> DD-MM-YYYY
            Excel transforma automáticamente una fecha hacia Epoch,
            por lo que hay convertirlas de nuevo
        """
        return datetime.fromtimestamp(periodo / 1000).strftime("%d-%m-%Y")


@dataclass
class Analisis(object):
    """
        Parent Class para las demás clases de Analisis.
        Hereda el Balance general y el Estados de Resultados
    """
    js: Json


@dataclass
class AnalisisLiquidez(Analisis):
    """
        Child Class de Analisis.
        Para analizar la liquidez
    """

    def dias_cobro(self):
        return [
            (cuentas_por_cobrar * 365)
            / ventas
            for cuentas_por_cobrar, ventas in
            zip(
                self.js.cuentas_por_cobrar_comerciales_y_otras,
                self.js.ventas
                )
        ]

    def dias_inventario(self):
        return [
            abs((inventarios * 365)
                / costo_de_ventas)
            for inventarios, costo_de_ventas in
            zip(
                self.js.inventarios,
                self.js.costo_de_ventas
                )
        ]

    def razon_acida(self):
        return [
            (activo_corriente - inventarios) / pasivo_corriente
            for activo_corriente, inventarios, pasivo_corriente in
            zip(
                self.js.activo_corriente,
                self.js.inventarios,
                self.js.pasivo_corriente
                )
        ]

    def razon_super_acida(self):
        return [
            (activo_corriente -
             inventarios -
             cuentas_por_cobrar)
            / pasivo_corriente
            for activo_corriente,
            inventarios,
            cuentas_por_cobrar,
            pasivo_corriente in
            zip(
                self.js.activo_corriente,
                self.js.inventarios,
                self.js.cuentas_por_cobrar_comerciales_y_otras,
                self.js.pasivo_corriente
                )
        ]

    def razon_corriente(self):
        return [
            activo_corriente / pasivo_corriente
            for activo_corriente, pasivo_corriente in
            zip(self.js.activo_corriente, self.js.pasivo_corriente)
        ]

    def razon_de_conversion(self):
        return [
            dias_cobro / dias_inventario
            for dias_cobro, dias_inventario in
            zip(self.dias_cobro(), self.dias_inventario())
        ]


@dataclass
class AnalisisSolvenciaRiesgo(Analisis):
    """
        Child Class de Analisis.
        Para analizar la solvencia y el riesgo
    """

    def pasivo_no_corriente_sobre_activo(self):
        return [
            pasivo_no_corriente / activo_total
            for pasivo_no_corriente, activo_total in
            zip(self.js.pasivo_no_corriente, self.js.activo_total)
        ]

    def pasivo_no_corriente_sobre_patrimonio(self):
        return [
            pasivo_no_corriente / patrimonio
            for pasivo_no_corriente, patrimonio in
            zip(self.js.pasivo_no_corriente, self.js.patrimonio)
        ]

    def pasivo_sobre_activos(self):
        return [
            pasivo_total / activo_total
            for pasivo_total, activo_total in
            zip(self.js.pasivo_total, self.js.activo_total)
        ]

    def patrimonio_sobre_activos(self):
        return [
            patrimonio / activo_total
            for patrimonio, activo_total in
            zip(self.js.patrimonio, self.js.activo_total)
        ]

    def periodo_de_intereses_ganados(self):
        return [
            utilidad_operativa / gastos_financieros
            for utilidad_operativa, gastos_financieros in
            zip(self.js.utilidad_operativa, self.js.gastos_financieros)
        ]

    def razon_de_flujo_de_efectivo(self):
        return [
            (utilidad_neta - otras_provisiones) / pasivo_corriente
            for utilidad_neta, otras_provisiones, pasivo_corriente in
            zip(
                self.js.utilidad_neta,
                self.js.otras_provisiones,
                self.js.pasivo_corriente
                )
        ]


@dataclass
class RendimientoOperativo(Analisis):
    """
        Child Class de Analisis.
        Para analizar el rendimiento operativo
    """

    def margen_antes_de_impuesto(self):
        return [
            utilidad_antes_de_impuestos / ventas
            for utilidad_antes_de_impuestos, ventas in
            zip(self.js.utilidad_antes_de_impuestos, self.js.ventas)
        ]

    def margen_bruto(self):
        return [
            (ventas - costo_de_ventas) / ventas
            for ventas, costo_de_ventas in
            zip(self.js.ventas, self.js.costo_de_ventas)
        ]

    def margen_de_utilidad_neta(self):
        return [
            utilidad_neta / ventas
            for utilidad_neta, ventas in
            zip(self.js.utilidad_neta, self.js.ventas)
        ]

    def margen_operativo(self):
        return [
            utilidad_operativa / ventas
            for utilidad_operativa, ventas in
            zip(self.js.utilidad_operativa, self.js.ventas)
        ]


@dataclass
class AnalisisDupont(Analisis):
    """
        Child Class de Analisis.
        Para analizar el sistema Dupont
    """

    def apalancamiento_financiero(self):
        return [
            (utilidad_antes_de_impuestos / utilidad_operativa) *
            multiplicador_del_capital
            for utilidad_antes_de_impuestos,
            utilidad_operativa,
            multiplicador_del_capital in
            zip(
                self.js.utilidad_antes_de_impuestos,
                self.js.utilidad_operativa,
                self.multiplicador_del_capital()
                )
        ]

    def efecto_fiscal(self):
        return [
            utilidad_neta / utilidad_antes_de_impuestos
            for utilidad_neta, utilidad_antes_de_impuestos in
            zip(self.js.utilidad_neta, self.js.utilidad_antes_de_impuestos)
        ]

    def margen_neto(self):
        return [
            utilidad_neta / ventas
            for utilidad_neta, ventas in
            zip(self.js.utilidad_neta, self.js.ventas)
        ]

    def margen_operativo(self):
        return [
            utilidad_operativa / ventas
            for utilidad_operativa, ventas in
            zip(self.js.utilidad_operativa, self.js.ventas)
        ]

    def multiplicador_del_capital(self):
        return [
            activo_total / patrimonio
            for activo_total, patrimonio in
            zip(self.js.activo_total, self.js.patrimonio)
        ]

    def rotacion_de_activos(self):
        return [
            ventas / activo_total
            for ventas, activo_total in
            zip(self.js.ventas, self.js.activo_total)
        ]

    def roe(self):
        return [
            margen_neto * rotacion_de_activos * multiplicador_del_capital
            for margen_neto, rotacion_de_activos, multiplicador_del_capital in
            zip(
                self.margen_neto(),
                self.rotacion_de_activos(),
                self.multiplicador_del_capital()
                )
        ]

    def roe_extendido(self):
        return [
            efecto_fiscal *
            margen_operativo *
            rotacion_de_activos *
            apalancamiento_financiero
            for efecto_fiscal,
            margen_operativo,
            rotacion_de_activos,
            apalancamiento_financiero in
            zip(
                self.efecto_fiscal(),
                self.margen_operativo(),
                self.rotacion_de_activos(),
                self.apalancamiento_financiero()
                )
        ]


def cumulative_mean(numbers: List):
    """
        Función para calcular la media acumuluda de una List
    """
    cumulative_sum = 0
    cumulative_mean_values = []

    for i, num in enumerate(numbers, 1):
        cumulative_sum += num
        mean = cumulative_sum / i
        cumulative_mean_values.append(mean)

    return cumulative_mean_values


@dataclass
class ExplotacionActivos(Analisis):
    """
        Child Class de Analisis.
        Para analizar la rotación según el promedio (se considera un cum mean)
    """

    def rotacion_de_inventarios(self):
        promedio_lista = cumulative_mean(self.js.inventarios)
        return [
            abs(costo_de_ventas / promedio)
            for costo_de_ventas, promedio in
            zip(self.js.costo_de_ventas, promedio_lista)
        ]

    def rotacion_de_cuentas_por_cobrar_comerciales_y_otras(self):
        promedio_lista = cumulative_mean(
            self.js.cuentas_por_cobrar_comerciales_y_otras
            )
        return [
            ventas / promedio
            for ventas, promedio in
            zip(self.js.ventas, promedio_lista)
        ]

    def rotacion_de_propiedades_planta_equipo(self):
        promedio_lista = cumulative_mean(self.js.propiedades_planta_equipo)
        return [
            ventas / promedio
            for ventas, promedio in
            zip(self.js.ventas, promedio_lista)
        ]

    def rotacion_de_activo_promedio(self):
        promedio_lista = cumulative_mean(self.js.activo_total)
        return [
            ventas / promedio
            for ventas, promedio in
            zip(self.js.ventas, promedio_lista)
        ]


@dataclass
class GenerarResultados:
    file: str
    """
        Evalúa todos los métodos de todas las clases que se pasen como lista
    """

    def __post_init__(self):
        self.excel = self.excel_reader()
        self.data = Json(**self.excel)
        self.AnalisisLiquidez = AnalisisLiquidez(js=self.data)
        self.AnalisisSolvenciaRiesgo = AnalisisSolvenciaRiesgo(js=self.data)
        self.RendimientoOperativo = RendimientoOperativo(js=self.data)
        self.AnalisisDupont = AnalisisDupont(js=self.data)
        self.ExplotacionActivos = ExplotacionActivos(js=self.data)
        # Lista de análisis a clasificar
        self.clases = [
            AnalisisLiquidez,
            AnalisisSolvenciaRiesgo,
            RendimientoOperativo,
            AnalisisDupont,
            ExplotacionActivos
            ]

    def excel_reader(self) -> Dict[str, List[float]]:
        excel = pd.read_excel(self.file)
        result = excel.to_json(orient="columns")
        parsed = json.loads(result)
        # Convierte el dict de cada valor en una lista simple
        lista = {k: list(w.values()) for k, w in parsed.items()}

        return lista

    @staticmethod
    def get_metodos(clase: any) -> List[str]:
        """
            Crea una lista con todos los métodos de una clase
        """
        return [
            method for method in dir(clase)
            if not method.startswith('__')
            and callable(getattr(clase, method))
        ]

    def get_resultados(self, clase: str) -> Dict[str, List[float]]:
        """
            Crea un Dict con el nombre del método y sus valores.
        """
        diccionario = {}
        for metodo in self.get_metodos(clase):
            diccionario.update({
                eval(f'self.{clase.__name__}.{metodo}.__name__'):
                    eval(f'self.{clase.__name__}.{metodo}()')
            })

        return diccionario

    def resultados_final(self) -> Dict[str, List[float]]:
        """
            Evalúa los métodos de una lista de clases y los
            combina en un solo Dict
        """
        # Se empieza por agregar los valores de Excel
        diccionario = dict(self.data.copy())
        # Luego los valores calculados
        for clase in self.clases:
            diccionario.update(self.get_resultados(clase=clase))
        return diccionario

    def csv(self):
        resultados = self.resultados_final()
        df = pd.DataFrame(resultados)
        df.to_csv('calculado.csv', index=False)


if __name__ == "__main__":
    file = askopenfilename()
    GenerarResultados(file=file).csv()
