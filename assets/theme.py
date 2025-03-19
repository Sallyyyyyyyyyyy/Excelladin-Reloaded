"""
Theme definitie voor Excelladin Reloaded
Implementeert een 1001 Nachten thema
"""

# Kleuren voor het 1001 Nachten thema
# Rijke kleuren voor een exotische oosterse sfeer
KLEUREN = {
    "achtergrond": "#785869",  # Gedempte paars - mysterieuze achtergrond
    "header_achtergrond": "#fdb04d",  # Gouden geel - opvallende header
    "tabblad_actief": "#b01345",  # Diepe roos - duidelijk zichtbaar voor actieve tabs
    "tabblad_inactief": "#785869",  # Gedempte paars - consistent met de achtergrond
    "tekst": "#FFFF00",  # Felgeel - opvallende tekst
    "button": "#d6254b",  # Helder rood - opvallend voor knoppen
    "button_hover": "#b01345",  # Diepe roos - subtiele verandering bij hover
    "fout": "#b01345",  # Diepe roos - duidelijk voor foutmeldingen
    "succes": "#0a0d2c",  # Donker marineblauw - elegant voor succesmeldingen
}

# Fonts
FONTS = {
    "titel": ("Papyrus", 16, "bold"),
    "subtitel": ("Papyrus", 12, "bold"),
    "normaal": ("Arial", 10),
    "klein": ("Arial", 8),
}

# Stijlen voor Tkinter widgets
STIJLEN = {
    "header": {
        "background": KLEUREN["header_achtergrond"],
        "padx": 10,
        "pady": 5,
    },
    "werkgebied": {
        "background": KLEUREN["achtergrond"],
        "padx": 10,
        "pady": 10,
    },
    "button": {
        "background": KLEUREN["button"],
        "foreground": "#FFFF00",  # Felgeel in plaats van wit
        "activebackground": KLEUREN["button_hover"],
        "activeforeground": "#FFFF00",  # Felgeel in plaats van wit
        "font": FONTS["normaal"],
        "borderwidth": 0,
        "padx": 10,
        "pady": 5,
    },
    "tabblad": {
        "background": KLEUREN["tabblad_inactief"],
        "foreground": KLEUREN["tekst"],
        "font": FONTS["normaal"],
        "borderwidth": 0,
    },
    "tabblad_actief": {
        "background": KLEUREN["tabblad_actief"],
        "foreground": "#FFFF00",  # Felgeel in plaats van wit
        "font": FONTS["normaal"],
        "borderwidth": 0,
    },
    "label": {
        "background": KLEUREN["achtergrond"],
        "foreground": KLEUREN["tekst"],
        "font": FONTS["normaal"],
    },
    "titel_label": {
        "background": KLEUREN["header_achtergrond"],
        "foreground": KLEUREN["tekst"],
        "font": FONTS["titel"],
    },
    "entry": {
        "background": "#fdb04d",  # Gouden geel in plaats van wit
        "foreground": KLEUREN["tekst"],
        "font": FONTS["normaal"],
    },
    "checkbox": {
        "background": KLEUREN["achtergrond"],
        "foreground": KLEUREN["tekst"],
        "font": FONTS["normaal"],
        "selectcolor": KLEUREN["achtergrond"],
    },
    "status": {
        "background": KLEUREN["header_achtergrond"],
        "foreground": KLEUREN["tekst"],
        "font": FONTS["klein"],
    },
    "foutmelding": {
        "background": KLEUREN["fout"],
        "foreground": "#FFFF00",  # Felgeel in plaats van wit
        "font": FONTS["normaal"],
        "padx": 10,
        "pady": 5,
    },
}

# Tooltips stijl
TOOLTIP_STIJL = {
    "background": "#0a0d2c",  # Donker marineblauw in plaats van lichtgeel
    "foreground": KLEUREN["tekst"],
    "font": FONTS["klein"],
    "padx": 5,
    "pady": 3,
    "borderwidth": 1,
    "relief": "solid",
}