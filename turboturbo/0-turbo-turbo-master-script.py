"""
Script 0 - Hoofdscript voor het importeren van producten

Beschrijving:
Dit script voert het volledige importproces uit:
1. Het start script 1 (1navigeer-naar-productlijst.py) slechts één keer.
   - Dit script opent RentPro, logt in en navigeert naar de productlijstpagina.
   - Zodra script 1 succesvol is voltooid, wordt teruggekoppeld naar dit script.
2. Daarna worden de productgegevens uit een Excel-bestand ingelezen.
3. Voor elke gevulde rij in de Excel wordt script 2 (2-ga-naar-productpagina-en-sla-op.py) aangeroepen.
   - Dit script verwerkt de gegevens van één product.
   - Na elke succesvolle uitvoering van script 2 wordt gecontroleerd of er nog meer producten zijn.
4. Zodra alle producten zijn verwerkt, eindigt het script.

Aanvullende informatie:
- Alle logberichten worden weggeschreven in een logbestand in de map 'logs'.
- Bij een foutmelding stopt het script en wordt een pop-up getoond met de foutdetails en opties om de foutmelding te kopiëren of het logbestand te openen.
- Foutmeldingen zorgen ervoor dat het script onmiddellijk stopt en de laatste logregel wordt weergegeven in de pop-up.
- **Alle tekst wordt nu in UTF-8 verwerkt om encoding-fouten te voorkomen.**

"""

import subprocess
import pandas as pd
import os
import sys
import datetime
from tkinter import messagebox

# ✅ Forceer UTF-8 encoding voor standaarduitvoer en standaardfout
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# Bepaal de directory van het huidige script
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, "logs")
os.makedirs(log_dir, exist_ok=True)  # Maak de logs-map als deze nog niet bestaat

# Logbestand aanmaken met timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(log_dir, f"product_import_{timestamp}.log")

# Variabele om de laatste foutregel op te slaan
laatste_foutmelding = None

def log_message(message, is_error=False):
    """ Schrijft naar console en logbestand, toont pop-up bij fouten. """
    global laatste_foutmelding
    timestamped_message = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    
    print(timestamped_message)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(timestamped_message + "\n")

    if is_error:
        laatste_foutmelding = message
        toon_fout_popup(timestamped_message)
        exit(1)

def toon_fout_popup(bericht):
    """ Toont een pop-up met de laatste foutmelding. """
    messagebox.showerror("❌ Foutmelding", bericht)

def run_script(script_path, *args):
    """ Voert een extern script uit en logt de output. """
    script_name = os.path.basename(script_path)
    log_message(f"🚀 Initiatie van subroutine: {script_name} met parameters: {args}")

    try:
        result = subprocess.run(
            [sys.executable, script_path, *args],
            text=True,
            check=True,
            encoding="utf-8",
            capture_output=False  # ✅ Nu zie je de foutmeldingen direct!
        )
        log_message(f"✅ {script_name} succesvol voltooid! Statuscode: {result.returncode}")
        if result.stdout:
            log_message(f"📜 Output ontvangen van {script_name}:\n{result.stdout.strip()}")
        if result.stderr:
            log_message(f"⚠️ Waarschuwing van {script_name}:\n{result.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        log_message(f"❌ Storing gedetecteerd in {script_name}! Foutcode: {e.returncode}\n{e.stderr}", is_error=True)

def verwerk_producten(df):
    """ Verwerkt elk product uit de Excel-lijst door script 2 aan te roepen. """
    log_message("📊 Verwerking gestart: producten worden verwerkt...")
    
    for index, row in df.iterrows():
        product_naam = row['Producttitel categoriepagina en winkelwagen']
        if not isinstance(product_naam, str) or product_naam.strip() == "":
            log_message(f"⚠️ Rij {index + 1} is leeg. Overslaan en doorgaan!")
            continue

        log_message(f"🚀 Verwerken product {index + 1}: '{product_naam}'...")
        script_path = os.path.join(script_dir, "2-ga-naar-productpagina-en-sla-op.py")
        log_message(f"🔍 Start script 2 voor product {index + 1} ({product_naam})...")
        run_script(script_path, str(index))
    
    log_message("🏁 Alle producten verwerkt!")

if __name__ == "__main__":
    log_message("🔑 Toegangsprotocol geactiveerd. Inlogproces gestart...")
    
    script1_path = os.path.join(script_dir, "1navigeer-naar-productlijst.py")
    run_script(script1_path)  # Script 1 wordt slechts één keer uitgevoerd

    try:
        df = pd.read_excel(os.path.join(script_dir, "products2import.xlsx"))
        df = df.dropna(subset=['Producttitel categoriepagina en winkelwagen'])
        if df.empty:
            log_message("⚠️ Geen producten om te verwerken. Script wordt beëindigd.")
            exit(0)
    except Exception as e:
        log_message(f"❌ Fout bij inlezen Excel: {e}", is_error=True)
    
    verwerk_producten(df)
    log_message("🎉 Operatie voltooid! Alle producten geïmporteerd. Moge de snelheid met je zijn! 🏎️✨")
