import os
import sys
import pandas as pd
import numpy as np

# =====================================================
# Agregar la raíz del proyecto al PATH
# =====================================================
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

# =====================================================
# Importar módulos del proyecto
# =====================================================
from src.consumo import calcular_consumo_exacto_universal
from src.metrologia import aplicar_sinceramiento_metrologico
from src.validaciones import auditar_consistencia_campo


# =====================================================
# Datos de laboratorio
# =====================================================
def simular_laboratorio_datos():
    """
    Genera un DataFrame de prueba para validar el motor
    de auditoría de HydroAI Pro.
    """

    datos = {

        "ID": [
            101,
            102,
            103,
            104
        ],

        "LEC JUNIO 2026": [
            530,
            850,
            15,
            611
        ],

        "LEC MAYO 2026": [
            500,
            800,
            980,
            600
        ],

        "LEC ABRIL 2026": [
            470,
            750,
            950,
            589
        ],

        "Consumo a Facturar": [
            30,
            50,
            15,
            11
        ],

        "OBSERVACION JUNIO": [
            "LECTURA NORMAL",
            "LECTURA NORMAL",
            "MEDIDOR CAMBIADO",
            "CERRADO PARA EL ACCESO"
        ],

        "Estrato": [
            "2 - BAJO",
            "3 - MEDIO BAJO",
            "1 - BAJO BAJO",
            "4 - MEDIO"
        ],

        "Estado Técnico": [
            "CON SERVICIO",
            "CON SERVICIO",
            "CON SERVICIO",
            "CON SERVICIO"
        ],

        "FECHA_INSTALACION": [
            "2024-06-30",
            "2017-06-30",
            "2026-01-01",
            "2025-06-30"
        ]
    }

    df = pd.DataFrame(datos)

    col_map = {

        "id_cuenta": "ID",

        "c_jun": "LEC JUNIO 2026",

        "c_may": "LEC MAYO 2026",

        "c_abr": "LEC ABRIL 2026",

        "col_facturar": "Consumo a Facturar",

        "col_observacion": "OBSERVACION JUNIO",

        "col_estrato": "Estrato",

        "col_estado_tec": "Estado Técnico",

        "col_fecha_inst": "FECHA_INSTALACION"
    }

    return df, col_map


# =====================================================
# Prueba principal
# =====================================================
def test_ingenieria_hidrica():

    df, col_map = simular_laboratorio_datos()

    # -------------------------------
    # Preparar columnas
    # -------------------------------

    df["L_JUN"] = df[col_map["c_jun"]]

    df["L_MAY"] = df[col_map["c_may"]]

    df["L_ABR"] = df[col_map["c_abr"]]

    df["FACTURADO_MES"] = df[col_map["col_facturar"]]

    df["OBS_CAMPO"] = (
        df[col_map["col_observacion"]]
        .fillna("")
        .str.upper()
    )

    # -------------------------------
    # Ejecutar algoritmos
    # -------------------------------

    df = calcular_consumo_exacto_universal(
        df,
        limite_anomalo=300
    )

    df = aplicar_sinceramiento_metrologico(
        df,
        col_map,
        "2026-06-30",
        5.0,
        0.015
    )
    
    # Ejecutar auditoría integrada sin alterar los asserts originales
    df = auditar_consistencia_campo(df, col_map)

    # -------------------------------
    # Validaciones
    # -------------------------------

    c101 = df.loc[
        df["ID"] == 101,
        "Consumo_Sincerado_Metrologico"
    ].iloc[0]

    c102 = df.loc[
        df["ID"] == 102,
        "Consumo_Sincerado_Metrologico"
    ].iloc[0]

    c103 = df.loc[
        df["ID"] == 103,
        "Consumo_Mes_Exacto"
    ].iloc[0]

    c104 = df.loc[
        df["ID"] == 104,
        "Consumo_Mes_Exacto"
    ].iloc[0]

    assert np.isclose(c101, 30.0)

    assert np.isclose(c102, 53.0)

    assert np.isclose(c103, 15.0)

    assert np.isclose(c104, 11.0)


# =====================================================
# Ejecutar manualmente
# =====================================================
if __name__ == "__main__":

    import pytest

    print("\n🚀 Ejecutando laboratorio de pruebas HydroAI Pro...\n")

    pytest.main(["-v", __file__])
