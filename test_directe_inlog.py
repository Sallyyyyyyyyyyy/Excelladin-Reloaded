"""
Directe test voor inlogknop met DIRECT COPIED CODE 
uit turboturbo script - geen onnodige complexiteit
"""
import tkinter as tk
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def log(text):
    """Print naar console met timestamp"""
    print(f"[{time.strftime('%H:%M:%S')}] {text}")

def inlog_test():
    """Test inlog met EXACT turboturbo script code"""
    log("🚀 Test gestart")
    
    # 1. Chrome-opties instellen - EXACTE CODE uit turboturbo script
    log("Chrome opties instellen...")
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--window-size=1600,1000")
    options.add_experimental_option("detach", True)
    options.add_argument("--remote-debugging-port=9222")
    
    # 2. Start WebDriver - EXACTE CODE uit turboturbo script
    log("WebDriver starten...")
    driver = webdriver.Chrome(options=options)
    
    try:
        # 3. Navigeer naar RentPro - EXACTE CODE uit turboturbo script
        log("Navigeren naar RentPro...")
        driver.get("http://metroeventsdc.rentpro5.nl/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # 4. Controleer huidige URL om data: te detecteren
        current_url = driver.current_url
        log(f"Huidige URL: {current_url}")
        
        if current_url.startswith("data:"):
            log("⚠️ PROBLEEM: data: URL gedetecteerd!")
            return False
        
        # 5. Controleer op iframe en switch indien nodig - EXACTE CODE uit turboturbo script
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            log(f"Iframe gevonden, overschakelen...")
            driver.switch_to.frame(iframes[0])
        
        # 6. Vul gebruikersnaam in - EXACTE CODE uit turboturbo script
        log("Gebruikersnaam invullen...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "UserName"))
        ).send_keys("sally")
        
        # 7. Vul wachtwoord in - EXACTE CODE uit turboturbo script
        log("Wachtwoord invullen...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "Password"))
        ).send_keys("e7VBPymQ")
        
        # 8. Klik op login knop - EXACTE CODE uit turboturbo script
        log("Login knop klikken...")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Log in']"))
        ).click()
        
        # 9. Wacht even voor pagina laden - EXACTE CODE uit turboturbo script
        log("Wachten op login resultaat...")
        time.sleep(3)
        
        # 10. Controleer resultaat
        log("Controleren of login succesvol was...")
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
        
    except Exception as e:
        log(f"❌ Fout: {e}")
        return False
    finally:
        # Blijf open voor debug
        log("Browser blijft open voor inspectie")
        input("Druk op Enter om de browser te sluiten...")
        driver.quit()

# UI voor de inlogtest
root = tk.Tk()
root.title("RentPro Inlog Test")
root.geometry("400x250")
root.configure(bg="#f0f0f0")

# Header
tk.Label(
    root, 
    text="RentPro Inlog Test", 
    bg="#f0f0f0", 
    font=("Arial", 16, "bold")
).pack(pady=15)

# Status label
status_var = tk.StringVar(value="Klik op de knop om de test te starten")
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
            "✅ Test geslaagd: Login werkt!" if success else 
            "❌ Test gefaald: Login werkt niet"
        ))
    
    threading.Thread(target=run_test, daemon=True).start()

tk.Button(
    root,
    text="Start Inlog Test",
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
