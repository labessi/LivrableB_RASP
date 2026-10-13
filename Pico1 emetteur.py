"""
pico1_emetteur.py
Ce script tourne sur le PICO 1.

Logique :
  1. On fixe une consigne (le rapport cyclique qu'on veut appliquer).
  2. On démarre le PWM à cette valeur.
  3. On envoie la consigne au Pico 2 par UART.
  4. On attend que le Pico 2 nous renvoie la valeur qu'il a mesurée.
  5. On calcule l'écart entre consigne et mesure, puis on l'affiche.
"""

import machine
import time
import trame


# 1. Consigne fixée pour ce test
# 49000 correspond a 75 % du max.
CONSIGNE = 49000


# 2. Configuration du PWM 
pwm = machine.PWM(machine.Pin(15))   # broche GPIO15 = sortie PWM
pwm.freq(1000)                       # fréquence du signal : 1000 Hz
pwm.duty_u16(CONSIGNE)               # applique la consigne tout de suite


# 3. Configuration de la liaison UART vers le Pico 2
# TX (broche 0) = ce qu'on envoie, RX (broche 1) = ce qu'on reçoit.
# TX du Pico 1 se branche sur le RX du Pico 2,
# et vice-versa, plus un fil GND commun.
uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))

print("Pico 1 : consigne =", CONSIGNE)

# Envoie la consigne
uart.write(trame.encoder("C", CONSIGNE))

# 4. Attente de la réponse du Pico 2 
mesure = None
while mesure is None:
    if uart.any():                       #  données recues ?
        ligne = uart.readline()
        if ligne:
            prefixe, valeur = trame.decoder(ligne.decode())
            if prefixe == "M":           #  trame de mesure
                mesure = valeur
    time.sleep(0.05)                     # petite pause pour ne pas boucler a vide


# 5. Calcul et affichage du résultat
ecart = abs(CONSIGNE - mesure)
resultat = {"consigne": CONSIGNE, "mesure": mesure, "ecart": ecart}

print("Pico 1 : mesure reçue =", mesure)
print("Pico 1 : écart =", ecart)
print("Pico 1 : résultat complet =", resultat)
