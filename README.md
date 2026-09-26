### Werner SCS Cloud ###
Das Projekt ist die Cloud-Erweiterung für einen bestehenden Windows-SCS-Konverter.
Der ursprüngliche Konverter war schon vorhanden. Ich habe dazu eine zentrale Control API und die Cloud-Infrastruktur aufgebaut, damit Benutzer, Lizenzen und Programmversionen nicht mehr lokal über einzelne Lizenzdateien verwaltet werden müssen.
Was das System macht
Der Nutzer kann sich direkt im SCS-Konverter ein Konto anlegen und sich danach mit E-Mail und Passwort anmelden.
Ein Konto enthält unter anderem:
- Name
- E-Mail
- Passwort
- MND
Das Konto wird in PostgreSQL gespeichert. Über eine Admin-Oberfläche kann anschließend eine Lizenz für den Nutzer angelegt werden.
Wenn eine gültige Lizenz vorhanden ist, kann sich der Nutzer einloggen und der SCS-Konverter startet normal.
Architektur
SCS-Konverter.exe
        |
        | HTTPS
        v
api.scs-konverter.de
        |
        v
      Caddy
        |
        v
     FastAPI
        |
        v
   PostgreSQL
Die Control API läuft auf einem AWS-Lightsail-Server in Docker.
Control API
Die Control API ist mit FastAPI gebaut und übernimmt unter anderem:
- Benutzerverwaltung
- Login
- Passwortprüfung
- JWT-Authentifizierung
- Lizenzprüfung
- Adminrechte
- MND-Zuordnung
- Releaseverwaltung
- Abrufen der aktuell freigegebenen Programmversion
Der SCS-Konverter greift nicht direkt auf PostgreSQL zu, sondern kommuniziert nur über die API.
Datenbank
Als Datenbank wird PostgreSQL verwendet.
Die wichtigsten Tabellen sind aktuell:
users
Speichert die Benutzerkonten.
Beispiele für Felder:
id
name
email
hashed_password
admin
mnd
lizenzen
Speichert die Lizenzen der Benutzer.
id
user_id
valid_from
valid_until
active
created_at
releases
Speichert die Informationen zu verfügbaren Versionen des SCS-Konverters.
version
release_date
size
location
checksum
active
Datenbankänderungen werden mit Alembic verwaltet.
Login und Lizenzen
Beim Login schickt der SCS-Konverter E-Mail und Passwort an die Control API.
Die API prüft:
1. Gibt es den Benutzer?
2. Ist das Passwort korrekt?
3. Gibt es eine gültige Lizenz?
Wenn alles passt, bekommt der Client ein JWT zurück.
Mit diesem Token können anschließend geschützte Endpunkte aufgerufen werden, zum Beispiel für die Benutzerdaten.
Die MND wird ebenfalls aus der Datenbank geladen und muss deshalb nicht mehr über eine lokale Lizenzdatei gespeichert werden.
Updates
Der SCS-Konverter kann automatisch prüfen, ob eine neue Version vorhanden ist.
Der Ablauf sieht ungefähr so aus:
SCS-Konverter startet
        |
        v
aktuelle Version über API abrufen
        |
        v
neue Version vorhanden?
        |
        v
neue EXE herunterladen
        |
        v
Dateigröße + SHA-256 prüfen
        |
        v
updater.exe starten
        |
        v
alte EXE beenden und ersetzen
        |
        v
neue Version starten
Der Kunde braucht dadurch neue Versionen nicht mehr manuell auszutauschen.
S3 und CloudFront
Die Release-Dateien liegen in einem privaten AWS-S3-Bucket.
Der Bucket selbst ist nicht öffentlich erreichbar.
Für die Downloads wird CloudFront verwendet:
SCS-Konverter
      |
      v
CloudFront
      |
      v
privater S3-Bucket
Die Control API liefert dem Client die Download-URL, Dateigröße und SHA-256-Prüfsumme des aktuell aktiven Releases.
Admin-Oberfläche
Zusätzlich gibt es eine Admin-Webseite.
Darüber können unter anderem:
- Benutzer angesehen werden
- Lizenzen verwaltet werden
- Releases angelegt und aktiviert werden
Die Oberfläche läuft unter:
https://admin.scs-konverter.de
Das Frontend besteht aus HTML, CSS und JavaScript und verwendet die bestehende Control API.
Die eigentliche Prüfung der Adminrechte passiert immer im Backend.
Deployment
Das Backend läuft aktuell auf AWS Lightsail mit Ubuntu.
Verwendet werden:
- Docker
- Docker Compose
- FastAPI
- PostgreSQL
- Caddy
- AWS S3
- AWS CloudFront
Die grobe Struktur ist:
AWS Lightsail
|
+-- Caddy
|
+-- Docker
    |
    +-- control_api
    |
    +-- db-scs
PostgreSQL ist nicht direkt aus dem Internet erreichbar.
Die API läuft intern auf Port 8000. Caddy nimmt HTTPS-Anfragen auf Port 443 entgegen und leitet sie an FastAPI weiter.
HTTPS und Domain
Die API ist über
https://api.scs-konverter.de
erreichbar.
Die Domain zeigt per DNS auf die statische IP des Lightsail-Servers.
Caddy kümmert sich um:
- HTTPS
- TLS-Zertifikate
- automatische Zertifikatserneuerung
- Reverse Proxy zur Control API
Secrets
Passwörter und andere Secrets werden nicht im Git-Repository gespeichert.
Auf dem Server werden Environment Variables verwendet, zum Beispiel:
POSTGRES_PW=...
JWT_SECRET=...
Diese Werte werden über Docker Compose an die Container weitergegeben.
Starten
Backend bauen und starten:
docker compose up -d --build
Container prüfen:
docker compose ps
Logs der API ansehen:
docker compose logs -f control_api
Datenbankmigrationen ausführen:
docker compose exec control_api /app/.venv/bin/alembic upgrade head
Aktueller Stand
Der komplette Ablauf funktioniert aktuell:
Konto anlegen
-> Lizenz vergeben
-> einloggen
-> MND laden
-> SCS-Konverter starten
-> nach Updates suchen
-> neue Version herunterladen
-> Update automatisch installieren
Außerdem laufen aktuell:
- Control API auf AWS
- PostgreSQL
- Docker Deployment
- eigene Domain
- HTTPS
- Caddy Reverse Proxy
- S3 für Releases
- CloudFront für Downloads
- Admin-Webseite
Noch geplant
Als Nächstes sollen vor allem Betriebs- und DevOps-Themen verbessert werden:
- Monitoring
- automatische Backups
- Alerts bei Ausfällen
- bessere Logs / Observability
- CI/CD
- später eventuell Infrastructure as Code
Verwendete Technologien
- Python
- FastAPI
- PostgreSQL
- Alembic
- JWT
- Docker
- Docker Compose
- Ubuntu
- Caddy
- AWS Lightsail
- AWS S3
- AWS CloudFront
- Git / GitHub
- HTML / CSS / JavaScript
