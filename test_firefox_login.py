"""
Test script voor RentPro login met Firefox browser
Alternatieve oplossing voor het Chrome wit scherm probleem
"""
import tkinter as tk
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

def log(text):
    """Print naar console met timestamp"""
    print(f"[{time.strftime('%H:%M:%S')}] {text}")

def inlog_test():
    """Test inlog met Firefox in plaats van Chrome"""
    log("🚀 Test gestart met Firefox")
    
    try:
        # Firefox opties instellen
        log("Firefox opties instellen...")
        options = webdriver.FirefoxOptions()
        options.add_argument("--width=1600")
        options.add_argument("--height=1000")
        
        # Start Firefox WebDriver
        log("Firefox WebDriver starten...")
        driver = webdriver.Firefox(
            service=Service(GeckoDriverManager().install()),
            options=options
        )
        
        # Navigeer naar RentPro
        log("Navigeren naar RentPro...")
        driver.get("http://metroeventsdc.rentpro5.nl/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Controleer huidige URL
        current_url = driver.current_url
        log(f"Huidige URL: {current_url}")
        
        # Controleer op iframe en switch indien nodig
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            log(f"Iframe gevonden, overschakelen...")
            driver.switch_to.frame(iframes[0])
        
        # Controleer of login pagina geladen is
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "UserName"))
        )
        
        if username_field:
            log("✅ Login pagina succesvol geladen!")
            # Vul gebruikersnaam in
            username_field.send_keys("sally")
            
            # Vul wachtwoord in
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Password"))
            ).send_keys("e7VBPymQ")
            
            # Klik op login knop
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Log in']"))
            ).click()
            
            # Wacht even voor pagina laden
            log("Wachten op login resultaat...")
            time.sleep(3)
            
            # Controleer resultaat
            if "Klanten vandaag online" in driver.page_source:
                log("✅ LOGIN SUCCESVOL! (Klanten indicator gevonden)")
                return True
            
            # Alternatieve controle
            success_indicators = ["Dashboard", "Welkom", "Uitloggen", "Logout", "Menu"]
            if any(indicator in driver.page_source for indicator in success_indicators):
                log("✅ LOGIN SUCCESVOL! (Alternatieve indicator gevonden)")
                return True
                
            log("❌ Login mislukt, geen succes indicators gevonden")
            return False
        else:
            log("❌ Login pagina niet geladen")
            return False
            
    except Exception as e:
        log(f"❌ Fout: {e}")
        return False
    finally:
        # Blijf open voor debug
        log("Browser blijft open voor inspectie")
        input("Druk op Enter om de browser te sluiten...")
        try:
            driver.quit()
        except:
            pass

# UI voor de inlogtest
root = tk.Tk()
root.title("RentPro Firefox Inlog Test")
root.geometry("400x250")
root.configure(bg="#f0f0f0")

# Header
tk.Label(
    root, 
    text="RentPro Firefox Inlog Test", 
    bg="#f0f0f0", 
    font=("Arial", 16, "bold")
).pack(pady=15)

# Status label
status_var = tk.StringVar(value="Klik op de knop om Firefox te testen")
status = tk.Label(
    root, 
    textvariable=status_var, 
    bg="#f0f0f0", 
    font=("Arial", 10)
)
status.pack(pady=10)

# Test knop
def start_test():
    status_var.set("⏳ Test wordt uitgevoerd...")
    root.update()
    
    # Start test in aparte thread
    import threading
    def run_test():
        success = inlog_test()
        root.after(0, lambda: status_var.set(
            "✅ Test geslaagd: Firefox werkt!" if success else 
            "❌ Test gefaald: Firefox werkt niet"
        ))
    
    threading.Thread(target=run_test, daemon=True).start()

tk.Button(
    root,
    text="Start Firefox Test",
    command=start_test,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 12),
    width=15,
    height=2
).pack(pady=20)

# Exit handler
def on_close():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

if __name__ == "__main__":
    root.mainloop()
