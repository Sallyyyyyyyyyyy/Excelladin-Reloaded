import sys
import os
import time
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Forceer UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# Bepaal de directory van het huidige script en de logmap
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

# Logbestand aanmaken met timestamp
log_filename = os.path.join(log_dir, f"script1_log_{time.strftime('%Y%m%d_%H%M%S')}.log")

def log_message(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(log_filename, "a", encoding="utf-8") as log_file:
        log_file.write(full_message + "\n")

def kopieer_foutmelding(foutmelding, root):
    """ Kopieert de foutmelding naar het klembord zonder pyperclip. """
    root.clipboard_clear()
    root.clipboard_append(foutmelding)
    root.update()
    messagebox.showinfo("Gekopieerd!", "Foutmelding gekopieerd naar klembord.")

def open_logbestand():
    """ Opent het logbestand in Kladblok. """
    os.system(f'notepad.exe "{log_filename}"')

def show_error_popup(error_message):
    """ Toont een foutmelding met kopieer- en log-open opties. """
    root = tk.Tk()
    root.withdraw()
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
    tk.Button(popup, text="❌ OK en Sluiten", command=popup.destroy).pack(side="right", padx=10)
    
    popup.mainloop()
    sys.exit(1)

# Chrome-opties instellen
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-web-security")
options.add_argument("--allow-running-insecure-content")
options.add_argument("--window-size=1600,1000")
options.add_experimental_option("detach", True)  # ✅ Chrome blijft open
options.add_argument("--remote-debugging-port=9222")  # ✅ Nodig voor script 2


# Start WebDriver
log_message("🚀 Motor opgestart, hyperdrive warmdraaien... (WebDriver starten)")
driver = webdriver.Chrome(options=options)

def close_browser():
    log_message("🛑 Browser blijft open voor inspectie. Handmatig sluiten als nodig.")
    sys.exit(0)

try:
    driver.get("http://metroeventsdc.rentpro5.nl/")
    log_message("🌌 Bestemming bereikt, scannen op levenstekens... (Navigeren naar RentPro)")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        log_message(f"🔍 Meerdere dimensies gedetecteerd, overschakelen naar iframe {len(iframes)}... (Iframe gevonden en geswitcht)")
        driver.switch_to.frame(iframes[0])
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "UserName"))).send_keys("sally")
    log_message("📝 Identiteitsgegevens ingevoerd, toegangscode verzonden... (Gebruikersnaam ingevuld)")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Password"))).send_keys("e7VBPymQ")
    log_message("🔑 Toegangsrechten verkregen, deur gaat open... (Wachtwoord ingevuld)")

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Log in']"))).click()
    log_message("✅ Authenticatie succesvol, luchtsluis openen... (Login-knop geklikt)")

    time.sleep(3)
    if driver.find_elements(By.XPATH, "//*[contains(text(), 'Klanten vandaag online')]"):
        log_message("✅ Klanten vandaag online gedetecteerd, toegang bevestigd!")
    else:
        log_message("⚠️ Klanten vandaag online niet gevonden! Mogelijk geen actieve klanten.")
        raise Exception("Klanten vandaag online niet gevonden")

    log_message("📦 Cargodeuren openen, op weg naar productvoorraad... (Navigeren naar productpagina)")
    driver.get("http://metroeventsdc.rentpro5.nl/Product")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    log_message("🎯 Doel bereikt, voorraad in zicht! (Productpagina geladen)")
    
    log_message("⏳ Extra stabilisatiecontrole, even wachten... (Wachten voor volledige paginalading)")
    time.sleep(3)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'dB DVA S1521N 21\" sub actief')]")
        ))
        log_message("✅ Doelobject gelokaliseerd, missie voltooid! (Tekst gevonden op pagina)")
    except Exception as e:
        log_message(f"⚠️ Lading verloren in de hyperruimte: {e}. Coördinaten opnieuw instellen... (Fout bij zoeken tekst)")
        raise
    
    log_message("🚀 Missie voltooid, klaar om terug te keren naar de basis! (Script voltooid zonder fouten)")
    close_browser()

except Exception as e:
    error_message = f"⛔ Kritieke fout: {str(e)}"
    log_message(error_message)
    show_error_popup(error_message)
