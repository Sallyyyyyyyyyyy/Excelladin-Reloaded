# __pycache__ Automatisch Beheer

## Implementatie

De volgende wijzigingen zijn doorgevoerd om __pycache__ directories automatisch te beheren:

1. Alle bestaande __pycache__ directories en .pyc bestanden zijn verwijderd.

2. Een .gitignore bestand is toegevoegd met de volgende regels:
   ```
   # Python bytecode files
   __pycache__/
   *.py[cod]
   *$py.class
   ```

3. Een nieuwe `clean_pycache()` functie is toegevoegd aan `modules/helpers.py`:
   ```python
   def clean_pycache():
       """Verwijder alle __pycache__ directories en .pyc bestanden"""
       import os
       import shutil
       
       count_dirs = 0
       count_files = 0
       
       for root, dirs, files in os.walk('.'):
           # Verwijder __pycache__ directories
           for d in dirs[:]:  # Kopieer de lijst om veilig items te verwijderen tijdens iteratie
               if d == '__pycache__':
                   path = os.path.join(root, d)
                   try:
                       shutil.rmtree(path)
                       count_dirs += 1
                       # Verwijder deze directory uit de lijst zodat we er niet in zoeken
                       dirs.remove(d)
                   except Exception as e:
                       from modules.logger import logger
                       logger.logWaarschuwing(f"Kon __pycache__ niet verwijderen: {path}: {e}")
           
           # Verwijder .pyc bestanden
           for f in files:
               if f.endswith('.pyc'):
                   path = os.path.join(root, f)
                   try:
                       os.remove(path)
                       count_files += 1
                   except Exception as e:
                       from modules.logger import logger
                       logger.logWaarschuwing(f"Kon .pyc bestand niet verwijderen: {path}: {e}")
       
       from modules.logger import logger
       if count_dirs > 0 or count_files > 0:
           logger.logInfo(f"Opruiming: {count_dirs} __pycache__ directories en {count_files} .pyc bestanden verwijderd")
   ```

4. De `main.py` is aangepast om de functie automatisch bij het opstarten uit te voeren:
   ```python
   # Importeer modules
   from modules.logger import logger
   from modules.gui import ExcelladinApp
   from modules.helpers import clean_pycache
   
   # Verwijder Python cache bestanden
   clean_pycache()
   ```

## Voordelen

- Voorkomt problemen met verouderde bytecode bestanden
- Houdt de repository schoon
- Automatische opruiming bij elke start van de applicatie
- Logging van verwijderde bestanden voor transparantie
