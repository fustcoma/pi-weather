<img src="images/web-icon.png" alt="Pi Weather">

# π Weather

π Weather és una estació meteorològica amb Raspberry Pi Zero W que recull dades ambientals amb un sensor DHT11 i un anemòmetre casolà. El projecte permet consultar la temperatura, la humitat relativa, la sensació tèrmica calculada i la velocitat del vent des d'una pàgina web publicada amb GitHub Pages.

La Raspberry Pi fa les mesures, les desa en fitxers locals i les publica automàticament al repositori de GitHub. El DHT11 proporciona temperatura i humitat; l'anemòmetre utilitza un interruptor magnètic (*reed switch*) i imants per detectar el gir de les cassoletes i estimar la velocitat del vent. La velocitat calculada depèn del muntatge i del factor de calibratge, per tant s'ha de considerar una estimació fins que es contrasti amb un instrument de referència.

## Funcionament general

El sistema està dividit en dues parts: la Raspberry Pi, que s'encarrega de mesurar i publicar les dades, i la pàgina web, que s'encarrega de mostrar-les.

```text
DHT11 ------------------+
                         |
Anemòmetre -> reed switch +--> Raspberry Pi Zero W
                              |
                              +--> temperatura.py
                                      |
                                      +--> pi.txt
                                      |
                                      +--> historial.csv
                                      |
                                      +--> Git commit
          |
          +--> Git push
                  |
                  v
               GitHub
                  |
                  v
             GitHub Pages
                  |
                  v
          index.html + script.js
```

El funcionament és:

1. La Raspberry Pi llegeix el DHT11 durant 60 segons.
2. Es fa una lectura aproximadament cada 2 segons.
3. Es calcula la mitjana de totes les lectures.
4. Es calcula la sensació tèrmica a partir de temperatura i humitat.
5. Es compten els impulsos del *reed switch* de l'anemòmetre durant el període de mesura i se n'estima la velocitat del vent.
6. Les dades actuals, inclosa la velocitat del vent, es guarden a `pi.txt`.
7. La nova mesura s'afegeix a `historial.csv`.
8. Cada 5 minuts aproximadament es fa un commit i un push a GitHub.
9. La pàgina web comprova les dades cada 10 segons.
10. Les gràfiques s'actualitzen automàticament quan apareixen noves dades.

No cal tenir la pàgina web oberta a la Raspberry Pi.

---

# Requisits

## Hardware

* Raspberry Pi Zero W
* Sensor DHT11
* Anemòmetre de tres cassoletes amb coixinet 608, imants i interruptor magnètic (*reed switch*)
* Connexió a Internet
* Cables per connectar els sensors

## Software

* Python 3
* Git
* GitHub
* GitHub Pages
* Un repositori GitHub

En aquest projecte el repositori és:

```text
fustcoma/pi-weather
```

---

# Connexió del DHT11

El DHT11 està connectat de la següent manera:

```text
DHT11 DATA -> GPIO 2
DHT11 VCC  -> 3.3 V
DHT11 GND  -> GND
```

El GPIO 2 correspon al pin físic 3 de la Raspberry Pi.

El programa utilitza:

```python
board.D2
```

Si el mòdul DHT11 no incorpora una resistència pull-up, es pot utilitzar una resistència d'entre 4.7 kΩ i 10 kΩ entre DATA i 3.3 V.

---

# Estructura del projecte

El repositori conté:

```text
pi-weather/
|
+-- index.html
+-- script.js
+-- temperatura.py
+-- prova.py              # programa de prova independent de l'anemòmetre
+-- pi.txt
+-- historial.csv
```

## `temperatura.py`

És el programa principal que s'executa a la Raspberry Pi.

S'encarrega de:

* Llegir el DHT11.
* Fer lectures durant 60 segons.
* Fer una lectura cada 2 segons.
* Calcular les mitjanes.
* Calcular la sensació tèrmica.
* Actualitzar `pi.txt`.
* Actualitzar `historial.csv`.
* Fer commits a Git.
* Fer push a GitHub.
* Continuar funcionant encara que un `git push` falli.

## `pi.txt`

Conté les dades més recents. Amb la integració de l'anemòmetre, el format actual afegeix la velocitat del vent com a quarta línia i deixa la data i l'hora a la cinquena.

Format:

```text
temperatura
humitat
sensacio
vent_kmh
data i hora
```

Exemple:

```text
26.60
53.36
29.00
2.43
06/09/2026 22:50:29
```

Aquest fitxer s'utilitza per mostrar les dades actuals a la web.

## `historial.csv`

Conté totes les mesures.

Format:

```text
data,hora,temperatura,humitat,sensacio,vent_kmh
```

Exemple:

```text
data,hora,temperatura,humitat,sensacio,vent_kmh
06/09/2026,22:50:29,26.60,53.36,29.00,2.43
06/09/2026,22:51:32,26.70,53.10,29.10,2.10
```

Si el fitxer no existeix, `temperatura.py` el crea automàticament amb la capçalera corresponent.

## `index.html`

És la interfície de la pàgina web.

Mostra:

* Temperatura actual.
* Humitat actual.
* Sensació tèrmica actual.
* Velocitat actual del vent.
* Data i hora de l'última actualització.
* Gràfica de temperatura.
* Gràfica d'humitat.
* Gràfica de sensació tèrmica.
* Gràfica de velocitat del vent, si aquesta sèrie està inclosa a la versió desplegada.

La pàgina utilitza un disseny fosc.

Els períodes disponibles són:

```text
1 hora
6 hores
24 hores
7 dies
Tot
```

## `script.js`

S'encarrega de:

* Carregar `pi.txt`.
* Carregar `historial.csv`.
* Actualitzar les dades actuals.
* Crear les gràfiques.
* Canviar el període de les gràfiques.
* Actualitzar automàticament les dades cada 10 segons.
* Detectar períodes sense dades.

Utilitza Chart.js per generar les gràfiques.

---

# Instal·lació

## 1. Clonar el repositori

Des de la Raspberry Pi:

```bash
cd ~
git clone https://github.com/fustcoma/pi-weather.git
```

Entrar al projecte:

```bash
cd ~/pi-weather
```

---

# 2. Crear l'entorn virtual de Python

Crear l'entorn virtual:

```bash
python3 -m venv ~/dht-env
```

Activar-lo:

```bash
source ~/dht-env/bin/activate
```

Quan estigui activat, normalment apareixerà `(dht-env)` al principi de la terminal.

Per sortir de l'entorn virtual:

```bash
deactivate
```

---

# 3. Instal·lar les llibreries

Amb l'entorn virtual activat:

```bash
pip install adafruit-blinka
pip install adafruit-circuitpython-dht
```

El programa actual no necessita NumPy.

---

# 4. Configurar Git

Git necessita saber quin usuari farà els commits.

Configurar el nom:

```bash
git config --global user.name "EL_TEU_USERNAME"
```

Configurar el correu:

```bash
git config --global user.email "EL_TEU_EMAIL"
```

Comprovar-ho:

```bash
git config --global --list
```

---

# 5. Crear un Personal Access Token de GitHub

Per poder fer `git push` des de la Raspberry Pi mitjançant HTTPS, GitHub necessita una credencial.

La contrasenya normal del compte de GitHub no s'utilitza per a aquest procés.

Cal crear un Personal Access Token.

## 5.1 Entrar a la configuració

A GitHub:

1. Obre `Settings`.
2. Entra a `Developer settings`.
3. Entra a `Personal access tokens`.
4. Selecciona `Fine-grained tokens`.
5. Selecciona `Generate new token`.

## 5.2 Configurar el token

Posa un nom identificatiu, per exemple:

```text
Raspberry Pi Estació Meteorològica
```

Selecciona una data d'expiració.

A `Repository access`, selecciona:

```text
Only select repositories
```

I selecciona:

```text
usuari/nom-del-repositori
```

A `Repository permissions`, busca:

```text
Contents
```

I posa:

```text
Read and write
```

Finalment, crea el token.

## 5.3 Guardar el token

GitHub només mostra el token complet una vegada.

Cal copiar-lo quan aparegui.

El token no s'ha d'introduir mai dins de:

```text
temperatura.py
index.html
script.js
```

Tampoc s'ha de pujar a GitHub.

---

# 6. Fer que Git recordi el token

Perquè Git no demani el token en cada `git push`, configurar:

```bash
git config --global credential.helper store
```

Després fer un primer push:

```bash
cd ~/pi-weather
git push
```

Git demanarà:

```text
Username:
Password:
```

A `Username`, utilitza el teu nom d'usuari de GitHub:

A `Password`, enganxa el Personal Access Token.

No utilitzis la contrasenya normal del compte de GitHub.

Després d'això, Git guardarà la credencial localment i els futurs `git push` no haurien de tornar a demanar el token.

La credencial quedarà guardada a:

```text
~/.git-credentials
```

Aquest fitxer conté informació sensible.

No s'ha de compartir ni pujar al repositori.

---

# 7. Provar GitHub abans de continuar

Abans de configurar l'automatització, és recomanable comprovar que la Raspberry pot fer push.

Executar:

```bash
cd ~/pi-weather
git status
```

Després:

```bash
git push
```

Si el push funciona sense errors i no torna a demanar el token en les següents ocasions, Git està configurat correctament.

---

# Anemòmetre casolà

## Per a què serveix

L'anemòmetre mesura la velocitat aproximada del vent. El muntatge és un anemòmetre de tres cassoletes: quan el vent les empeny, el rotor gira. Els imants instal·lats a la part giratòria passen a prop d'un interruptor magnètic (*reed switch*), que obre o tanca el contacte. La Raspberry Pi detecta aquests canvis com a impulsos elèctrics.

El programa compta els impulsos durant un interval conegut i, a partir del nombre d'impulsos i del factor de conversió/calibratge utilitzat pel muntatge, calcula una velocitat en km/h. La lectura no és una mesura meteorològica certificada: la forma de les cassoletes, la distància dels imants al *reed switch*, la fricció del coixinet i el calibratge influeixen en el resultat.

## Peces utilitzades

El muntatge s'ha basat en el disseny d'[alf45tar/Anemometer](https://github.com/alf45tar/Anemometer), adaptat per connectar-lo directament a una Raspberry Pi Zero W:

* Coixinet 608 de 8 × 22 × 7 mm.
* Tres insercions roscades M3 i tres cargols M3 × 10.
* Interruptor magnètic (*reed switch*).
* Dos imants de 6 × 3 mm.
* Junta tòrica de 8 × 2 mm.
* Cassoletes i peces impreses en 3D del disseny original.

El crèdit del disseny original correspon a alf45tar. La lectura amb Raspberry Pi i la integració amb π Weather són l'adaptació d'aquest projecte.

## Connexió del reed switch

La connexió final utilitzada és:

```text
Raspberry Pi Zero W                 Reed switch
-----------------------------------------------
GPIO 8 (BCM) / pin físic 24  ------ un terminal
GND / pin físic 20            ------ l'altre terminal
```

El programa identifica el pin pel número BCM `8`, no pel número físic. Això és important: `REED_PIN = 8` vol dir GPIO 8, que físicament és el pin 24 de la capçalera de 40 pins. El pin físic 20 és GND.

El circuit utilitza la resistència *pull-up* interna del GPIO. Per això, el *reed switch* es connecta entre GPIO 8 i GND: no s'ha de connectar a 5 V. Quan el contacte està obert, l'entrada normalment es llegeix com a HIGH; quan el contacte es tanca, es llegeix com a LOW. El programa de prova o la llibreria poden expressar aquest estat com `is_pressed` o com un canvi d'estat.

Abans d'alimentar el muntatge, comprova el número dels pins amb un esquema de la capçalera de la Raspberry Pi. No confonguis GPIO 8 amb el pin físic 8: són numeracions diferents.

## Per a què serveix `prova.py`

`prova.py` és un programa de diagnòstic independent per comprovar l'anemòmetre sense haver d'arrencar tot el sistema meteorològic ni publicar dades a GitHub. Serveix per aïllar els problemes del sensor:

1. Llegeix l'entrada GPIO connectada al *reed switch*.
2. Detecta els impulsos generats quan els imants passen pel contacte.
3. Comprova que el senyal arriba realment a la Raspberry Pi.
4. Permet observar si el rotor i el contacte magnètic funcionen abans d'integrar la lectura a `temperatura.py`.

Durant les proves es va arribar a obtenir una sortida semblant a:

```text
Velocitat: 2.43 km/h
```

Aquesta línia és un exemple d'una lectura de prova, no una velocitat fixa ni una garantia de calibratge. Si `prova.py` detecta els impulsos però `temperatura.py` no, cal revisar la integració del codi principal. Si no detecta cap impuls, primer s'han de comprovar el cablejat, el contacte i els imants.

Executa'l des del directori del projecte i amb el mateix entorn de Python que s'utilitza per a l'estació:

```bash
cd ~/pi-weather
source ~/dht-env/bin/activate
python prova.py
```

Atura la prova amb `Ctrl + C` si el programa continua llegint el sensor. `prova.py` no substitueix `temperatura.py`: és una eina de diagnòstic per provar l'anemòmetre de manera separada.

## Paràmetres de mesura

La configuració de mesura treballada per al projecte utilitza aquests intervals:

```python
REED_PIN = 8
DURADA_MESURA = 60
INTERVAL_LECTURA = 2
INTERVAL_PUSH = 300
```

* `REED_PIN = 8`: GPIO BCM on està connectat el *reed switch*.
* `DURADA_MESURA = 60`: durada del període de mesura, en segons.
* `INTERVAL_LECTURA = 2`: interval de lectura/mostreig, en segons.
* `INTERVAL_PUSH = 300`: interval aproximat entre publicacions a GitHub, és a dir, 300 segons o 5 minuts.

El càlcul de la velocitat depèn del recompte d'impulsos i dels paràmetres de conversió del disseny. Per obtenir valors fiables, compara l'anemòmetre amb un anemòmetre de referència en diverses velocitats de vent i ajusta el factor de calibratge si cal.

## Com s'integra a π Weather

`temperatura.py` continua sent el programa principal. A més de llegir el DHT11, ara també recull la informació de l'anemòmetre i desa la velocitat del vent als fitxers de dades:

* `pi.txt`: velocitat del vent a la quarta línia; la data i l'hora passen a la cinquena.
* `historial.csv`: velocitat del vent al camp `vent_kmh`, després de les dades de temperatura, humitat i sensació tèrmica.

La pàgina web només pot mostrar les dades de vent si el seu `script.js` llegeix el nou camp i `index.html` conté l'element visual corresponent. Si la Raspberry Pi ja calcula el vent però la web no el mostra, comprova primer el contingut dels fitxers i després que la versió de la web publicada inclogui aquests canvis.

---

# 8. Provar el sensor manualment

Activar l'entorn virtual:

```bash
source ~/dht-env/bin/activate
```

Entrar al projecte:

```bash
cd ~/pi-weather
```

Executar:

```bash
python temperatura.py
```

El programa començarà a fer lectures.

Es poden veure dades semblants a:

```text
Lectura: 26.00 C, 53.00 %
Lectura: 26.00 C, 54.00 %
Lectura: 26.00 C, 53.00 %
```

Després de completar els 60 segons de mesura, calcularà:

```text
Temperatura mitjana
Humitat mitjana
Sensació tèrmica
```

I actualitzarà:

```text
pi.txt
historial.csv
```

Per aturar-lo manualment:

```text
Ctrl + C
```

---

# 9. Crear el servei automàtic

Perquè el programa no s'hagi d'executar manualment cada vegada que s'encén la Raspberry Pi, s'utilitza `systemd`.

Es crea un servei anomenat:

```text
estacio.service
```

Crear-lo:

```bash
sudo nano /etc/systemd/system/estacio.service
```

Posar-hi:

```ini
[Unit]
Description=Estacio meteorologica DHT11
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pi-weather
ExecStart=/home/pi/dht-env/bin/python /home/pi/pi-weather/temperatura.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Guardar i sortir.

Aquest fitxer indica a systemd:

* Quin programa executar.
* Quin usuari utilitzar.
* En quina carpeta executar-lo.
* Quin Python utilitzar.
* Que s'ha de reiniciar si el programa falla.
* Que s'ha d'iniciar durant l'arrencada de la Raspberry Pi.

Els camins han de coincidir amb la ubicació real del projecte i de l'entorn virtual.

---

# 10. Activar el servei

Després de crear el fitxer:

```bash
sudo systemctl daemon-reload
```

Iniciar el servei:

```bash
sudo systemctl start estacio.service
```

Comprovar l'estat:

```bash
sudo systemctl status estacio.service
```

Hauria d'aparèixer:

```text
Active: active (running)
```

---

# 11. Activar l'inici automàtic

Perquè el programa s'executi automàticament cada vegada que la Raspberry Pi s'encén:

```bash
sudo systemctl enable estacio.service
```

A partir d'aquest moment no cal executar manualment:

```bash
python temperatura.py
```

ni:

```bash
source ~/dht-env/bin/activate
```

durant l'arrencada.

Systemd utilitza directament:

```text
/home/pi/dht-env/bin/python
```

---

# 12. Comprovar l'arrencada automàtica

Es pot comprovar reiniciant la Raspberry:

```bash
sudo reboot
```

Quan torni a estar disponible:

```bash
sudo systemctl status estacio.service
```

Si apareix:

```text
Active: active (running)
```

el programa s'ha iniciat automàticament.

També es poden veure els logs:

```bash
journalctl -u estacio.service -f
```

---

# Control del servei

## Iniciar

```bash
sudo systemctl start estacio.service
```

## Aturar

```bash
sudo systemctl stop estacio.service
```

## Reiniciar

```bash
sudo systemctl restart estacio.service
```

## Veure l'estat

```bash
sudo systemctl status estacio.service
```

## Veure els logs en temps real

```bash
journalctl -u estacio.service -f
```

## Veure les últimes 100 línies

```bash
journalctl -u estacio.service -n 100
```

## Desactivar l'inici automàtic

```bash
sudo systemctl disable estacio.service
```

Això no elimina el servei.

Només evita que s'iniciï automàticament.

Per tornar-lo a activar:

```bash
sudo systemctl enable estacio.service
```

---

# Actualització de les dades

Cada cicle de `temperatura.py` dura aproximadament:

```text
60 segons de mesura
+
10 segons d'espera
```

Durant els 60 segons es fa una lectura cada 2 segons.

Les lectures obtingudes es fan servir per calcular una mitjana.

Després es guarden les dades a:

```text
pi.txt
historial.csv
```

El programa no fa un `git push` després de cada mesura.

El push es fa aproximadament cada 5 minuts.

El procés és:

```text
Dada nova
   |
   v
pi.txt
   |
   v
historial.csv
   |
   v
git add
   |
   v
git commit
   |
   v
git push
   |
   v
GitHub
```

Si un `git push` falla, el programa no s'atura. Continuarà fent mesures i tornarà a intentar publicar-les en el següent interval.

---

# Actualització automàtica de la web

La pàgina web comprova `pi.txt` i `historial.csv` cada 10 segons.

Això significa que no cal recarregar manualment la pàgina perquè apareguin noves dades.

El flux és:

```text
Raspberry Pi
     |
     | nova dada
     v
Fitxers locals
     |
     | cada 5 minuts
     v
GitHub
     |
     | comprovació cada 10 segons
     v
Web
```

Per tant, el temps màxim aproximat entre un `git push` i la detecció de la nova dada per la web és d'uns 10 segons.

Si el navegador està mostrant dades antigues després de modificar el codi de la web, es pot fer una recàrrega completa amb:

```text
Ctrl + Shift + R
```

---

# Gràfiques

Les gràfiques utilitzen les dades de:

```text
historial.csv
```

Hi ha tres gràfiques:

```text
Temperatura
Humitat
Sensació tèrmica
```

Els períodes disponibles són:

```text
1 hora
6 hores
24 hores
7 dies
Tot
```

---

# Separació de dades sense mesures

La web detecta automàticament quan hi ha un període llarg sense dades.

Actualment el límit és de:

```text
5 minuts
```

Per exemple:

```text
10:01  30 C
10:02  30 C
10:03  30 C
10:04  30 C
13:04  34 C
```

Entre `10:04` i `13:04` han passat més de 5 minuts.

La gràfica no connectarà aquests dos punts.

Es mostrarà aproximadament:

```text
30 ──────────        ───── 34
```

en lloc de:

```text
30 ─────────────────────── 34
```

Això evita crear línies incorrectes quan la Raspberry està apagada, perd connexió, el sensor deixa de funcionar o simplement no hi ha dades durant un període.


---

# Càlcul de la sensació tèrmica

La sensació tèrmica es calcula utilitzant temperatura i humitat relativa.

La fórmula utilitzada pel programa és:

```python
e = (humitat / 100) * 6.105 * math.exp(
    17.72 * temperatura / (237.7 + temperatura)
)

sensacio = temperatura + 0.33 * e - 4
```

El resultat es guarda amb dues xifres decimals.

---

# GitHub Pages

La pàgina web està pensada per funcionar amb GitHub Pages.

El repositori és:

```text
https://github.com/fustcoma/pi-weather
```

GitHub Pages utilitza:

```text
index.html
script.js
pi.txt
historial.csv
```

La pàgina web no necessita Python ni cap servidor propi.

Només necessita poder llegir els fitxers del repositori.

---

# Actualitzar el codi del projecte

Si es modifica `temperatura.py`, `script.js` o `index.html`, cal pujar els canvis a GitHub.

Des de l'ordinador:

```bash
git add .
git commit -m "Actualització del projecte"
git push
```

Després, si s'ha modificat `temperatura.py`, cal actualitzar també la còpia de la Raspberry Pi.

A la Raspberry:

```bash
cd ~/pi-weather
git pull
```

Després reiniciar el servei:

```bash
sudo systemctl restart estacio.service
```

Això és important perquè el servei que ja està funcionant continuarà utilitzant el programa anterior fins que es reiniciï.

---

# Actualitzar només el programa de la Raspberry

Si només s'ha modificat `temperatura.py`:

```bash
cd ~/tpi-weather
git pull
sudo systemctl restart estacio.service
```

Comprovar:

```bash
sudo systemctl status estacio.service
```

---

# Actualitzar el servei de systemd

Si es modifica:

```text
/etc/systemd/system/estacio.service
```

cal executar:

```bash
sudo systemctl daemon-reload
```

I després:

```bash
sudo systemctl restart estacio.service
```

Si també es vol assegurar que continua iniciant-se automàticament:

```bash
sudo systemctl enable estacio.service
```

---

# Historial de dades

`historial.csv` no s'ha de crear manualment.

Si no existeix, `temperatura.py` el crea automàticament.

A partir d'aquí, cada mesura s'afegeix al final del fitxer.

Per consultar-lo des de la Raspberry:

```bash
cat historial.csv
```

Per consultar només les últimes línies:

```bash
tail historial.csv
```

Per exemple:

```bash
tail -20 historial.csv
```

---

# Comprovar les dades actuals

Per veure el contingut de `pi.txt`:

```bash
cat pi.txt
```

Exemple:

```text
26.60
53.36
29.00
2.43
06/09/2026 22:50:29
```

---

# Logs del servei

El servei utilitza el sistema de logs de systemd.

Per veure els logs:

```bash
journalctl -u estacio.service
```

Per veure'ls en temps real:

```bash
journalctl -u estacio.service -f
```

Per veure les últimes 100 línies:

```bash
journalctl -u estacio.service -n 100
```

Per veure els logs des de l'últim arrencament:

```bash
journalctl -u estacio.service -b
```

---

# Guardar els logs després d'un reinici

Per poder investigar errors encara que la Raspberry Pi es reiniciï, es pot activar l'emmagatzematge persistent dels logs de systemd.

Crear la carpeta:

```bash
sudo mkdir -p /var/log/journal
```

Editar:

```bash
sudo nano /etc/systemd/journald.conf
```

Buscar:

```text
#Storage=auto
```

I canviar-ho per:

```text
Storage=persistent
```

Després reiniciar el servei de journald:

```bash
sudo systemctl restart systemd-journald
```

A partir d'aquest moment, els logs es conservaran entre reinicis.

---

# Investigar un reinici inesperat

Si la Raspberry Pi es reinicia inesperadament, primer es pot consultar l'arrencada anterior.

Veure els últims missatges de l'arrencada anterior:

```bash
journalctl -b -1 -e
```

Veure només avisos:

```bash
journalctl -b -1 -p warning
```

Buscar problemes d'alimentació o voltatge:

```bash
journalctl -b -1 | grep -i -E "under-voltage|voltage|throttl|power"
```

Buscar problemes de temperatura:

```bash
journalctl -b -1 | grep -i -E "thermal|temperature|overheat"
```

Veure avisos del kernel:

```bash
journalctl -b -1 -k -p warning
```

Veure les últimes 100 línies del kernel:

```bash
journalctl -b -1 -k | tail -100
```

També es pot comprovar l'estat de throttling:

```bash
vcgencmd get_throttled
```

I la temperatura actual:

```bash
vcgencmd measure_temp
```

La informació de l'arrencada anterior només estarà disponible si els logs persistents estaven activats abans del reinici.

---

# Apagar la Raspberry Pi

Si s'està connectat per SSH, la Raspberry Pi es pot apagar de manera segura amb:

```bash
sudo poweroff
```

També es pot utilitzar:

```bash
sudo shutdown -h now
```

És preferible apagar-la així abans de desconnectar l'alimentació físicament.

---

# Solució de problemes

## El DHT11 no funciona

Comprovar:

* DATA està connectat al GPIO 2.
* GPIO 2 correspon al pin físic 3.
* VCC està connectat a 3.3 V.
* GND està connectat correctament.
* Hi ha una resistència pull-up si el mòdul no la incorpora.

També comprovar que les llibreries estiguin instal·lades:

```bash
source ~/dht-env/bin/activate
pip list
```

---

## El servei no funciona

Executar:

```bash
sudo systemctl status estacio.service
```

Després:

```bash
journalctl -u estacio.service -n 100
```

Això normalment mostrarà l'error que impedeix iniciar `temperatura.py`.

---

## El programa funciona manualment però no amb systemd

Comprovar els camins del servei:

```ini
User=pi
WorkingDirectory=/home/pi/pi-weather
ExecStart=/home/pi/dht-env/bin/python /home/pi/pi-weather/temperatura.py
```

També comprovar que el fitxer existeixi:

```bash
ls ~/pi-weather/temperatura.py
```

I que existeixi el Python de l'entorn virtual:

```bash
ls ~/dht-env/bin/python
```

---

## Git no fa push

Comprovar:

```bash
cd ~/pi-weather
git status
```

Provar:

```bash
git push
```

Comprovar que Git recorda les credencials:

```bash
git config --global --get credential.helper
```

Hauria de mostrar:

```text
store
```

Si torna a demanar el token, cal tornar a autenticar Git amb el Personal Access Token.

---

## La web no mostra dades

Comprovar des de la Raspberry:

```bash
cat pi.txt
```

I:

```bash
cat historial.csv
```

Comprovar també que els canvis hagin arribat a GitHub:

```bash
git status
```

Si s'han fet canvis però encara no s'han publicat:

```bash
git add .
git commit -m "Actualització de dades"
git push
```

Si el problema és només la memòria cau del navegador:

```text
Ctrl + Shift + R
```

---

## La gràfica no s'actualitza

La Raspberry actualitza les dades aproximadament cada minut, però només les publica a GitHub cada 5 minuts.

Per tant, una dada nova pot tardar fins a uns 5 minuts a arribar a GitHub.

Una vegada publicada, `script.js` la comprova cada 10 segons.

Comprovar també que `historial.csv` contingui una nova línia:

```bash
tail historial.csv
```

---

## L'anemòmetre no detecta impulsos

Durant el muntatge es van provar connexions i programes de diagnòstic separats. Si no apareix cap impuls:

1. Comprova que el *reed switch* estigui connectat entre GPIO 8 (pin físic 24) i GND (per exemple, pin físic 20).
2. Assegura't que el programa utilitzi numeració BCM (`REED_PIN = 8`) i no el número físic del connector.
3. Apropa els imants al *reed switch* i gira el rotor a poc a poc. Els imants han de passar prou a prop del contacte i amb l'orientació adequada.
4. Comprova que els terminals del *reed switch* i els cables no estiguin trencats. Si tens un multímetre, utilitza el mode de continuïtat per veure si el contacte es tanca quan hi apropes un imant.
5. Prova primer el cable entre GPIO i GND. Si el programa detecta el canvi en tancar el circuit manualment però no quan gira l'anemòmetre, el problema probablement és mecànic o magnètic: posició dels imants, distància, orientació o contacte.
6. Executa `prova.py` abans de depurar el programa principal.

En les proves es va observar que tancar el circuit entre el GPIO i GND podia activar l'entrada, mentre que el conjunt d'imants i *reed switch* no sempre generava impulsos. Això ajuda a separar un problema de programari o de pin d'un problema de posicionament del sensor.

## `ModuleNotFoundError` en instal·lar o importar `gpiozero`

Durant les proves va aparèixer un error del tipus `ModuleNotFoundError` per a `gpiozero`, tot i que s'havia intentat instal·lar la llibreria. En aquests casos, el més important és assegurar-se que la instal·lació i l'execució utilitzen el mateix Python: activar `~/dht-env` abans d'instal·lar o executar res.

```bash
source ~/dht-env/bin/activate
python -m pip show gpiozero
python -c "import sys; print(sys.executable)"
```

Si `pip show` no troba el paquet, instal·la'l en aquest mateix entorn:

```bash
python -m pip install gpiozero
```

Després torna a executar `prova.py` des de l'entorn activat. Si l'error continua, comprova la ruta de Python mostrada per `sys.executable` i no barregis `pip` d'un Python amb l'executable d'un altre. Aquest problema és diferent d'un error de cablejat: un mòdul que no s'importa impedeix que el programa comenci, mentre que un sensor que no detecta impulsos requereix revisar el circuit i el muntatge.

## El programa mostra velocitats estranyes o zero

* Comprova que els imants passin pel *reed switch* una vegada per cada posició prevista pel disseny.
* Gira el rotor manualment i observa si el recompte d'impulsos canvia.
* Comprova que no hi hagi fregament excessiu al coixinet 608.
* Revisa el factor de conversió/calibratge emprat pel codi. Un valor de prova com `2.43 km/h` només confirma que el programa ha produït una lectura; no demostra per si sol que la velocitat sigui exacta.
* Evita interpretar zero com a prova definitiva que no hi ha vent: també pot indicar que el rotor no gira lliurement o que el *reed switch* no detecta els imants.

---

# Seguretat

No s'han de pujar mai al repositori:

* Personal Access Tokens.
* Contrasenyes.
* Claus privades.
* Credencials SSH.
* Altres secrets.

El token de GitHub està guardat localment a:

```text
~/.git-credentials
```

No s'ha de compartir aquest fitxer.

El token tampoc s'ha d'escriure dins de:

```text
temperatura.py
```

---

# Resum de la instal·lació

En una instal·lació nova, els passos principals són:

```bash
cd ~
git clone https://github.com/fustcoma/pi-weather.git
cd ~/pi-weather

python3 -m venv ~/dht-env
source ~/dht-env/bin/activate

pip install adafruit-blinka
pip install adafruit-circuitpython-dht

git config --global user.name "EL_TEU_USUARI"
git config --global user.email "EL_TEU_EMAIL"

git config --global credential.helper store

git push
```

Després crear:

```text
/etc/systemd/system/estacio.service
```

Amb:

```ini
[Unit]
Description=Estacio meteorologica DHT11
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pi-weather
ExecStart=/home/pi/dht-env/bin/python /home/pi/pi-weather/temperatura.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

I activar-lo:

```bash
sudo systemctl daemon-reload
sudo systemctl start estacio.service
sudo systemctl enable estacio.service
```

Comprovar:

```bash
sudo systemctl status estacio.service
```

A partir d'aquí, la Raspberry Pi pot funcionar de manera autònoma.

---

# Arquitectura final

```text
                    DHT11
                      |
                      v
              Raspberry Pi Zero W
                      |
                      v
               temperatura.py
                      |
             +--------+--------+
             |                 |
             v                 v
          pi.txt        historial.csv
             |                 |
             +--------+--------+
                      |
                      v
                     Git
                      |
                 cada 5 minuts
                      |
                      v
                   GitHub
                      |
                      v
                GitHub Pages
                      |
             +--------+--------+
             |                 |
             v                 v
         index.html       script.js
                               |
                               v
                         Chart.js
                               |
                    +----------+----------+
                    |          |          |
                    v          v          v
              Temperatura   Humitat   Sensació
```

El servei `estacio.service` fa que tot el sistema de mesura s'iniciï automàticament quan la Raspberry Pi s'encén, mentre que GitHub Pages permet consultar les dades des de qualsevol dispositiu amb accés a Internet.

## Llicència

Aquest projecte està publicat sota la **llicència MIT**.

## Autor

Creat per **fustcoma**.

Anemòmetre creat per [**alf45tar**](https://github.com/alf45tar/Anemometer)