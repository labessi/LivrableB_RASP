"""
pico2_recepteur.py
Ce script tourne sur le PICO 2.

Logique:
  1. On attend de recevoir la consigne envoyée par Pico 1.
  2. On lit la tension filtrée sur l'entrée ADC.
  3. Cette lecture est déjà sur la même échelle que la consigne
  4. On renvoie la mesure au Pico 1 par UART.
  5. On calcule l'écart et on l'affiche.
"""

import machine
import time
import trame


# 1. Configuration de la liaison UART vers le Pico 1
uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))


# 2. Configuration de l'ADC (lecture de la tension du filtre RC)

adc = machine.ADC(machine.Pin(26))   # broche ADC0, reliée à la sortie du filtre RC

print("Pico 2 : en attente de la consigne...")


# 3. Attente de la consigne envoyée par le Pico 1

consigne = None
while consigne is None:
    if uart.any():
        ligne = uart.readline()
        if ligne:
            prefixe, valeur = trame.decoder(ligne.decode())
            if prefixe == "C":           #  trame de consigne
                consigne = valeur
    time.sleep(0.05)

print("Pico 2 : consigne reçue =", consigne)


# 4. Lecture de la tension filtree via l'ADC
mesure = adc.read_u16()


# 5. Renvoi de la mesure au Pico 1
uart.write(trame.encoder("M", mesure))


# 6. Calcul et affichage du res
ecart = abs(consigne - mesure)
resultat = {"consigne": consigne, "mesure": mesure, "ecart": ecart}

print("Pico 2 : mesure envoyée =", mesure)
print("Pico 2 : écart =", ecart)
print("Pico 2 : résultat complet =", resultat)
