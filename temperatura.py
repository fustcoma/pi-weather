
import board
import adafruit_dht
import time
import math
import csv
import os
import subprocess

from datetime import datetime
from anemometre import obtenir_polsos, calcular_velocitat


# =========================
# CONFIGURACIO
# =========================

DURADA_MESURA = 60
INTERVAL_LECTURA = 2
INTERVAL_PUSH = 300

FITXER_ACTUAL = "pi.txt"
FITXER_HISTORIAL = "historial.csv"

DHT_PIN = board.D2


# =========================
# SENSOR DHT11
# =========================

dht = adafruit_dht.DHT11(DHT_PIN)


# =========================
# SENSACIO TERMICA
# =========================

def calcular_sensacio(temperatura, humitat):
    e = (
        (humitat / 100)
        * 6.105
        * math.exp(
            17.72 * temperatura /
            (237.7 + temperatura)
        )
    )

    return temperatura + 0.33 * e - 4


# =========================
# HISTORIAL
# =========================

CAPCALERA_HISTORIAL = [
    "data",
    "hora",
    "temperatura",
    "humitat",
    "sensacio",
    "vent"
]


def crear_historial_si_no_existeix():
    if not os.path.exists(FITXER_HISTORIAL):
        with open(
            FITXER_HISTORIAL,
            "w",
            newline="",
            encoding="utf-8"
        ) as fitxer:
            escriptor = csv.writer(fitxer)
            escriptor.writerow(CAPCALERA_HISTORIAL)


def adaptar_historial():
    """
    Afegeix la columna vent a un historial antic
    sense eliminar les dades existents.
    """

    crear_historial_si_no_existeix()

    with open(
        FITXER_HISTORIAL,
        "r",
        newline="",
        encoding="utf-8"
    ) as fitxer:
        files = list(csv.reader(fitxer))

    if not files:
        files = [CAPCALERA_HISTORIAL]

    capcalera = files[0]

    if capcalera == CAPCALERA_HISTORIAL:
        return

    if capcalera[:5] != CAPCALERA_HISTORIAL[:5]:
        raise ValueError(
            "La capcalera de historial.csv "
            "no te el format esperat."
        )

    files_noves = [CAPCALERA_HISTORIAL]

    for fila in files[1:]:
        if len(fila) < 5:
            continue

        fila_nova = fila[:5]

        if len(fila) >= 6:
            fila_nova.append(fila[5])
        else:
            # Les mesures antigues no tenen
            # dades de vent.
            fila_nova.append("")

        files_noves.append(fila_nova)

    fitxer_temporal = FITXER_HISTORIAL + ".tmp"

    with open(
        fitxer_temporal,
        "w",
        newline="",
        encoding="utf-8"
    ) as fitxer:
        escriptor = csv.writer(fitxer)
        escriptor.writerows(files_noves)

    os.replace(
        fitxer_temporal,
        FITXER_HISTORIAL
    )


def guardar_historial(
    temperatura,
    humitat,
    sensacio,
    vent,
    moment
):
    adaptar_historial()

    with open(
        FITXER_HISTORIAL,
        "a",
        newline="",
        encoding="utf-8"
    ) as fitxer:
        escriptor = csv.writer(fitxer)

        escriptor.writerow([
            moment.strftime("%d/%m/%Y"),
            moment.strftime("%H:%M:%S"),
            f"{temperatura:.2f}",
            f"{humitat:.2f}",
            f"{sensacio:.2f}",
            f"{vent:.2f}"
        ])


# =========================
# DADES ACTUALS
# =========================

def guardar_actual(
    temperatura,
    humitat,
    sensacio,
    vent,
    moment
):
    with open(
        FITXER_ACTUAL,
        "w",
        encoding="utf-8"
    ) as fitxer:
        fitxer.write(f"{temperatura:.2f}\n")
        fitxer.write(f"{humitat:.2f}\n")
        fitxer.write(f"{sensacio:.2f}\n")
        fitxer.write(f"{vent:.2f}\n")
        fitxer.write(
            moment.strftime("%d/%m/%Y %H:%M:%S")
        )


# =========================
# GITHUB
# =========================

def pujar_github():
    try:
        print("Comprovant GitHub...")

        subprocess.run(
            [
                "git",
                "add",
                FITXER_ACTUAL,
                FITXER_HISTORIAL
            ],
            check=True
        )

        resultat_commit = subprocess.run(
            [
                "git",
                "commit",
                "-m",
                "Actualitzacio dades meteorologiques"
            ],
            capture_output=True,
            text=True
        )

        if resultat_commit.returncode == 0:
            print("Canvis preparats per pujar.")
        else:
            print("No hi ha canvis nous per crear un commit.")

        resultat_push = subprocess.run(
            ["git", "push"],
            capture_output=True,
            text=True
        )

        if resultat_push.returncode == 0:
            print("Dades pujades a GitHub.")
            return True

        print("Error fent push:")
        print(resultat_push.stderr)

        return False

    except Exception as error:
        print(f"Error amb GitHub: {error}")
        return False


# =========================
# PROGRAMA PRINCIPAL
# =========================

adaptar_historial()

ultim_push = time.monotonic()

print("Estacio meteorologica iniciada.")
print("Anemometre connectat al GPIO 8.")


try:
    while True:
        temperatures = []
        humitats = []

        # Comencem a comptar el vent
        # abans de la primera lectura.
        polsos_inicials = obtenir_polsos()
        inici = time.monotonic()

        print("Comencant una nova mesura.")

        while time.monotonic() - inici < DURADA_MESURA:
            try:
                temperatura = dht.temperature
                humitat = dht.humidity

                if (
                    temperatura is not None
                    and humitat is not None
                ):
                    temperatures.append(temperatura)
                    humitats.append(humitat)

                    print(
                        f"Lectura: {temperatura:.2f} C, "
                        f"{humitat:.2f} %"
                    )

            except RuntimeError as error:
                print(
                    f"Error temporal del DHT11: {error}"
                )

            except Exception as error:
                print(f"Error del sensor: {error}")

            temps_rest = (
                DURADA_MESURA
                - (time.monotonic() - inici)
            )

            if temps_rest > 0:
                time.sleep(
                    min(INTERVAL_LECTURA, temps_rest)
                )

        # Calculem la velocitat mitjana
        # durant el mateix interval de mesura.
        durada_vent = time.monotonic() - inici
        polsos_finals = obtenir_polsos()

        polsos_vent = (
            polsos_finals - polsos_inicials
        )

        vent_kmh = calcular_velocitat(
            polsos_vent,
            durada_vent
        )

        if temperatures and humitats:
            temperatura_mitjana = (
                sum(temperatures) / len(temperatures)
            )

            humitat_mitjana = (
                sum(humitats) / len(humitats)
            )

            sensacio = calcular_sensacio(
                temperatura_mitjana,
                humitat_mitjana
            )

            moment = datetime.now()

            print()
            print("Resultat de la mesura:")
            print(
                f"Temperatura: "
                f"{temperatura_mitjana:.2f} C"
            )
            print(f"Humitat: {humitat_mitjana:.2f} %")
            print(f"Sensacio: {sensacio:.2f} C")
            print(f"Vent: {vent_kmh:.2f} km/h")
            print(f"Polsos de vent: {polsos_vent}")
            print(
                f"Hora: {moment.strftime('%d/%m/%Y %H:%M:%S')}"
            )

            guardar_actual(
                temperatura_mitjana,
                humitat_mitjana,
                sensacio,
                vent_kmh,
                moment
            )

            guardar_historial(
                temperatura_mitjana,
                humitat_mitjana,
                sensacio,
                vent_kmh,
                moment
            )

            print("Dades guardades.")

        else:
            print(
                "No s'han pogut obtenir "
                "dades suficients del DHT11."
            )

        if (
            time.monotonic() - ultim_push
            >= INTERVAL_PUSH
        ):
            pujar_github()
            ultim_push = time.monotonic()

        print("Esperant la seguent mesura.")
        print()

except KeyboardInterrupt:
    print("Aturant l'estacio meteorologica.")

finally:
    dht.exit()
