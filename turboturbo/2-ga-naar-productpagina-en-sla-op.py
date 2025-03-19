import os
import sys
import time
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException

# Forceer UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Bepaal logmap en maak deze aan
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)

# Logbestand aanmaken met timestamp
log_filename = os.path.join(log_dir, f"script2_log_{time.strftime('%Y%m%d_%H%M%S')}.log")

def log_message(message):
    """ Logt een bericht met timestamp naar het logbestand en de console """
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(log_filename, "a", encoding="utf-8") as log_file:
        log_file.write(full_message + "\n")

def kopieer_foutmelding(foutmelding, root):
    """ Kopieert de foutmelding naar het klembord """
    root.clipboard_clear()
    root.clipboard_append(foutmelding)
    root.update()
    messagebox.showinfo("Gekopieerd!", "Foutmelding gekopieerd naar klembord.")

def open_logbestand():
    """ Opent het logbestand in Kladblok """
    os.system(f'notepad.exe "{log_filename}"')

def show_error_popup(error_message):
    """ Toont een foutmelding in een pop-up en stopt het script zonder vast te lopen """
    root = tk.Tk()
    root.withdraw()  # Verberg het hoofdvenster

    popup = tk.Toplevel(root)
    popup.geometry("400x200")
    popup.title("❌ Foutmelding")

    tk.Label(popup, text="Er is een fout opgetreden:", font=("Arial", 10, "bold")).pack(pady=5)
    text_box = tk.Text(popup, height=4, wrap="word")
    text_box.insert("1.0", error_message)
    text_box.config(state="disabled")
    text_box.pack(pady=5)

    tk.Button(popup, text="📋 Kopiëren", command=lambda: kopieer_foutmelding(error_message, root)).pack(side="left", padx=10)
    tk.Button(popup, text="📖 Log openen", command=open_logbestand).pack(side="left", padx=10)
    tk.Button(popup, text="❌ OK en Sluiten", command=lambda: safe_exit(popup)).pack(side="right", padx=10)

    popup.protocol("WM_DELETE_WINDOW", lambda: safe_exit(popup))
    popup.after(100, lambda: popup.focus_force())

    popup.mainloop()

def safe_exit(popup):
    """ Sluit de popup en beëindigt het script correct zonder vast te lopen """
    popup.destroy()
    log_message("🚨 EJECT EJECT EJECT! Net als die keer op Hoth, evacuatie in volle gang! | Script wordt afgesloten na foutmelding.")  
    root = tk.Tk()
    root.withdraw()
    root.quit()
    sys.exit(1)

def init_driver():
    """ Initialiseer en verbind met een bestaande Chrome-sessie """
    options = Options()
    options.debugger_address = "localhost:9222"
    driver = webdriver.Chrome(options=options)
    return driver

def vul_veld(veld_naam, waarde):
    """ Probeert een invoerveld in te vullen en stopt direct bij een fout. """
    try:
        log_message(f"🔧 Hyper-quantumregisters gekalibreerd met 89% nauwkeurigheid. Ontwijken van interstellaire stofdeeltjes... | Wachten op element: '{veld_naam}'")
        input_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, veld_naam)))
        
        log_message(f"🧹 Purgeringssequentie geactiveerd. Zoals ze in Mos Eisley zeggen, je moet eerst opruimen! | Veld '{veld_naam}' wordt leeggemaakt")
        input_field.clear()

        log_message(f"✍️ Invoersnelheid over de 350 parsecs per minuut. Informatie wordt sneller getransporteerd dan licht... | Vullen van '{veld_naam}' met waarde '{waarde}'")
        input_field.send_keys(str(waarde))

        log_message(f"✅ Missie geslaagd met een waarschijnlijkheid van 99,9%! Ik zou zeggen, 'dat ging lekker soepel', als ik menselijke emoties kon ervaren... | '{veld_naam}' succesvol ingevuld met '{waarde}'")

    except NoSuchElementException as e:
        foutmelding = f"⚠️ Houston, we hebben een probleem! Element niet gevonden in deze sector van het universum! | Veld '{veld_naam}' niet gevonden: {e}"
        log_message(foutmelding)
        show_error_popup(foutmelding)
    except TimeoutException as e:
        foutmelding = f"⚠️ Tijddilatatie gedetecteerd! Zelfs met warpsnelheid duurt het te lang! | Timeout bij het zoeken naar veld '{veld_naam}': {e}"
        log_message(foutmelding)
        show_error_popup(foutmelding)
    except Exception as e:
        foutmelding = f"⚠️ CATASTROPHIC SYSTEM FAILURE! Waarschijnlijkheid van succes gedaald naar 0.0001%! | Kritieke fout bij veld '{veld_naam}': {e}"
        log_message(foutmelding)
        show_error_popup(foutmelding)

def klik_opslaan_knop():
    """Vereenvoudigde functie om de opslaan knop te vinden en klikken"""
    log_message("💾 Initieer de hypersprong naar de opslag-nexus! Coördinaten ingesteld, hypermatter-reactor op 85%... | Op zoek naar de opslaan knop")
    
    try:
        log_message("🔍 Scanners op maximale gevoeligheid. Het zoeken naar de knoppen is zoals een naald in een kosmische hooiberg! | Zoeken naar opslaan knop via XPath")
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Product opslaan')]"))
        )
        
        # Scrollen naar de knop
        log_message("⬇️ Trekstralen geactiveerd! Trekken objecten in zichtsveld met 300% efficiëntie... | Scrollen naar de opslaanknop")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        time.sleep(1)
        
        # Knop klikken
        log_message("👆 Precisie-targeting-systemen online. Druk op de grote rode knop over 3...2...1... | Klikken op de opslaanknop")
        button.click()
        log_message("✅ 'Ik heb een goed gevoel hierover!' - knop met warpfactor 9 ingedrukt! | Knop succesvol geklikt")
        return True
            
    except Exception as e:
        foutmelding = f"💥 ALARMBELLEN RINKELEN! We zijn geraakt door een meteorieten-storm! | Kon de opslaan knop niet vinden of klikken: {e}"
        log_message(foutmelding)
        show_error_popup(foutmelding)
        return False

# Functie om de productrij op basis van index te halen
def get_product_by_index(index):
    """Haalt de productrij op basis van de meegegeven index"""
    excel_bestand = os.path.join(os.path.dirname(os.path.abspath(__file__)), "products2import.xlsx")
    df = pd.read_excel(excel_bestand)
    if index >= len(df):
        raise ValueError(f"⚠️ Index {index} is buiten bereik. Aantal producten: {len(df)}")
    return df.iloc[int(index)]

# Start van de hoofdcode
if __name__ == "__main__":
    try:
        # Controleer of er een command line argument is opgegeven
        if len(sys.argv) < 2:
            raise ValueError("⚠️ Geen productindex opgegeven. Gebruik: python script2.py [index]")
        
        product_index = int(sys.argv[1])
        log_message(f"🔢 Coördinaten ingesteld op product index {product_index}. Targeting systemen online... | Verwerken van product {product_index}")
        
        # Browser starten en verbinden
        driver = init_driver()
        log_message("🚀 Hoofdmotor ontstoken! We vliegen met een snelheid van 1.21 gigawatt! | Chrome WebDriver gestart")

        # Navigeren naar de productpagina
        log_message("➕ Koers gezet naar de Outer Rim, sectoren 7-G. ETA: 12 parsecs... | Navigeren naar producttoevoegpagina")
        driver.get("http://metroeventsdc.rentpro5.nl/Product/Edit")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        log_message("🆕 'Dit is waar de pret begint!' We hebben het doel bereikt zonder één schrammetje! | Pagina voor nieuw product is geopend")

        # Product uit Excel halen op basis van index
        product_data = get_product_by_index(product_index)
        log_message(f"📋 Dossier {product_index} opgehaald van de codebanken van Scarif! | Product data geladen: {product_data['Producttitel categoriepagina en winkelwagen']}")
        
        # Vereiste kolommen controleren
        vereiste_kolommen = ["Product_Title", "Product_UrlName"]
        for kolom in vereiste_kolommen:
            if kolom not in product_data or pd.isna(product_data[kolom]) or str(product_data[kolom]).strip() == "":
                raise ValueError(f"⚠️ De leegte van het universum is hier! Een zwart gat in onze data! | Lege of ontbrekende waarde gedetecteerd in '{kolom}'")
        
        log_message(f"✅ 'Er is een 97.6% kans dat deze data correct is.' Alle systemen op groen! | Productgegevens gevalideerd")

        # Velden invullen
        log_message("⚙️ Kwantumprocessor werkt op 110% van capaciteit. Gegevensoverdracht begint in T-minus 3, 2, 1... | Starten met het invullen van velden")
        vul_veld("Product_Name", product_data["Producttitel categoriepagina en winkelwagen"])
        vul_veld("Product_Title", product_data["Product_Title"])
        vul_veld("Product_UrlName", product_data["Product_UrlName"])

        # Product opslaan
        log_message("💾 'Het is tijd voor het Grote Moment!' Alle schakels in de kwantumketen worden gesynchroniseerd... | Product wordt opgeslagen")
        if klik_opslaan_knop():
            log_message("✅ 'Raak! Dat was een schot in de roos!' | Product opslaan actie uitgevoerd")

            # Wacht tot de pagina volledig geladen is
            log_message("⏳ 'Geduld, jonge Padawan.' De tijdmatrix herkalibreeert... | Wachten tot de pagina is geladen")
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Controleer of de tekst "S1521N" ergens op de pagina staat
            if "S1521N" in driver.page_source:
                log_message("✅ WE DID IT! WE DID IT! IT'S ALIIIIIVE! 'Ik sta altijd op 90% humorsetting en nu zit ik op 100%!' | 'S1521N' gevonden, product succesvol opgeslagen")
            else:
                log_message("⚠️ 'Ik heb hier een slecht gevoel over...' Waar is onze kostbare lading gebleven? | De tekst 'S1521N' is niet gevonden")
                show_error_popup("⚠️ De verwachte tekst 'S1521N' is niet gevonden na het opslaan van het product.")

        # Succesvol afronden
        log_message("🎉 'Dit was je finest hour!' Missie geslaagd en wachten op volgende orders... | Product verwerkt. Terugkoppeling naar hoofdscript.")
        print("✅ Product verwerkt. Terug naar hoofdscript voor volgende product.")
        sys.exit(0)  # Succesvol afsluiten met code 0

    except Exception as e:
        foutmelding = f"💥 KRITIEK ALARM! ALLE MOTOREN UITGEVALLEN! ONMIDDELLIJKE EVACUATIE VEREIST! | FATALE FOUT: {e}"
        log_message(foutmelding)
        show_error_popup(foutmelding)
        sys.exit(1)  # Afsluiten met foutcode 1

log_message("🚀 Missie voltooid! Terug naar de basis. BWAAAAAAAAAAAAAAAPPPP | Script uitgevoerd en voltooid")