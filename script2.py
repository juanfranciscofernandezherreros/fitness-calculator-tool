"""
script2.py — Distribución de macros basada en gasto calórico.

Este script es un ejemplo de uso de la función calcular_macros_diarios de la
librería fitness_tools.
"""
from fitness_tools import calcular_macros_diarios

if __name__ == "__main__":
    gasto_sabado = 3343  # Cambia por tu gasto real del día
    peso_actual = 72.25

    macros = calcular_macros_diarios(gasto_sabado, peso_actual)

    print("--- DISTRIBUCIÓN PARA HOY ---")
    for nutriente, valor in macros.items():
        print(f"{nutriente}: {valor}")
