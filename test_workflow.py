"""
Test script om het specifieke probleem met de inlogknop in de rentpro_tab.py workflow te debuggen
"""
import tkinter as tk
import asyncio
import sys
import time
from modules.rentpro_handler import rentproHandler
from modules.logger import logger

# Globale variabelen
ingelogd = False
inlog_window = None

async def simuleer_login_knop_klik():
    """Simuleer exact wat er gebeurt wanneer op de inlogknop wordt gedrukt"""
    print("\n🔘 Login knop geklikt (simulatie start)")
    print("-----------------------------------")
    
    # Stap 1: Initialiseren
    print("Stap 1: WebDriver initialiseren...")
    init_result = await rentproHandler.initialize()
    print(f"Resultaat: {'✅ Success' if init_result else '❌ Mislukt'}")
    
    # Controleer browser status na init
    if rentproHandler.driver:
        print(f"Browser URL na initialisatie: {rentproHandler.driver.current_url}")
        if rentproHandler.driver.current_url.startswith('data:'):
            print("⚠️ DATA URL GEDETECTEERD na initialisatie!")
    
    # Stap 2: Login poging
    print("\nStap 2: Inloggen bij RentPro...")
    login_result = await rentproHandler.login("sally", "e7VBPymQ")  # Testaccount
    print(f"Resultaat: {'✅ Success' if login_result else '❌ Mislukt'}")
    
    # Controleer browser status na login poging
    if rentproHandler.driver:
        print(f"Browser URL na login poging: {rentproHandler.driver.current_url}")
        if rentproHandler.driver.current_url.startswith('data:'):
            print("⚠️ DATA URL GEDETECTEERD na login poging!")
    
    # Update status
    global ingelogd
    ingelogd = login_result
    print(f"Login status bijgewerkt: {'✅ Ingelogd' if ingelogd else '❌ Niet ingelogd'}")
    print("-----------------------------------")

def toon_inlog_status():
    """Toon de huidige inlogstatus in het UI venster"""
    status_text = "✅ Ingelogd" if ingelogd else "❌ Niet ingelogd"
    status_label.config(text=f"Status: {status_text}")

def handle_inlog_knop():
    """Verwerk de inlogknop klik en update UI"""
    # Schakel knop uit tijdens verwerking
    inlog_button.config(state=tk.DISABLED)
    status_label.config(text="⏳ Bezig met inloggen...")
    
    # Definieer een asyncio functie die de login verwerkt
    async def proces():
        await simuleer_login_knop_klik()
        # Update UI vanuit main thread
        inlog_window.after(0, lambda: status_label.config(text=f"Status: {'✅ Ingelogd' if ingelogd else '❌ Niet ingelogd'}"))
        inlog_window.after(0, lambda: inlog_button.config(state=tk.NORMAL))
    
    # Voer asyncio taak uit in de achtergrond
    loop = asyncio.get_event_loop()
    loop.create_task(proces())

def maak_ui():
    """Maak een eenvoudig test UI venster"""
    global inlog_window, status_label, inlog_button
    
    inlog_window = tk.Tk()
    inlog_window.title("RentPro Inlog Test")
    inlog_window.geometry("400x250")
    inlog_window.configure(bg="#f0f0f0")
    
    # Header
    header = tk.Label(
        inlog_window,
        text="RentPro Inlog Tester",
        bg="#f0f0f0",
        font=("Arial", 16, "bold")
    )
    header.pack(pady=15)
    
    # Statuslabel
    status_label = tk.Label(
        inlog_window,
        text="Status: ❌ Niet ingelogd",
        bg="#f0f0f0",
        font=("Arial", 12)
    )
    status_label.pack(pady=10)
    
    # Inlogknop
    inlog_button = tk.Button(
        inlog_window,
        text="Inloggen",
        command=handle_inlog_knop,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 12),
        width=15,
        height=2
    )
    inlog_button.pack(pady=20)
    
    # Sluitknop
    close_button = tk.Button(
        inlog_window,
        text="Sluiten",
        command=inlog_window.destroy,
        bg="#f44336",
        fg="white",
        font=("Arial", 12),
        width=15
    )
    close_button.pack(pady=10)
    
    return inlog_window

# Setup asyncio event loop voor Tkinter
def setup_asyncio_tkinter():
    """Configureer asyncio om te werken met Tkinter"""
    # Maak nieuwe event loop voor deze thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Definieer functie om asyncio te laten samenwerken met tkinter
    def run_tasks():
        loop.call_soon(lambda: loop.stop() if not inlog_window else None)
        loop.run_forever()
        inlog_window.after(50, run_tasks)  # Continue checking every 50ms
    
    # Start de asyncio/tkinter integratie
    inlog_window.after(50, run_tasks)

if __name__ == "__main__":
    print("🚀 Start workflow test")
    print("======================")
    
    # Maak en start UI
    inlog_window = maak_ui()
    
    # Setup asyncio voor tkinter
    setup_asyncio_tkinter()
    
    # Start UI hoofdloop
    inlog_window.mainloop()
    
    # Cleanup na sluiten UI
    print("\n🧹 Opruimen...")
    loop = asyncio.get_event_loop()
    close_task = loop.create_task(rentproHandler.close())
    loop.run_until_complete(close_task)
    
    print("======================")
    print("🏁 Test beëindigd")
