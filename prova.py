from gpiozero import Button
from signal import pause

REED_PIN = 8

reed = Button(REED_PIN, pull_up=True)

def pols_detectat():
    print("Pols detectat!")

reed.when_pressed = pols_detectat

print("Esperant polsos del reed switch...")

pause()