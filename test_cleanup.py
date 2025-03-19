"""
Test script voor de clean_pycache functie
"""
import os
import sys

# Voeg applicatiemap toe aan sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importeer de cleanup functie
from modules.helpers import clean_pycache

# Voer de cleanup functie uit
print("Start cleanup test...")
clean_pycache()
print("Cleanup test voltooid.")
