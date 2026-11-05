# LivrableB_RASP
Communication série et contrôle PWM entre deux Raspberry Pi Pico

Un Pico (Pico 1) fixe un rapport cyclique PWM et l'envoie par UART à un second Pico (Pico 2). Le Pico 2 mesure le signal avec son ADC, renvoie la mesure par UART, et les deux cartes calculent et affichent l'écart.

## Fichiers

- `trame.py` Encodage/décodage des trames UART 
-  `pico1_emetteur.py`  PWM, envoie la consigne, reçoit la mesure, affiche l'écart
-  `pico2_recepteur.py`  Reçoit la consigne, lit l'ADC , renvoie la mesure

## Câblage 
| Pico 1 | Pico 2 | Rôle |
|---|---|---|
| GP8 (TX) | GP9 (RX) | consigne vers le Pico 2 |
| GP9 (RX) | GP8 (TX) | mesure vers le Pico 1 |
| GND | GND | masse |
| GP16 (PWM, DEL1) | A0 (GP26) | PWM versbADC  |
| VBUS | VSYS | alimentation du Pico 2 par le Pico 1

Avant de lancer : mettre le potentiomètre R1 de la carte du Pico 2 au milieu.

## Utilisation
Aucune bibliothèque à installer (modules standard de MicroPython : `machine`, `time`).
1. Copier `trame.py` sur les deux Pico.
2. Copier `pico2_recepteur.py` sur le Pico 2 sous le nom `main.py` (démarre à la mise sous tension).
3. Brancher l'USB sur le Pico 1 (il alimente aussi le Pico 2), puis exécuter `pico1_emetteur.py`.
4. Lire les résultats dans la console du Pico 1.

## Tests
- `python3 trame.py` : auto-test de l'encodage/décodage.
- Essai sur matériel ( moyenne de 200 lectures ADC) :

| Consigne | Mesure | Écart | Écart (% de l'échelle) |
|---|---|---|---|
| 16384 | 16196 | 188 | 0,3 % |
| 32768 | 32066 | 702 | 1,1 % |
| 49000 | 47312 | 1688 | 2,6 % |
| 60000 | 58031 | 1969 | 3,0 % |

## Code réutilisé
Aucun code de tiers. Seules les fonctions standard de MicroPython sont utilisées (licence MIT).
