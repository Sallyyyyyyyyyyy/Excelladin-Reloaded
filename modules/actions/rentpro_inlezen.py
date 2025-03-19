"""
RentPro inlezen module voor Excelladin Reloaded
Verantwoordelijk voor het inlezen van data uit RentPro
"""
import asyncio
from modules.logger import logger
from modules.excel_handler import excelHandler
from modules.actions.base import ActieBasis, ActieResultaat
from modules.actions.rentpro import RentProConnector, run_async

class RentProInlezenActie(ActieBasis):
    """Actie om product data in te lezen vanuit RentPro"""
    
    def __init__(self):
        """Initialiseer de RentPro inlezen actie"""
        super().__init__(
            naam="rentProInlezen",
            beschrijving="Haalt productdata op van RentPro en importeert in Excel",
            categorie="Inlezen vanuit RentPro"
        )
    
    def voerUit(self, parameters, rijen=None):
        """
        Implementatie van de actie
        
        Args:
            parameters (dict): Parameters voor de actie, moet bevatten:
                - product_id (str): ID van het product om in te lezen
                - doelKolommen (list): Lijst met kolomnamen om te vullen
            rijen (tuple): Optioneel, tuple met (startRij, eindRij) om alleen een bereik te bewerken
            
        Returns:
            ActieResultaat: Resultaat van de actie
        """
        try:
            # Controleer verplichte parameters
            verplicht = ["product_id", "doelKolommen"]
            for param in verplicht:
                if param not in parameters:
                    return ActieResultaat(
                        False, 
                        f"Ontbrekende parameter: {param}"
                    )
            
            product_id = parameters["product_id"]
            doelKolommen = parameters["doelKolommen"]
            
            # Controleer of er een bestand is geopend
            if not excelHandler.isBestandGeopend():
                return ActieResultaat(
                    False, 
                    "Kan actie niet uitvoeren: Geen Excel-bestand geopend"
                )
            
            # Controleer of alle doelkolommen bestaan
            for kolom in doelKolommen:
                if kolom not in excelHandler.kolomNamen:
                    return ActieResultaat(
                        False, 
                        f"Doelkolom '{kolom}' bestaat niet in het bestand"
                    )
            
            # Maak RentPro connector
            connector = RentProConnector()
            
            # Verbind met RentPro
            logger.logInfo("Verbinden met RentPro...")
            if not run_async(connector.verbind()):
                return ActieResultaat(
                    False,
                    "Kon niet verbinden met RentPro"
                )
            
            # Haal product data op
            logger.logInfo(f"Ophalen product data voor ID: {product_id}...")
            product_data = run_async(connector.lees_product_data(product_id))
            
            if not product_data:
                run_async(connector.sluit())
                return ActieResultaat(
                    False,
                    f"Kon geen data ophalen voor product ID: {product_id}"
                )
            
            # Lees veldmappings
            try:
                veld_mappings = connector.lees_veld_mappings()
            except Exception as e:
                run_async(connector.sluit())
                return ActieResultaat(
                    False,
                    f"Fout bij lezen veldmappings: {e}"
                )
            
            # Omgekeerde mapping maken (veld_id -> kolomnaam)
            omgekeerde_mapping = {v: k for k, v in veld_mappings.items()}
            
            # Bepaal het aantal rijen
            if rijen:
                startRij, eindRij = rijen
                aantalRijen = eindRij - startRij + 1
                rij_index = startRij
            else:
                aantalRijen = 1
                rij_index = 0  # Standaard naar eerste rij schrijven
            
            # Vul Excel met product data
            for kolom in doelKolommen:
                if kolom in veld_mappings:
                    veld_id = veld_mappings[kolom]
                    if veld_id in product_data:
                        waarde = product_data[veld_id]
                        excelHandler.bewerkKolom(kolom, [waarde], (rij_index, rij_index))
                        logger.logInfo(f"Kolom '{kolom}' gevuld met waarde '{waarde}'")
            
            # Sluit browser
            run_async(connector.sluit())
            
            return ActieResultaat(
                True,
                f"Product data succesvol ingelezen voor product ID: {product_id}"
            )
        
        except Exception as e:
            logger.logFout(f"Fout bij uitvoeren RentProInlezenActie: {e}")
            return ActieResultaat(False, f"Fout bij uitvoeren actie: {e}")

class RentProMeerdereInlezenActie(ActieBasis):
    """Actie om meerdere producten in te lezen vanuit RentPro"""
    
    def __init__(self):
        """Initialiseer de RentPro meerdere inlezen actie"""
        super().__init__(
            naam="rentProMeerdereInlezen",
            beschrijving="Haalt data op van meerdere producten uit RentPro en importeert in Excel",
            categorie="Inlezen vanuit RentPro"
        )
    
    def voerUit(self, parameters, rijen=None):
        """
        Implementatie van de actie
        
        Args:
            parameters (dict): Parameters voor de actie, moet bevatten:
                - product_ids (list): Lijst met product IDs om in te lezen
                - doelKolommen (list): Lijst met kolomnamen om te vullen
            rijen (tuple): Optioneel, tuple met (startRij, eindRij) om alleen een bereik te bewerken
            
        Returns:
            ActieResultaat: Resultaat van de actie
        """
        try:
            # Controleer verplichte parameters
            verplicht = ["product_ids", "doelKolommen"]
            for param in verplicht:
                if param not in parameters:
                    return ActieResultaat(
                        False, 
                        f"Ontbrekende parameter: {param}"
                    )
            
            product_ids = parameters["product_ids"]
            doelKolommen = parameters["doelKolommen"]
            
            # Controleer of er een bestand is geopend
            if not excelHandler.isBestandGeopend():
                return ActieResultaat(
                    False, 
                    "Kan actie niet uitvoeren: Geen Excel-bestand geopend"
                )
            
            # Controleer of alle doelkolommen bestaan
            for kolom in doelKolommen:
                if kolom not in excelHandler.kolomNamen:
                    return ActieResultaat(
                        False, 
                        f"Doelkolom '{kolom}' bestaat niet in het bestand"
                    )
            
            # Bepaal het aantal rijen
            if rijen:
                startRij, eindRij = rijen
                aantalRijen = eindRij - startRij + 1
            else:
                aantalRijen = excelHandler.haalRijAantal()
                startRij, eindRij = 0, aantalRijen - 1
            
            # Controleer of er genoeg rijen zijn
            if len(product_ids) > aantalRijen:
                return ActieResultaat(
                    False,
                    f"Niet genoeg rijen beschikbaar. Nodig: {len(product_ids)}, Beschikbaar: {aantalRijen}"
                )
            
            # Maak RentPro connector
            connector = RentProConnector()
            
            # Verbind met RentPro
            logger.logInfo("Verbinden met RentPro...")
            if not run_async(connector.verbind()):
                return ActieResultaat(
                    False,
                    "Kon niet verbinden met RentPro"
                )
            
            # Lees veldmappings
            try:
                veld_mappings = connector.lees_veld_mappings()
            except Exception as e:
                run_async(connector.sluit())
                return ActieResultaat(
                    False,
                    f"Fout bij lezen veldmappings: {e}"
                )
            
            # Omgekeerde mapping maken (veld_id -> kolomnaam)
            omgekeerde_mapping = {v: k for k, v in veld_mappings.items()}
            
            # Verwerk elk product
            for i, product_id in enumerate(product_ids):
                rij_index = startRij + i
                
                # Haal product data op
                logger.logInfo(f"Ophalen product data voor ID: {product_id}...")
                product_data = run_async(connector.lees_product_data(product_id))
                
                if not product_data:
                    logger.logWaarschuwing(f"Kon geen data ophalen voor product ID: {product_id}")
                    continue
                
                # Vul Excel met product data
                for kolom in doelKolommen:
                    if kolom in veld_mappings:
                        veld_id = veld_mappings[kolom]
                        if veld_id in product_data:
                            waarde = product_data[veld_id]
                            excelHandler.bewerkKolom(kolom, [waarde], (rij_index, rij_index))
                            logger.logInfo(f"Kolom '{kolom}' gevuld met waarde '{waarde}' voor rij {rij_index+1}")
            
            # Sluit browser
            run_async(connector.sluit())
            
            return ActieResultaat(
                True,
                f"Product data succesvol ingelezen voor {len(product_ids)} producten"
            )
        
        except Exception as e:
            logger.logFout(f"Fout bij uitvoeren RentProMeerdereInlezenActie: {e}")
            return ActieResultaat(False, f"Fout bij uitvoeren actie: {e}")

class RentProZoekInlezenActie(ActieBasis):
    """Actie om producten te zoeken en in te lezen vanuit RentPro"""
    
    def __init__(self):
        """Initialiseer de RentPro zoek en inlezen actie"""
        super().__init__(
            naam="rentProZoekInlezen",
            beschrijving="Zoekt producten in RentPro en importeert de gevonden data in Excel",
            categorie="Inlezen vanuit RentPro"
        )
    
    def voerUit(self, parameters, rijen=None):
        """
        Implementatie van de actie
        
        Args:
            parameters (dict): Parameters voor de actie, moet bevatten:
                - zoekterm (str): Zoekterm om producten te vinden
                - doelKolommen (list): Lijst met kolomnamen om te vullen
                - max_resultaten (int): Maximum aantal resultaten om in te lezen
            rijen (tuple): Optioneel, tuple met (startRij, eindRij) om alleen een bereik te bewerken
            
        Returns:
            ActieResultaat: Resultaat van de actie
        """
        try:
            # Controleer verplichte parameters
            verplicht = ["zoekterm", "doelKolommen"]
            for param in verplicht:
                if param not in parameters:
                    return ActieResultaat(
                        False, 
                        f"Ontbrekende parameter: {param}"
                    )
            
            zoekterm = parameters["zoekterm"]
            doelKolommen = parameters["doelKolommen"]
            max_resultaten = parameters.get("max_resultaten", 10)
            
            # Controleer of er een bestand is geopend
            if not excelHandler.isBestandGeopend():
                return ActieResultaat(
                    False, 
                    "Kan actie niet uitvoeren: Geen Excel-bestand geopend"
                )
            
            # Controleer of alle doelkolommen bestaan
            for kolom in doelKolommen:
                if kolom not in excelHandler.kolomNamen:
                    return ActieResultaat(
                        False, 
                        f"Doelkolom '{kolom}' bestaat niet in het bestand"
                    )
            
            # Bepaal het aantal rijen
            if rijen:
                startRij, eindRij = rijen
                aantalRijen = eindRij - startRij + 1
            else:
                aantalRijen = excelHandler.haalRijAantal()
                startRij, eindRij = 0, aantalRijen - 1
            
            # Maak RentPro connector
            connector = RentProConnector()
            
            # Verbind met RentPro
            logger.logInfo("Verbinden met RentPro...")
            if not run_async(connector.verbind()):
                return ActieResultaat(
                    False,
                    "Kon niet verbinden met RentPro"
                )
            
            # Navigeer naar productpagina
            logger.logInfo("Navigeren naar productpagina...")
            if not run_async(connector.navigeer_naar_producten()):
                run_async(connector.sluit())
                return ActieResultaat(
                    False,
                    "Kon niet navigeren naar productpagina"
                )
            
            # Zoek producten
            logger.logInfo(f"Zoeken naar producten met zoekterm: {zoekterm}...")
            
            # Implementeer zoekfunctionaliteit
            # Dit is een voorbeeld en moet worden aangepast aan de werkelijke RentPro interface
            search_results = run_async(self._zoek_producten(connector, zoekterm, max_resultaten))
            
            if not search_results:
                run_async(connector.sluit())
                return ActieResultaat(
                    False,
                    f"Geen producten gevonden met zoekterm: {zoekterm}"
                )
            
            # Lees veldmappings
            try:
                veld_mappings = connector.lees_veld_mappings()
            except Exception as e:
                run_async(connector.sluit())
                return ActieResultaat(
                    False,
                    f"Fout bij lezen veldmappings: {e}"
                )
            
            # Controleer of er genoeg rijen zijn
            if len(search_results) > aantalRijen:
                logger.logWaarschuwing(f"Meer resultaten gevonden ({len(search_results)}) dan beschikbare rijen ({aantalRijen}). Alleen de eerste {aantalRijen} resultaten worden ingelezen.")
                search_results = search_results[:aantalRijen]
            
            # Verwerk elk gevonden product
            for i, product_id in enumerate(search_results):
                rij_index = startRij + i
                
                # Haal product data op
                logger.logInfo(f"Ophalen product data voor ID: {product_id}...")
                product_data = run_async(connector.lees_product_data(product_id))
                
                if not product_data:
                    logger.logWaarschuwing(f"Kon geen data ophalen voor product ID: {product_id}")
                    continue
                
                # Vul Excel met product data
                for kolom in doelKolommen:
                    if kolom in veld_mappings:
                        veld_id = veld_mappings[kolom]
                        if veld_id in product_data:
                            waarde = product_data[veld_id]
                            excelHandler.bewerkKolom(kolom, [waarde], (rij_index, rij_index))
                            logger.logInfo(f"Kolom '{kolom}' gevuld met waarde '{waarde}' voor rij {rij_index+1}")
            
            # Sluit browser
            run_async(connector.sluit())
            
            return ActieResultaat(
                True,
                f"Product data succesvol ingelezen voor {len(search_results)} producten"
            )
        
        except Exception as e:
            logger.logFout(f"Fout bij uitvoeren RentProZoekInlezenActie: {e}")
            return ActieResultaat(False, f"Fout bij uitvoeren actie: {e}")
    
    async def _zoek_producten(self, connector, zoekterm, max_resultaten):
        """
        Zoek producten in RentPro
        
        Args:
            connector (RentProConnector): De RentPro connector
            zoekterm (str): Zoekterm om producten te vinden
            max_resultaten (int): Maximum aantal resultaten
            
        Returns:
            list: Lijst met product IDs
        """
        try:
            # Vul het zoekveld in
            await connector.page.waitForSelector('#searchString')
            await connector.page.type('#searchString', zoekterm)
            
            # Klik op de zoekknop
            await connector.page.click('#searchButton')
            
            # Wacht op resultaten
            await connector.page.waitForSelector('.product-list-item')
            
            # Verzamel product IDs
            product_ids = await connector.page.evaluate(f'''
                () => {{
                    const items = document.querySelectorAll('.product-list-item');
                    const ids = [];
                    
                    for (let i = 0; i < items.length && i < {max_resultaten}; i++) {{
                        const id = items[i].getAttribute('data-product-id');
                        if (id) ids.push(id);
                    }}
                    
                    return ids;
                }}
            ''')
            
            return product_ids
        
        except Exception as e:
            logger.logFout(f"Fout bij zoeken naar producten: {e}")
            return []
