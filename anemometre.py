
import time
from threading import Lock
from gpiozero import Button

# GPIO 8 (BCM), pin fisic 24
REED_PIN = 8

# Constants inicials de calibratge
POLSOS_PER_VOLTA = 2.0
RADI_METRES = 0.078
FACTOR_CALIBRATGE = 2.5

# Protegeix el comptador quan hi ha lectures simultanies
_polsos = 0
_bloqueig = Lock()

reed = Button(
    REED_PIN,
    pull_up=True,
    bounce_time=0.01
)


def pols_detectat():
    global _polsos

    with _bloqueig:
        _polsos += 1


reed.when_pressed = pols_detectat


def obtenir_polsos():
    with _bloqueig:
        return _polsos


def calcular_velocitat(polsos, durada):
    if durada <= 0:
        return 0.0

    polsos_per_segon = polsos / durada
    voltes_per_segon = (
        polsos_per_segon / POLSOS_PER_VOLTA
    )

    metres_per_segon = (
        voltes_per_segon
        * 2
        * 3.141592653589793
        * RADI_METRES
        * FACTOR_CALIBRATGE
    )

    return metres_per_segon * 3.6


def mesurar_vent(durada=60):
    polsos_inicials = obtenir_polsos()
    inici = time.monotonic()

    time.sleep(durada)

    temps_transcorregut = time.monotonic() - inici
    polsos_finals = obtenir_polsos()

    polsos = polsos_finals - polsos_inicials

    return calcular_velocitat(
        polsos,
        temps_transcorregut
    )
