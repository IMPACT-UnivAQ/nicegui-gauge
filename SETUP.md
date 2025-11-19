# Setup Guide - Gauge Test Environment

## Struttura Completata

```
gauge/
├── __init__.py                    # Module initialization
├── gauge_svg_full.py              # Implementazione Soluzione 4
├── generate_backgrounds.py        # Script per generare PNG di sfondo
├── assets/                        # Risorse grafiche
│   ├── gauge_background_speed.png
│   └── gauge_background_heading.png
├── test_apps/                     # Minigui di test
│   ├── test_speed_gauge.py        # Test gauge velocità
│   ├── test_heading_gauge.py      # Test gauge heading
│   └── test_both_gauges.py        # Test entrambi i gauges
├── docker-compose.yml             # Docker compose per test
├── Dockerfile                     # Dockerfile minimale
├── requirements.txt               # Dipendenze
├── README.md                      # Documentazione
└── SETUP.md                       # Questa guida
```

## Utilizzo

### Test Locale (senza Docker)

```bash
cd dashboard_redis/gauge

# Installa dipendenze
pip install -r requirements.txt

# Genera background PNG (opzionale, richiede Pillow)
python3 generate_backgrounds.py

# Esegui test applicazioni
python3 test_apps/test_speed_gauge.py
# oppure
python3 test_apps/test_heading_gauge.py
# oppure
python3 test_apps/test_both_gauges.py
```

Accesso: http://localhost:8080

### Test con Docker

```bash
cd dashboard_redis/gauge

# Build e avvia container
docker-compose up --build

# Per testare applicazioni diverse, modifica il comando in docker-compose.yml
# oppure esegui direttamente:
docker-compose run gauge-test python3 test_apps/test_heading_gauge.py
docker-compose run gauge-test python3 test_apps/test_both_gauges.py
```

Accesso: http://localhost:8080

## Funzionalità Implementate

### Classe GaugeSVGFull

- [X] Generazione SVG completo in Python
- [X] Supporto PNG di sfondo (base64 inline)
- [X] Rotazione ago tramite SVG transform
- [X] Supporto gauge circolare (360 gradi) e semicircolare (180 gradi)
- [X] Tick marks e numeri configurabili
- [X] Display valore numerico
- [X] Aggiornamento efficiente del valore

### Minigui di Test

1. **test_speed_gauge.py**
   - Gauge velocità isolato (0-100 km/h)
   - Slider e input manuale
   - Auto-update simulation
   - Controlli per test parametri

2. **test_heading_gauge.py**
   - Gauge heading isolato (0-360 gradi)
   - Slider e input manuale
   - Rotazione continua
   - Test animazione fluida

3. **test_both_gauges.py**
   - Entrambi i gauges affiancati
   - Simulazione dati EGO sincronizzati
   - Controlli separati per speed e heading

## Prossimi Passi

1. **Raffinamento Visuale**
   - Migliorare qualità PNG di sfondo
   - Ottimizzare forma/stile ago
   - Aggiungere colori per zone (come gauge originale)

2. **Ottimizzazione Performance**
   - Test con aggiornamenti frequenti (10Hz+)
   - Minimizzare ricreazione SVG
   - Confronto prestazioni

3. **Integrazione Dashboard**
   - Adattare interfaccia per compatibilità con dashboard.py
   - Integrare in _create_ego_panel()
   - Test end-to-end con dati Redis reali

## Note

- I PNG di sfondo vengono generati automaticamente se Pillow è disponibile
- Se Pillow non è disponibile, i gauges funzionano comunque senza background
- Il gauge funziona completamente senza JavaScript (solo SVG/CSS)
- L'aggiornamento del valore usa JavaScript minimale solo per aggiornare l'attributo transform

