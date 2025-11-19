# NiceGUI Gauge - SVG Gauge Widget

Pacchetto Python per gauges grafici SVG completi programmati in Python/NiceGUI. Implementazione Python-only senza dipendenze JavaScript.

## Installazione

### Da GitHub (Repository Separato)

```bash
pip install git+https://github.com/IMPACT-UnivAQ/nicegui-gauge.git
```

### Da Repository Locale (Sviluppo)

```bash
pip install -e /path/to/nicegui-gauge
```

Oppure, se sei nella directory del pacchetto:

```bash
pip install -e .
```

## Utilizzo

Dopo l'installazione, puoi importare il modulo:

```python
from gauge import GaugeSVGFull, Gauge

# GaugeSVGFull è la classe principale
gauge = GaugeSVGFull(
    value=50,
    min_value=0,
    max_value=100,
    label='Speed',
    gauge_type='circular'
)

# Gauge è un alias di GaugeSVGFull per compatibilità
gauge = Gauge(
    value=50,
    min_value=0,
    max_value=100,
    label='Speed'
)
```

## Struttura

- `gauge_svg_full.py` - Implementazione classe GaugeSVGFull
- `assets/` - Risorse grafiche (PNG di sfondo, SVG ago)
- `test_apps/` - Minigui di test per raffinare la qualità

## Sviluppo e Test

### Test Locale

```bash
cd gauge
python test_apps/test_speed_gauge.py
```

### Test con Docker

```bash
cd gauge
docker-compose up
```

Accesso: http://localhost:8080

## Sviluppo Iterativo

1. Modificare `gauge_svg_full.py` per migliorare implementazione
2. Testare con minigui in `test_apps/`
3. Raffinare qualità visiva e performance
4. Integrare in dashboard principale quando pronto

## Pubblicazione

Per pubblicare il pacchetto:

```bash
# Build del pacchetto
python -m build

# Pubblicazione su PyPI (se configurato)
twine upload dist/*
```

