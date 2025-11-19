# Guida alla Migrazione: Separazione del Repository Gauge

Questa guida descrive i passi per separare la cartella `gauge` in un repository GitHub separato.

## Prerequisiti

- Accesso all'organizzazione GitHub IMPACT
- Git configurato con le credenziali appropriate
- Python 3.10+ installato

## Passi per Creare il Nuovo Repository

### 1. Creare il Repository su GitHub

1. Vai su GitHub nell'organizzazione IMPACT
2. Crea un nuovo repository chiamato `stocav-gauge`
3. Non inizializzare con README, .gitignore o licenza (abbiamo già questi file)

### 2. Preparare la Cartella Gauge

La cartella `dashboard_redis/gauge` è già configurata come pacchetto Python installabile con:

- `pyproject.toml` - Configurazione del pacchetto
- `MANIFEST.in` - File da includere nella distribuzione
- `.gitignore` - File da ignorare
- `README.md` - Documentazione aggiornata
- `__init__.py` - Esporta sia `GaugeSVGFull` che `Gauge` (alias)

### 3. Inizializzare il Repository Git nella Cartella Gauge

```bash
cd dashboard_redis/gauge
git init
git add .
git commit -m "Initial commit: StoCAV Gauge package"
```

### 4. Collegare al Repository Remoto

```bash
git remote add origin https://github.com/IMPACT/stocav-gauge.git
git branch -M main
git push -u origin main
```

## Aggiornare il Repository Principale

### Opzione A: Usare il Pacchetto Installato (Consigliato)

1. Nel repository principale, aggiungere la dipendenza nel file `requirements.txt` o `pyproject.toml`:

```txt
# requirements.txt
git+https://github.com/IMPACT/stocav-gauge.git@main#egg=stocav-gauge
```

Oppure in `pyproject.toml`:

```toml
[project]
dependencies = [
    "stocav-gauge @ git+https://github.com/IMPACT/stocav-gauge.git@main",
]
```

2. Installare il pacchetto:

```bash
pip install -e .  # se usi pyproject.toml
# oppure
pip install -r requirements.txt
```

3. Rimuovere la cartella `dashboard_redis/gauge` dal repository principale:

```bash
cd dashboard_redis
git rm -r gauge
git commit -m "Remove gauge module - now installed as separate package"
```

4. L'import nel codice rimane invariato:

```python
from gauge import Gauge  # Funziona ancora!
```

### Opzione B: Usare Git Submodule

Se preferisci mantenere il codice nel repository principale come riferimento:

```bash
cd dashboard_redis
git rm -r gauge
git submodule add https://github.com/IMPACT/stocav-gauge.git gauge
git commit -m "Convert gauge to git submodule"
```

**Nota**: Con i submodule, devi ricordare di inizializzare e aggiornare:

```bash
git submodule update --init --recursive
```

## Verifica

Dopo la migrazione, verifica che tutto funzioni:

1. Installare il pacchetto gauge
2. Eseguire i test del dashboard principale
3. Verificare che i gauge vengano visualizzati correttamente

## Sviluppo Futuro

Per sviluppare il pacchetto gauge:

1. Clonare il repository separato:

```bash
git clone https://github.com/IMPACT/stocav-gauge.git
cd stocav-gauge
```

2. Installare in modalità sviluppo:

```bash
pip install -e .
```

3. Fare modifiche e testare localmente
4. Commit e push al repository gauge
5. Nel repository principale, aggiornare la versione se necessario

## Note Importanti

- Il pacchetto è configurato per essere installabile direttamente da GitHub
- Gli assets (PNG) sono inclusi nel pacchetto tramite `MANIFEST.in`
- L'alias `Gauge = GaugeSVGFull` mantiene la compatibilità con il codice esistente
- Il nome del pacchetto è `stocav-gauge` ma il modulo si importa come `gauge`

