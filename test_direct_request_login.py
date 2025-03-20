"""
Test script voor directe HTTP requests implementatie (browserloze aanpak)
Dit script test of we succesvol kunnen inloggen via de API handler zonder browser
"""
import asyncio
from modules.logger import logger
from modules.rentpro.api_handler import ApiHandler

async def test_login():
    """Test login functionaliteit via directe HTTP requests (zonder browser)"""
    logger.logInfo("🚀 Test directe login gestart")
    
    # Creëer een API Handler instance
    api = ApiHandler()
    
    # Definieer inloggegevens
    gebruikersnaam = "metro"  # Vervang met echte gebruikersnaam
    wachtwoord = "M3tr0"      # Vervang met echt wachtwoord
    url = "http://metroeventsdc.rentpro5.nl/"
    
    # Probeer in te loggen
    success = await api.login(gebruikersnaam, wachtwoord, url)
    
    if success:
        logger.logInfo("✅ LOGIN SUCCESVOL! Directe HTTP login werkt!")
        
        # Test productlijst ophalen
        logger.logInfo("Productenlijst ophalen...")
        await api.navigate_to_products()
        products = await api.get_products_list()
        
        if products:
            logger.logInfo(f"✅ {len(products)} producten gevonden!")
            # Toon eerste drie producten
            for i, product in enumerate(products[:3]):
                logger.logInfo(f"  - Product {i+1}: {product['id']} - {product['naam']}")
        else:
            logger.logFout("❌ Geen producten gevonden")
    else:
        logger.logFout("❌ Login mislukt via directe HTTP requests")

if __name__ == "__main__":
    # Voer async test uit
    asyncio.run(test_login())
