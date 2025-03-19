"""
Super Direct RentPro Handler
Extreem vereenvoudigde versie zonder threading/async complexiteit
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import tkinter as tk
from tkinter import messagebox

def log_message(message, error=False):
    """Log een bericht naar console"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {'ERROR: ' if error else ''}{message}"
    print(msg, file=sys.stderr if error else sys.stdout)

def start_browser():
    """Start een nieuwe Chrome browser met de juiste instellingen"""
    try:
        # Chrome opties direct uit turboturbo script
        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--window-size=1600,1000")
        options.add_experimental_option("detach", True)
        options.add_argument("--remote-debugging-port=9222")
        
        # Start browser
        browser = webdriver.Chrome(options=options)
        log_message("Chrome browser succesvol gestart")
        return browser
    except Exception as e:
        log_message(f"Fout bij starten Chrome: {e}", error=True)
        return None

def login_to_rentpro(browser, gebruikersnaam, wachtwoord, url="http://metroeventsdc.rentpro5.nl"):
    """
    Log direct in bij RentPro zonder complexiteit
    
    Args:
        browser (WebDriver): Selenium WebDriver instance
        gebruikersnaam (str): RentPro gebruikersnaam
        wachtwoord (str): RentPro wachtwoord
        url (str): RentPro URL
        
    Returns:
        bool: True als login succesvol, anders False
    """
    try:
        # Navigeer naar de pagina
        log_message(f"Navigeren naar {url}")
        browser.get(url)
        
        # Wacht tot de pagina geladen is
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Controleer of we op een data: URL zijn beland
        if browser.current_url.startswith("data:"):
            log_message(f"Data URL gedetecteerd: {browser.current_url[:50]}...", error=True)
            return False
        
        # Controleer op iframe en switch indien nodig
        iframes = browser.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            log_message("Iframe gevonden, overschakelen")
            browser.switch_to.frame(iframes[0])
        
        # Vul gebruikersnaam in
        username_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "UserName"))
        )
        username_field.clear()
        username_field.send_keys(gebruikersnaam)
        log_message("Gebruikersnaam ingevuld")
        
        # Vul wachtwoord in
        password_field = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "Password"))
        )
        password_field.clear()
        password_field.send_keys(wachtwoord)
        log_message("Wachtwoord ingevuld")
        
        # Klik op login knop
        login_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Log in']"))
        )
        login_button.click()
        log_message("Login knop geklikt")
        
        # Wacht even voor pagina laden
        time.sleep(3)
        
        # Controleer of login succesvol was
        if "Klanten vandaag online" in browser.page_source:
            log_message("Login succesvol (klanten indicator gevonden)")
            return True
        
        # Alternatieve controle
        success_indicators = ["Dashboard", "Welkom", "Uitloggen", "Logout", "Menu"]
        if any(indicator in browser.page_source for indicator in success_indicators):
            log_message("Login succesvol (alternatieve indicator gevonden)")
            return True
        
        # Login mislukt
        log_message("Login mislukt, geen succes indicators gevonden", error=True)
        return False
        
    except Exception as e:
        log_message(f"Fout bij inloggen: {e}", error=True)
        return False

def close_browser(browser):
    """Sluit de browser"""
    if browser:
        try:
            browser.quit()
            log_message("Browser succesvol gesloten")
            return True
        except Exception as e:
            log_message(f"Fout bij sluiten browser: {e}", error=True)
            return False
    return True

# Eenvoudige test UI
def create_test_ui():
    """Maak een eenvoudige test UI"""
    root = tk.Tk()
    root.title("Super Direct RentPro Tester")
    root.geometry("400x300")
    
    # Browser instance
    browser = None
    
    # Status label
    status_var = tk.StringVar(value="Geen browser actief")
    status = tk.Label(root, textvariable=status_var, bg="#f0f0f0", font=("Arial", 10))
    status.pack(pady=10)
    
    # Inloggegevens frame
    login_frame = tk.Frame(root, padx=10, pady=10)
    login_frame.pack(fill=tk.X, padx=20)
    
    # Gebruikersnaam
    tk.Label(login_frame, text="Gebruikersnaam:").grid(row=0, column=0, sticky=tk.W)
    username_var = tk.StringVar(value="sally")  # Testaccount
    tk.Entry(login_frame, textvariable=username_var, width=25).grid(row=0, column=1)
    
    # Wachtwoord
    tk.Label(login_frame, text="Wachtwoord:").grid(row=1, column=0, sticky=tk.W)
    password_var = tk.StringVar(value="e7VBPymQ")  # Testaccount
    tk.Entry(login_frame, textvariable=password_var, width=25, show="*").grid(row=1, column=1)
    
    # URL
    tk.Label(login_frame, text="RentPro URL:").grid(row=2, column=0, sticky=tk.W)
    url_var = tk.StringVar(value="http://metroeventsdc.rentpro5.nl")
    tk.Entry(login_frame, textvariable=url_var, width=25).grid(row=2, column=1)
    
    # Functieknoppen
    def on_start_browser():
        """Start browser knop handler"""
        nonlocal browser
        if browser:
            messagebox.showwarning("Let op", "Er is al een browser actief")
            return
            
        browser = start_browser()
        if browser:
            status_var.set("Browser gestart")
        else:
            status_var.set("Fout bij starten browser")
    
    def on_login():
        """Login knop handler"""
        nonlocal browser
        if not browser:
            messagebox.showwarning("Let op", "Start eerst een browser")
            return
            
        # Direct inloggen
        status_var.set("Bezig met inloggen...")
        root.update()
        success = login_to_rentpro(
            browser, 
            username_var.get(), 
            password_var.get(), 
            url_var.get()
        )
        
        if success:
            status_var.set("Ingelogd ✅")
            messagebox.showinfo("Succes", "Succesvol ingelogd bij RentPro")
        else:
            status_var.set("Inloggen mislukt ❌")
            messagebox.showerror("Fout", "Kon niet inloggen bij RentPro")
    
    def on_close_browser():
        """Sluit browser knop handler"""
        nonlocal browser
        if not browser:
            messagebox.showwarning("Let op", "Geen actieve browser")
            return
            
        if close_browser(browser):
            browser = None
            status_var.set("Browser gesloten")
        else:
            status_var.set("Fout bij sluiten browser")
    
    # Knoppen
    buttons_frame = tk.Frame(root, padx=10, pady=10)
    buttons_frame.pack(fill=tk.X, padx=20, pady=10)
    
    tk.Button(
        buttons_frame, 
        text="Start Browser", 
        command=on_start_browser,
        bg="#4CAF50", fg="white", 
        width=12
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        buttons_frame, 
        text="Login", 
        command=on_login,
        bg="#2196F3", fg="white", 
        width=12
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        buttons_frame, 
        text="Sluit Browser", 
        command=on_close_browser,
        bg="#f44336", fg="white", 
        width=12
    ).pack(side=tk.LEFT, padx=5)
    
    # Exit handler
    def on_close():
        """Cleanup bij afsluiten"""
        nonlocal browser
        if browser:
            close_browser(browser)
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    
    return root

if __name__ == "__main__":
    # Toon UI
    root = create_test_ui()
    root.mainloop()
