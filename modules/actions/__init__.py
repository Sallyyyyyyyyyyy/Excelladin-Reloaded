# Initialiseert de modules.actions package
from modules.actions.base import ActieBasis, ActieResultaat
from modules.actions.rentpro_inlezen import (
    RentProInlezenActie,
    RentProMeerdereInlezenActie,
    RentProZoekInlezenActie
)
from modules.actions.rentpro_upload import (
    RentProUploadActie,
    RentProBulkUploadActie,
    RentProUpdateActie
)

# Importeer de benodigde variabelen en functies uit het actions.py bestand
import sys
import os
import importlib.util

# Pad naar het actions.py bestand
actions_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "actions.py")

# Laad het actions.py bestand als module
spec = importlib.util.spec_from_file_location("actions_module", actions_path)
actions_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(actions_module)

# Exporteer de benodigde variabelen en functies
BESCHIKBARE_ACTIES = actions_module.BESCHIKBARE_ACTIES
voerActieUit = actions_module.voerActieUit
