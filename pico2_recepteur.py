"""
pico2_recepteur.py
Ce script tourne sur le PICO 2 (récepteur/mesure), monté sur une
carte SED1515. Enregistré sous le nom main.py, il démarre dès la mise sous tension.

Logique (en boucle, jusqu'à l'arrêt du programme) :
  1. On attend une trame de consigne "C:<valeur>" envoyée par le Pico 1.
  2. On laisse le filtre RC se stabiliser, puis on lit l'ADC (GP26).
     La lecture est une moyenne de plusieurs échantillons.
  3. La lecture est déjà sur la même échelle que la consigne.
     On renvoie la mesure au Pico 1 (trame "M:<valeur>").
  4. On calcule l'écart et on l'affiche de ce côté aussi.

Broches : UART1 sur GP8 (TX) / GP9 (RX), ADC sur GP26 (A0).
"""

import machine
import time
import trame

PIN_TX = 8                    # GP8 = TX de l'UART1
PIN_RX = 9                    # GP9 = RX de l'UART1
PIN_ADC = 26                  # GP26 = ADC0

DELAI_STABILISATION_S = 0.5   # temps laissé au filtre RC pour se stabiliser
NB_ECHANTILLONS = 200         # nombre de lectures ADC moyennées


def lire_moyenne(adc, nombre=NB_ECHANTILLONS):
    """
    Lit l'ADC plusieurs fois et retourne la moyenne.
    Le pas de 370 µs n'est pas un multiple de 1000 µs 
    les lectures tombent à des points différents du cycle donc la moyenne
    redonne la valeur moyenne du signal même si le filtre est imparfait.
    """
    total = 0
    for _ in range(nombre):
        total += adc.read_u16()
        time.sleep_us(370)
    return total // nombre


def attendre_consigne(uart):
    """Bloque jusqu'à la réception d'une trame "C:<valeur>" valide."""
    while True:
        if uart.any():
            ligne = uart.readline()
            if ligne and ligne.endswith(b"\n"):      # trame complète seulement
                try:
                    prefixe, valeur = trame.decoder(ligne.decode())
                except Exception:
                    continue                          # parasite ignore
                if prefixe == "C":
                    return valeur
        time.sleep(0.01)


def main():
    uart = machine.UART(1, baudrate=9600, tx=machine.Pin(PIN_TX), rx=machine.Pin(PIN_RX),
                        timeout=100, timeout_char=50)
    adc = machine.ADC(machine.Pin(PIN_ADC))

    print("Pico 2 : en attente de la consigne...")
    while True:
        consigne = attendre_consigne(uart)
        print("Pico 2 : consigne reçue =", consigne)

        time.sleep(DELAI_STABILISATION_S)
        mesure = lire_moyenne(adc)
        uart.write(trame.encoder("M", mesure))

        ecart = abs(consigne - mesure)
        resultat = {"consigne": consigne, "mesure": mesure, "ecart": ecart}
        print("Pico 2 : mesure envoyée =", mesure)
        print("Pico 2 : écart =", ecart, "({:.1f} % de l'échelle)".format(ecart * 100 / 65535))
        print("Pico 2 : résultat complet =", resultat)


main()