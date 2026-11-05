"""
pico1_emetteur.py
Ce script tourne sur le PICO 1 (l'émetteur).

Logique :
  1. On applique la consigne au PWM (GP16).
  2. On l'envoie au Pico 2 par UART (trame "C:<valeur>").
  3. On attend la mesure renvoyée par le Pico 2 (trame "M:<valeur>").
     Sans réponse, on renvoie la consigne (le Pico 2 n'est peut-être pas
     encore démarré) jusqu'à ESSAIS_MAX fois.
  4. On calcule l'écart entre consigne et mesure, puis on l'affiche.

"""

import machine
import time
import trame

PIN_PWM = 16              # GP16 (DEL1 de la carte)
PIN_TX = 8                # GP8 = TX de l'UART1
PIN_RX = 9                # GP9 = RX de l'UART1

# Consignes testées. 49000 correspond à 75 %.
CONSIGNES = [16384, 32768, 49000, 60000]

DELAI_REPONSE_MS = 2000   # temps d'attente de la mesure avant de renvoyer
ESSAIS_MAX = 10           # nombre d'envois max par consigne (20s au total)


def vider_uart(uart):
    """Jette les octets déjà reçus (parasites, réponses en retard)."""
    while uart.any():
        uart.read()


def attendre_mesure(uart, delai_ms):
    """
    Attend une trame "M:<valeur>" pendant delai_ms millisecondes.
    Retourne la valeur mesurée, ou None si rien de valide n'est arrivé.
    Les trames incomplètes ou malformées sont ignorées.
    """
    debut = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), debut) < delai_ms:
        if uart.any():
            ligne = uart.readline()
            if ligne and ligne.endswith(b"\n"):      # trame complète seulement
                try:
                    prefixe, valeur = trame.decoder(ligne.decode())
                except Exception:
                    continue                          # parasite ignore
                if prefixe == "M":
                    return valeur
        time.sleep(0.01)
    return None


def main():
    pwm = machine.PWM(machine.Pin(PIN_PWM))
    pwm.freq(1000)                        # 1000 Hz
    uart = machine.UART(1, baudrate=9600, tx=machine.Pin(PIN_TX), rx=machine.Pin(PIN_RX),
                        timeout=100, timeout_char=50)

    resultats = []
    for consigne in CONSIGNES:
        pwm.duty_u16(consigne)
        print("Pico 1 : consigne =", consigne)

        mesure = None
        for essai in range(1, ESSAIS_MAX + 1):
            vider_uart(uart)
            uart.write(trame.encoder("C", consigne))
            mesure = attendre_mesure(uart, DELAI_REPONSE_MS)
            if mesure is not None:
                break
            print("Pico 1 : pas de réponse (essai {}/{})".format(essai, ESSAIS_MAX))

        if mesure is None:
            print("Pico 1 : ÉCHEC, vérifier le câblage UART et que le Pico 2 tourne")
            continue

        ecart = abs(consigne - mesure)
        resultat = {"consigne": consigne, "mesure": mesure, "ecart": ecart}
        resultats.append(resultat)
        print("Pico 1 : mesure reçue =", mesure)
        print("Pico 1 : écart =", ecart, "({:.1f} % de l'échelle)".format(ecart * 100 / 65535))
        print("Pico 1 : résultat complet =", resultat)

    print("Pico 1 : terminé,", len(resultats), "/", len(CONSIGNES), "mesures obtenues")


main()