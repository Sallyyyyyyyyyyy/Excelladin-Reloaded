"""
Patch2theRescue.py - Patch systeem voor Excelladin Reloaded

Instructies voor patch-makers:
1. Definieer je patches in dit bestand
2. Zorg dat elke patch de juiste structuur heeft
3. Voeg je patches toe aan de patches lijst onderaan
4. Zorg dat je een unieke patch_id gebruikt
"""
import os
import shutil
import importlib
import sys
import traceback
from datetime import datetime

# Globale configuratie
VERBOSE_LOGGING = True  # Uitgebreide logging naar console

# Log functie
def log_patch(bericht, berichtType="INFO"):
    """
    Log een bericht naar het patch logbestand
    
    Args:
        bericht (str): Het te loggen bericht
        berichtType (str): Type bericht (INFO, WAARSCHUWING, FOUT)
    """
    logBestandsnaam = "PatchCalling4Emergency.txt"
    huidigetijd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1001 Nachten stijl berichten
    prefixen = {
        "INFO": "O wijze gebruiker, ",
        "WAARSCHUWING": "Wees gewaarschuwd, o reiziger, ",
        "FOUT": "Bij Allah's baard! Een ramp is geschied: ",
        "PATCH": "De magie van de patch voltrekt zich: "
    }
    
    prefix = prefixen.get(berichtType, "")
    log_regel = f"[{huidigetijd}] [{berichtType}] {prefix}{bericht}\n"
    
    try:
        with open(logBestandsnaam, 'a', encoding='utf-8') as bestand:
            bestand.write(log_regel)
        
        # Print naar console voor betere zichtbaarheid
        if VERBOSE_LOGGING or berichtType in ["FOUT", "WAARSCHUWING"]:
            print(f"{berichtType}: {bericht}")
            
    except Exception as e:
        print(f"Kon niet naar patch logbestand schrijven: {e}")


class Patch:
    """Basis klasse voor een patch"""
    
    def __init__(self, patch_id, beschrijving):
        """
        Initialiseer een patch
        
        Args:
            patch_id (str): Unieke ID voor de patch
            beschrijving (str): Beschrijving van wat de patch doet
        """
        self.patch_id = patch_id
        self.beschrijving = beschrijving
    
    def pas_toe(self):
        """
        Pas de patch toe (implementeer in subklassen)
        
        Returns:
            bool: True als de patch succesvol is toegepast, anders False
        """
        raise NotImplementedError("Deze methode moet worden geïmplementeerd in subklassen")


class BestandsPatch(Patch):
    """Patch om bestanden te vervangen of toe te voegen"""
    
    def __init__(self, patch_id, beschrijving, bron_bestanden, doel_paden, maak_backup=True):
        """
        Initialiseer een bestandspatch
        
        Args:
            patch_id (str): Unieke ID voor de patch
            beschrijving (str): Beschrijving van wat de patch doet
            bron_bestanden (list): Lijst met paden naar bronbestanden in de patch
            doel_paden (list): Lijst met paden waar de bestanden naartoe moeten
            maak_backup (bool): Of er backups gemaakt moeten worden van bestaande bestanden
        """
        super().__init__(patch_id, beschrijving)
        self.bron_bestanden = bron_bestanden
        self.doel_paden = doel_paden
        self.maak_backup = maak_backup
    
    def pas_toe(self):
        """
        Pas de bestandspatch toe
        
        Returns:
            bool: True als de patch succesvol is toegepast, anders False
        """
        if len(self.bron_bestanden) != len(self.doel_paden):
            log_patch(f"Patch {self.patch_id} fout: Aantal bronbestanden komt niet overeen met aantal doelbestanden", "FOUT")
            return False
        
        succes = True
        
        for i, (bron, doel) in enumerate(zip(self.bron_bestanden, self.doel_paden)):
            try:
                # Controleer of bronbestand bestaat
                if not os.path.exists(bron):
                    log_patch(f"Bronbestand {bron} bestaat niet", "FOUT")
                    succes = False
                    continue
                
                # Maak backup indien nodig
                if self.maak_backup and os.path.exists(doel):
                    backup_pad = f"{doel}.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    shutil.copy2(doel, backup_pad)
                    log_patch(f"Backup gemaakt van {doel} naar {backup_pad}", "INFO")
                
                # Kopieer bestand
                doel_map = os.path.dirname(doel)
                if doel_map and not os.path.exists(doel_map):
                    os.makedirs(doel_map)
                
                shutil.copy2(bron, doel)
                log_patch(f"Bestand {bron} gekopieerd naar {doel}", "PATCH")
                
            except Exception as e:
                log_patch(f"Fout bij patchen bestand {bron} naar {doel}: {e}", "FOUT")
                log_patch(f"Stack trace: {traceback.format_exc()}", "FOUT")
                succes = False
        
        return succes


class ModulePatch(Patch):
    """Patch om code in een module te wijzigen"""
    
    def __init__(self, patch_id, beschrijving, module_naam, wijzigingen):
        """
        Initialiseer een modulepatch
        
        Args:
            patch_id (str): Unieke ID voor de patch
            beschrijving (str): Beschrijving van wat de patch doet
            module_naam (str): Naam van de module om te patchen
            wijzigingen (list): Lijst met (oud, nieuw) tuples voor tekstvervanging
        """
        super().__init__(patch_id, beschrijving)
        self.module_naam = module_naam
        self.wijzigingen = wijzigingen
    
    def pas_toe(self):
        """
        Pas de modulepatch toe
        
        Returns:
            bool: True als de patch succesvol is toegepast, anders False
        """
        try:
            # Zoek het modulebestand
            if self.module_naam.startswith('modules.'):
                module_basis = self.module_naam.split('.')[1]
                module_pad = os.path.join('modules', f"{module_basis}.py")
            else:
                module_pad = f"{self.module_naam.replace('.', os.sep)}.py"
            
            # Geef duidelijke foutmelding als het pad niet wordt gevonden
            if not os.path.exists(module_pad):
                log_patch(f"Module bestand {module_pad} niet gevonden", "FOUT")
                log_patch(f"Huidige werkmap: {os.getcwd()}", "INFO")
                log_patch(f"Beschikbare bestanden in modules: {os.listdir('modules') if os.path.exists('modules') else 'map niet gevonden'}", "INFO")
                return False
            
            # Maak backup
            backup_pad = f"{module_pad}.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.copy2(module_pad, backup_pad)
            log_patch(f"Backup gemaakt van {module_pad} naar {backup_pad}", "INFO")
            
            # Lees bestand
            with open(module_pad, 'r', encoding='utf-8') as f:
                inhoud = f.read()
            
            # Controleer of alle oude patronen gevonden worden
            wijzigingen_toegepast = 0
            nieuwe_inhoud = inhoud
            for oud, nieuw in self.wijzigingen:
                if oud not in nieuwe_inhoud:
                    log_patch(f"Patroon niet gevonden in module: {oud[:50]}...", "WAARSCHUWING")
                    continue
                nieuwe_inhoud = nieuwe_inhoud.replace(oud, nieuw)
                wijzigingen_toegepast += 1
            
            # Alleen opslaan als er wijzigingen zijn aangebracht
            if wijzigingen_toegepast > 0:
                # Schrijf bestand
                with open(module_pad, 'w', encoding='utf-8') as f:
                    f.write(nieuwe_inhoud)
                
                log_patch(f"Module {self.module_naam} succesvol gepatcht met {wijzigingen_toegepast} wijzigingen", "PATCH")
            else:
                log_patch(f"Geen wijzigingen toegepast op module {self.module_naam}", "WAARSCHUWING")
                return False
            
            # Herlaad module indien geladen
            if self.module_naam in sys.modules:
                try:
                    importlib.reload(sys.modules[self.module_naam])
                    log_patch(f"Module {self.module_naam} hergeladen", "INFO")
                except Exception as e:
                    log_patch(f"Kon module {self.module_naam} niet herladen: {e}", "WAARSCHUWING")
                    log_patch(f"Stack trace: {traceback.format_exc()}", "FOUT")
            
            return True
        except Exception as e:
            log_patch(f"Fout bij patchen module {self.module_naam}: {e}", "FOUT")
            log_patch(f"Stack trace: {traceback.format_exc()}", "FOUT")
            return False


class DependencyPatch(Patch):
    """Patch om afhankelijkheden te installeren"""
    
    def __init__(self, patch_id, beschrijving, packages):
        """
        Initialiseer een dependency patch
        
        Args:
            patch_id (str): Unieke ID voor de patch
            beschrijving (str): Beschrijving van wat de patch doet
            packages (list): Lijst met packagenamen om te installeren
        """
        super().__init__(patch_id, beschrijving)
        self.packages = packages
    
    def pas_toe(self):
        """
        Installeer de benodigde packages
        
        Returns:
            bool: True als alle packages succesvol zijn geïnstalleerd, anders False
        """
        try:
            import pip
            import subprocess
            
            succes = True
            for package in self.packages:
                log_patch(f"Controleren of {package} is geïnstalleerd...", "INFO")
                
                # Probeer de module te importeren
                try:
                    __import__(package.replace('-', '_').split('>=')[0].split('==')[0])
                    log_patch(f"{package} is al geïnstalleerd", "INFO")
                except ImportError:
                    log_patch(f"{package} is niet geïnstalleerd, bezig met installeren...", "INFO")
                    
                    # Probeer package te installeren
                    try:
                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                        log_patch(f"{package} succesvol geïnstalleerd", "INFO")
                    except Exception as e:
                        log_patch(f"Fout bij installeren van {package}: {e}", "FOUT")
                        log_patch(f"Stack trace: {traceback.format_exc()}", "FOUT")
                        log_patch(f"Installeer handmatig met: pip install {package}", "WAARSCHUWING")
                        succes = False
            
            return succes
        except Exception as e:
            log_patch(f"Fout bij controleren van afhankelijkheden: {e}", "FOUT")
            log_patch(f"Stack trace: {traceback.format_exc()}", "FOUT")
            return False


# Lijst met beschikbare patches
patches = [
    # Installeer afhankelijkheden eerst
    DependencyPatch(
        "dependency_patch_001",
        "Installeer benodigde afhankelijkheden (Pillow)",
        ["pillow"]
    ),
    
    # Logo afbeelding patch - vervangt de placeholder met de alladin.jpg afbeelding
    ModulePatch(
        "logo_afbeelding_patch_001",
        "Vervangt de logo placeholder met de alladin.jpg afbeelding",
        "modules.gui",
        [
            ("""        # Placeholder voor afbeelding (links)
        self.logoPlaceholder = tk.Label(
            self.headerFrame,
            text="[Logo]",
            foreground=STIJLEN["label"]["foreground"],
            font=STIJLEN["label"]["font"],
            background=STIJLEN["header"]["background"],
            width=10,
            height=2
        )
        self.logoPlaceholder.pack(side=tk.LEFT)""",
            
            """        # Laad en toon afbeelding (links)
        try:
            from PIL import Image, ImageTk
            import os
            
            img_path = os.path.join('assets', 'alladin.jpg')
            if os.path.exists(img_path):
                # Open de afbeelding en pas de grootte aan
                original_img = Image.open(img_path)
                # Bereken nieuwe grootte met behoud van aspect ratio
                width, height = original_img.size
                new_height = 50
                new_width = int(width * (new_height / height))
                resized_img = original_img.resize((new_width, new_height), Image.LANCZOS)
                
                # Converteer naar PhotoImage voor Tkinter
                tk_img = ImageTk.PhotoImage(resized_img)
                
                # Maak label met afbeelding
                self.logoLabel = tk.Label(
                    self.headerFrame,
                    image=tk_img,
                    background=STIJLEN["header"]["background"]
                )
                self.logoLabel.image = tk_img  # Bewaar referentie
                self.logoLabel.pack(side=tk.LEFT, padx=5)
                
                logger.logInfo("Logo afbeelding succesvol geladen")
            else:
                logger.logWaarschuwing(f"Afbeelding niet gevonden: {img_path}")
                # Fallback naar placeholder als afbeelding niet bestaat
                self.logoPlaceholder = tk.Label(
                    self.headerFrame,
                    text="[Logo]",
                    foreground=STIJLEN["label"]["foreground"],
                    font=STIJLEN["label"]["font"],
                    background=STIJLEN["header"]["background"],
                    width=10,
                    height=2
                )
                self.logoPlaceholder.pack(side=tk.LEFT)
        except Exception as e:
            logger.logFout(f"Fout bij laden logo afbeelding: {e}")
            # Fallback naar placeholder bij fouten
            self.logoPlaceholder = tk.Label(
                self.headerFrame,
                text="[Logo]",
                foreground=STIJLEN["label"]["foreground"],
                font=STIJLEN["label"]["font"],
                background=STIJLEN["header"]["background"],
                width=10,
                height=2
            )
            self.logoPlaceholder.pack(side=tk.LEFT)""")
        ]
    ),
]


def pas_patch_toe():
    """Hoofdfunctie om alle patches toe te passen"""
    log_patch("Start toepassen patches", "INFO")
    print("\n=== Excelladin Reloaded Patch Systeem ===")
    print(f"Huidige werkmap: {os.getcwd()}")
    print(f"Python versie: {sys.version}")
    print("=======================================\n")
    
    for patch in patches:
        log_patch(f"Toepassen patch {patch.patch_id}: {patch.beschrijving}", "INFO")
        print(f"\nToepassen: {patch.beschrijving}...")
        
        if patch.pas_toe():
            log_patch(f"Patch {patch.patch_id} succesvol toegepast", "PATCH")
            print(f"✓ Succes: {patch.beschrijving}")
        else:
            log_patch(f"Patch {patch.patch_id} kon niet worden toegepast", "FOUT")
            print(f"✗ Mislukt: {patch.beschrijving}")
    
    log_patch("Patchen voltooid", "INFO")
    print("\nPatchen voltooid! Druk op Enter om af te sluiten...")
    input()  # Wacht op Enter om te voorkomen dat het venster sluit bij dubbel-klikken


# Als dit script direct wordt uitgevoerd
if __name__ == "__main__":
    try:
        pas_patch_toe()
    except Exception as e:
        log_patch(f"Onverwachte fout in patch script: {e}", "FOUT")
        log_patch(f"Stack trace: {traceback.format_exc()}", "FOUT")
        print(f"\nEr is een onverwachte fout opgetreden: {e}")
        print("Controleer het logbestand voor meer details.")
        print("\nDruk op Enter om af te sluiten...")
        input()