"""
trame.py
Fonctions communes d'encodage/décodage des trames envoyées par UART
entre les deux Pico.

Format : "<préfixe>:<valeur>\n"
  - préfixe "C" = consigne (envoyée par Pico 1)
  - préfixe "M" = mesure   (renvoyée par Pico 2)

Ex :
    encoder("C", 48000)  -> "C:48000\n"
    decoder("C:48000\n") -> ("C", 48000)

Ce module est partagé par pico1_emetteur.py et pico2_recepteur.py pour
éviter de dupliquer la logique des deux côtés.
"""


def encoder(prefixe: str, valeur: int) -> str:
    """
    Construit une trame texte à partir d'un préfixe et
    d'une valeur entière. Retourne une chaîne
    prête à être envoyée par uart.write().
    """
    if prefixe not in ("C", "M"):
        raise ValueError("Préfixe de trame invalide : {}".format(prefixe))
    if not (0 <= valeur <= 65535):
        raise ValueError("Valeur hors plage (0-65535) : {}".format(valeur))
    return "{}:{}\n".format(prefixe, valeur)


def decoder(trame: str):
    """
    Décode la trame reçue et retourne un tuple.
    Lève ValueError si la trame est malformée.
    """
    trame = trame.strip()
    if ":" not in trame:
        raise ValueError("Trame malformée (pas de ':') : {!r}".format(trame))

    prefixe, _, texte_valeur = trame.partition(":")
    if prefixe not in ("C", "M"):
        raise ValueError("Préfixe de trame inconnu : {!r}".format(prefixe))

    try:
        valeur = int(texte_valeur)
    except ValueError:
        raise ValueError("Valeur non numérique dans la trame : {!r}".format(texte_valeur))

    return prefixe, valeur


# --- Auto test rapide  ---
if __name__ == "__main__":
    essai = encoder("C", 48000)
    assert essai == "C:48000\n", essai
    assert decoder(essai) == ("C", 48000)

    essai2 = encoder("M", 47850)
    assert decoder(essai2) == ("M", 47850)

    # Cas d'erreur attendus
    for mauvaise_trame in ["", "C48000", "X:123", "C:abc"]:
        try:
            decoder(mauvaise_trame)
            raise AssertionError("decoder() aurait dû lever une erreur pour {!r}".format(mauvaise_trame))
        except ValueError:
            pass

    print("trame.py : tous les tests passent.")
