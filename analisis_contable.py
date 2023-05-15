import json
from dataclasses import dataclass
import pandas as pd
from pydantic import BaseModel


class Activo(BaseModel):
    """
        Clase modelo que une las cuentas del activo
    """
    cuentas_por_cobrar_comerciales_y_otras: float
    efectivo_y_equivalentes: float
    inventarios: float
    otras_provisiones: float
    activo_corriente: float
    activo_no_corriente: float
    activo_total: float


class Pasivo(BaseModel):
    """
        Clase modelo que une las cuentas del pasivo
    """
    pasivo_corriente: float
    pasivo_no_corriente: float
    pasivo_total: float


class PatrimonioNeto(BaseModel):
    """
        Clase modelo que une las cuentas del patrimonio neto
    """
    patrimonio: float


class BalanceGeneral(BaseModel):
    """
        Clase modelo que une las cuentas del activo, pasivo y patrimonio neto
    """
    activo: Activo
    pasivo: Pasivo
    patrimonio_neto: PatrimonioNeto


class EstadoDeResultados(BaseModel):
    """
        Clase modelo que une las cuentas del Estado de Resultados
    """
    ventas: float
    costo_de_ventas: float
    gastos_financieros: float
    utilidad_operativa: float
    utilidad_antes_de_impuestos: float
    utilidad_neta: float


class Analisis(object):
    """
        Parent Class para las demás clases de Analisis.
        Hereda el Balance general y el Estados de Resultados
    """
    bg: BalanceGeneral
    er: EstadoDeResultados


class AnalisisLiquidez(Analisis):
    """
        Child Class de Analisis.
        Para analizar la liquidez
    """

    def dias_cobro(self):
        return (
                self.bg.activo.cuentas_por_cobrar_comerciales_y_otras * 365
        ) / self.er.ventas

    def dias_inventario(self):
        return abs(
            (
                    self.bg.activo.inventarios * 365
            ) / self.er.costo_de_ventas
        )

    def razon_acida(self):
        return (
                self.bg.activo.activo_corriente -
                self.bg.activo.inventarios
        ) / self.bg.pasivo.pasivo_corriente

    def razon_super_acida(self):
        return (
                self.bg.activo.activo_corriente -
                self.bg.activo.inventarios -
                self.bg.activo.cuentas_por_cobrar_comerciales_y_otras
        ) / self.bg.pasivo.pasivo_corriente


class AnalisisSolvenciaRiesgo(Analisis):
    """
        Child Class de Analisis.
        Para analizar la solvencia y el riesgo
    """

    def pasivo_no_corriente_sobre_activo(self):
        return self.bg.pasivo.pasivo_no_corriente / self.bg.activo.activo_total

    def pasivo_no_corriente_sobre_patrimonio(self):
        return self.bg.pasivo.pasivo_no_corriente / self.bg.patrimonio_neto.patrimonio

    def pasivo_sobre_activos(self):
        return self.bg.pasivo.pasivo_total / self.bg.activo.activo_total

    def patrimonio_sobre_actibos(self):
        return self.bg.patrimonio_neto.patrimonio / self.bg.activo.activo_total

    def periodo_de_intereses_ganados(self):
        return self.er.utilidad_operativa / self.er.gastos_financieros

    def razon_de_flujo_de_efectivo(self):
        return (
                self.er.utilidad_neta -
                self.bg.activo.otras_provisiones
        ) / self.bg.pasivo.pasivo_corriente


class RendimientoOperativo(Analisis):
    """
        Child Class de Analisis.
        Para analizar el rendimiento operativo
    """

    def margen_antes_de_impuesto(self):
        return self.er.utilidad_antes_de_impuestos / self.er.ventas

    def margen_bruto(self):
        return (self.er.ventas - self.er.costo_de_ventas) / self.er.ventas

    def margen_de_utilidad(self):
        return self.er.utilidad_neta / self.er.ventas

    def margen_operativo(self):
        return self.er.utilidad_operativa / self.er.ventas


class AnalisisDupont(Analisis):
    """
        Child Class de Analisis.
        Para analizar el sistema Dupont
    """

    def apalancamiento_financiero(self):
        return (
                self.er.utilidad_antes_de_impuestos /
                self.er.utilidad_operativa
        ) * self.multiplicador_del_capital()

    def efecto_fiscal(self):
        return self.er.utilidad_neta / self.er.utilidad_antes_de_impuestos

    def margen_neto(self):
        return self.er.utilidad_neta / self.er.ventas

    def margen_operativo(self):
        return self.er.utilidad_operativa / self.er.ventas

    def multiplicador_del_capital(self):
        return self.bg.activo.activo_total / self.bg.patrimonio_neto.patrimonio

    def rotacion_de_activos(self):
        return self.er.ventas / self.bg.activo.activo_total

    def roe(self):
        return self.margen_neto() * \
            self.rotacion_de_activos() * \
            self.multiplicador_del_capital()

    def roe_extendido(self):
        return self.efecto_fiscal() * \
            self.margen_operativo() * \
            self.rotacion_de_activos() * \
            self.apalancamiento_financiero()


@dataclass
class ExcelReader:
    file: str

    def reader(self):
        excel = pd.read_excel(self.file)
        result = excel.to_json(orient="columns")
        parsed = json.loads(result)

        return parsed


if __name__ == "__main__":
    file = 'analisis_contable_modelo.xlsx'
    print(ExcelReader(file=file).reader())
