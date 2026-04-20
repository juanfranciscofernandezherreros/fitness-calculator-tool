"""
script1.py — Cálculo de grasa corporal y masa magra (fórmula US Navy).

Este script es un ejemplo de uso de la función calcular_grasa_navy de la
librería fitness_tools.
"""
from fitness_tools import calcular_grasa_navy

if __name__ == "__main__":
    altura_cm = 175.0   # Cambia por tu altura real
    cintura_cm = 84.0   # Cambia por tu medida real
    cuello_cm = 38.0    # Cambia por tu medida real
    peso_actual = 72.25

    grasa, magra = calcular_grasa_navy(peso_actual, altura_cm, cintura_cm, cuello_cm)
    print(f"Porcentaje de Grasa: {grasa}%")
    print(f"Masa Magra: {magra} kg")
