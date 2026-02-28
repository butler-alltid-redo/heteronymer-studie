# Heteronymer / homografer med olika uttal

Det här projektet är till för att studera **ord som stavas likadant men kan uttalas olika** beroende på betydelse (på engelska ofta *heteronyms*). På svenska hamnar det ofta under **homografer**, och när uttalet skiljer sig pratar man ibland om **heteronymer**.

Målet här är praktiskt: en liten, växande datamängd + Python-skript som gör **snygga plottar/figurer** över uttalsvarianter.

## Struktur

- `data/heteronyms_sv.csv` – exempeldata (svenska, fokus)
- `scripts/make_plots.py` – genererar figurer till `figures/`

## Kom igång

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python scripts/make_plots.py
```

Figurer sparas i `figures/`.

## Dataformat

CSV-kolumner:

- `language` – t.ex. `sv`
- `word` – stavning
- `sense_id` – intern id för betydelse/variant
- `pos` – ordklass (valfritt)
- `meaning` – kort betydelse
- `ipa` – uttal i IPA (så gott det går)
- `notes` – valfritt

## Nästa steg (om du vill)

- Lägga till fler ord + källhänvisningar
- (Valfritt) Stöd för fler språk senare
- En liten webbsida/Streamlit-app för att filtrera och lyssna på TTS
