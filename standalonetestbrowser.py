"""
Zeer eenvoudig testscript om te controleren of Chrome correct opstart en navigeert
"""
from selenium import webdriver
import time

print("🚀 Start browser test")
print("-----------------------")

# Chrome opties exact zoals in turboturbo
print("1. Chrome opties instellen...")
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-web-security")
options.add_argument("--allow-running-insecure-content")
options.add_argument("--window-size=1600,1000")
options.add_experimental_option("detach", True)
options.add_argument("--remote-debugging-port=9222")

# Start Chrome
print("2. Chrome opstarten...")
driver = webdriver.Chrome(options=options)

try:
    # Test met een bekende website
    print("3. Navigeren naar Google (controle)...")
    driver.get("https://www.google.com")
    time.sleep(2)
    print(f"   Titel: {driver.title}")
    print(f"   URL: {driver.current_url}")
    
    if "Google" in driver.title:
        print("   ✅ Google navigatie succesvol")
    else:
        print("   ❌ Google navigatie mislukt")
    
    # Test met RentPro
    print("\n4. Navigeren naar RentPro...")
    driver.get("http://metroeventsdc.rentpro5.nl")
    time.sleep(2)
    print(f"   Titel: {driver.title}")
    print(f"   URL: {driver.current_url}")
    
    if driver.current_url.startswith("data:"):
        print("   ❌ PROBLEEM: data: URL gedetecteerd!")
        print(f"   Data URL: {driver.current_url[:100]}...")
    else:
        print("   ✅ Navigatie succesvol")
    
    # Wacht op gebruiker input om browser open te houden
    input("\n🛑 Druk op Enter om de browser te sluiten...")
    
except Exception as e:
    print(f"❌ FOUT: {e}")

finally:
    print("\n-----------------------")
    print("🏁 Test afgerond")
    # Browser blijft open vanwege detach=True
