# SELVALUCE DX - versione grafica modulare

Questa versione separa logica, grafica, mappa e battaglie in file diversi. È pensata per una resa da RPG portatile pixel-art di fine anni 2000, mantenendo però personaggi, creature e asset originali.

## Avvio

```powershell
cd "C:\Users\andrea.calgaro\OneDrive - LEGOR GROUP SPA\Desktop\gioco"
py main.py
```

Oppure fai doppio clic su `AVVIA_WINDOWS.bat`.

## File

- `main.py` - avvio
- `game.py` - loop, input, stati, salvataggio
- `battle.py` - combattimenti e cattura
- `world.py` - mappa, collisioni e NPC
- `assets.py` - loader PNG + grafica procedurale di fallback
- `models.py` - creature, particelle, NPC
- `data.py` - specie, mosse, allenatori e tipi
- `settings.py` - risoluzione, palette e percorsi

## Comandi

Mappa: WASD/frecce, E/Invio interagisci, Q squadra, P pozione, H aiuto, F5 salva, F11 fullscreen.

Battaglia: 1-4 mosse, C cattura, B zaino, Q squadra, F fuga.

## Asset veri

Vedi `assets/README.txt`. Il gioco parte anche senza asset esterni. Quando inserisci un PNG con il nome previsto, il loader lo preferisce automaticamente alla grafica generata da codice.
