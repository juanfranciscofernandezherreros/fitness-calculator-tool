"""
script3.py — Cálculo rápido de carbohidratos para el día.

Este script es un ejemplo de uso de la función carbos_flash de la
librería fitness_tools.
"""
from fitness_tools import carbos_flash

if __name__ == "__main__":
    peso_actual = 72.25
    gasto_hoy = 2930  # Cambia por tu gasto real del día (ej. un 10K)

    carbos = carbos_flash(gasto_hoy, peso_actual)
    print(f"Gramos de hidratos para hoy: {carbos}g")
