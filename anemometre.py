
import time
from threading import Lock

from gpiozero import Button


# =========================
# CONFIGURACIO
# =========================

REED_PIN = 8

# Valors inicials de calibratge.
# Cal ajustar-los per al teu anemometre.
POLSOS_PER_VOLTA = 2.0
RADI_METRES = 0.078
FACTOR_CALIBRATGE = 2.5

# Temps minim entre activacions del reed.
ANTI_REBOT_SEGONS = 0.01


# =========================
# COMPTADOR DE POLSOS
# =========================

_polsos = 0
_bloqueig = Lock()


def _pols_detectat():
    global _polsos

    with _bloqueig:
        _polsos += 1


reed = Button(
    REED_PIN,
    pull_up=True,
    bounce_time=ANTI_REBOT_SEGONS
)

reed.when_pressed = _pols_detectat


def obtenir_polsos():
    """Retorna el nombre acumulat de polsos."""
    with _bloqueig:
        return _polsos


# =========================
# CALCUL DE VELOCITAT
# =========================

def calcular_velocitat(polsos, durada):
    """Calcula la velocitat mitjana del vent en km/h."""

    if durada <= 0 or polsos <= 0:
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
    """
    Mesura el vent durant l'interval indicat.
    Retorna la velocitat mitjana en km/h.
    """

    polsos_inicials = obtenir_polsos()
    inici = time.monotonic()

    time.sleep(durada)

    durada_real = time.monotonic() - inici
    polsos_finals = obtenir_polsos()

    polsos = polsos_finals - polsos_inicials

    return calcular_velocitat(
        polsos,
        durada_real
    )
