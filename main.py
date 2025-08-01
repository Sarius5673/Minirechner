from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QGridLayout, QCheckBox, QDialog, QVBoxLayout, QComboBox
from PySide6.QtCore import QSettings
from asteval import Interpreter
import sys
from math import sqrt, log, log10, factorial, sin, cos, tan, asin, acos, atan, radians, degrees

light_theme = """
/* Light Theme */
QWidget {
    background-color: #f5f5f5;
    color: #222831;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 15px;
}
QPushButton {
    background-color: #e0e0e0;
    border: 1px solid #bdbdbd;
    border-radius: 6px;
    padding: 10px;
    color: #222831;
}
QPushButton:hover {
    background-color: #bdbdbd;
}
QPushButton:pressed {
    background-color: #9e9e9e;
}
QLabel#DisplayLabel {
    font-size: 26px;
    background-color: #ffffff;
    padding: 18px;
    border-radius: 8px;
    qproperty-alignment: AlignRight;
    color: #222831;
}
QCheckBox {
    padding: 6px;
}
"""

grey_theme = """
/* Grey Theme */
QWidget {
    background-color: #424242;
    color: #f5f5f5;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 15px;
}
QPushButton {
    background-color: #616161;
    border: 1px solid #757575;
    border-radius: 6px;
    padding: 10px;
    color: #f5f5f5;
}
QPushButton:hover {
    background-color: #757575;
}
QPushButton:pressed {
    background-color: #212121;
}
QLabel#DisplayLabel {
    font-size: 26px;
    background-color: #333333;
    padding: 18px;
    border-radius: 8px;
    qproperty-alignment: AlignRight;
    color: #f5f5f5;
}
QCheckBox {
    padding: 6px;
}
"""

dark_theme = """
/* Dark Theme */
QWidget {
    background-color: #181818;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 15px;
}
QPushButton {
    background-color: #232323;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 10px;
    color: #e0e0e0;
}
QPushButton:hover {
    background-color: #333333;
}
QPushButton:pressed {
    background-color: #111111;
}
QLabel#DisplayLabel {
    font-size: 26px;
    background-color: #222222;
    padding: 18px;
    border-radius: 8px;
    qproperty-alignment: AlignRight;
    color: #e0e0e0;
}
QCheckBox {
    padding: 6px;
}
"""

ans = "0"
deg_mode = True # True = degree, False = radiant; Standart = True
theme = 0 # 0 = light mode, 1 = grey mode, 2 = dark mode; Standart = 0

from PySide6.QtWidgets import QRadioButton, QButtonGroup

def einstellungen_oeffnen(parent, app):
    global deg_mode, theme

    dialog = QDialog(parent)
    dialog.setWindowTitle("Einstellungen")
    dialog.setFixedSize(320, 270)

    layout = QVBoxLayout(dialog)

    label_winkel = QLabel("Winkelmodus:")
    layout.addWidget(label_winkel)

    
    grad_radio = QRadioButton("Grad")
    rad_radio = QRadioButton("Radiant")

    gruppe = QButtonGroup(dialog)
    gruppe.addButton(grad_radio)
    gruppe.addButton(rad_radio)

    if deg_mode:
        grad_radio.setChecked(True)
    else:
        rad_radio.setChecked(True)

    layout.addWidget(grad_radio)
    layout.addWidget(rad_radio)

    label_design = QLabel("Design:")
    layout.addWidget(label_design)

    combo = QComboBox()
    combo.addItem("Light Mode")
    combo.addItem("Grey Mode")
    combo.addItem("Dark Mode")
    layout.addWidget(combo)

    if theme == 2:
        combo.setCurrentText("Dark Mode")
    elif theme == 1:
        combo.setCurrentText("Grey Mode")
    else:
        combo.setCurrentText("Light Mode")


    def speichern():
        global deg_mode, theme
        
        deg_mode = grad_radio.isChecked()
        dialog.accept()

        theme_text = combo.currentText()
        if theme_text == "Dark Mode":
            app.setStyleSheet(dark_theme)
            theme = 2
        elif theme_text == "Grey Mode":
            app.setStyleSheet(grey_theme)
            theme = 1
        else:
            app.setStyleSheet(light_theme)
            theme = 0




    speichern_btn = QPushButton("Speichern")
    if theme == 2:  # dark
        speichern_btn.setStyleSheet("color: #e0e0e0; background-color: #232323; border-radius: 6px; padding: 10px;")
    elif theme == 1:  # grey
        speichern_btn.setStyleSheet("color: #f5f5f5; background-color: #616161; border-radius: 6px; padding: 10px;")
    else:  # light
        speichern_btn.setStyleSheet("color: #222831; background-color: #e0e0e0; border-radius: 6px; padding: 10px;")
    speichern_btn.clicked.connect(speichern)

    layout.addWidget(speichern_btn)
    dialog.setLayout(layout)
    dialog.exec()

def finde_ausdruck_vor_fakultaet(text, pos):
    i = pos - 1
    if i < 0:
        return None
    
    klammern = 0

    while i >= 0:
        c = text[i]

        if c == ')':
            klammern += 1
        elif c == '(':
            klammern -= 1
            if klammern < 0:
                break

        if klammern == 0 and c in ("+", "-", "*", "/", "^"):
            break
        
        i -= 1

    start = i + 1
    end = pos

    return (start, end)

def trig_klammer_zu(ausdruck):
    for func in ["radians(", "degrees("]:
        pos = 0
        while True:
            idx = ausdruck.find(func, pos)
            if idx == -1:
                break

            klammer_start = idx + len(func)
            klammer_anzahl = 1
            i = klammer_start

            while i < len(ausdruck) and klammer_anzahl > 0:
                if ausdruck[i] == "(":
                    klammer_anzahl += 1
                elif ausdruck[i] == ")":
                    klammer_anzahl -= 1
                i += 1

            ausdruck = ausdruck[:i] + ")" + ausdruck[i:]
            pos = i + 1
    return ausdruck




def button_gedrueckt(text, anzeige):
    global ans
    if text == "C":
        anzeige.setText("0")
    elif text == "x²":
        text = "²"
        aktuell = anzeige.text()
        if aktuell in ("0", "Syntax Error"):
            anzeige.setText(text)
        else:
            anzeige.setText(aktuell + text)
    elif text == "√":
        text = "√("
        aktuell = anzeige.text()
        if aktuell in ("0", "Syntax Error"):
            anzeige.setText(text)
        else:
            anzeige.setText(aktuell + text)
    elif text == "ln":
        text = "ln("
        aktuell = anzeige.text()
        if aktuell in ("0", "Syntax Error"):
            anzeige.setText(text)
        else:
            anzeige.setText(aktuell + text)
    elif text == "log":
        text = "log("
        aktuell = anzeige.text()
        if aktuell in ("0", "Syntax Error"):
            anzeige.setText(text)
        else:
            anzeige.setText(aktuell + text)
    elif text == "x⁻¹":
        text = "⁻¹"
        aktuell = anzeige.text()
        if aktuell in ("0", "Syntax Error"):
            anzeige.setText(text)
        else:
            anzeige.setText(aktuell + text)
    elif text == "1/x":
        text = "(1/"
        aktuell = anzeige.text()
        if aktuell in ("0", "Syntax Error"):
            anzeige.setText(text)
        else:
            anzeige.setText(aktuell + text)
    elif text == "sin":
        text = "sin("
        aktuell = anzeige.text()
        if aktuell in ("0", "Syntax Error"):
            anzeige.setText(text)
        else:
            anzeige.setText(aktuell + text)
    elif text == "cos":
        text = "cos("
        aktuell = anzeige.text()
        if aktuell in ("0", "Syntax Error"):
            anzeige.setText(text)
        else:
            anzeige.setText(aktuell + text)
    elif text == "tan":
        text = "tan("
        aktuell = anzeige.text()
        if aktuell in ("0", "Syntax Error"):
            anzeige.setText(text)
        else:
            anzeige.setText(aktuell + text)
    elif text == "sin⁻¹":
        text = "sin⁻¹("
        aktuell = anzeige.text()
        if aktuell in ("0", "Syntax Error"):
            anzeige.setText(text)
        else:
            anzeige.setText(aktuell + text)
    elif text == "cos⁻¹":
        text = "cos⁻¹("
        aktuell = anzeige.text()
        if aktuell in ("0", "Syntax Error"):
            anzeige.setText(text)
        else:
            anzeige.setText(aktuell + text)
    elif text == "tan⁻¹":
        text = "tan⁻¹("
        aktuell = anzeige.text()
        if aktuell in ("0", "Syntax Error"):
            anzeige.setText(text)
        else:
            anzeige.setText(aktuell + text)
    elif text == "⌫":
        aktuell = anzeige.text()

        spezial_muster = ["ln(", "log(", "⁻¹", "√(", "(1/", "ANS"]
        gefunden = False

        for muster in spezial_muster:
            if aktuell.endswith(muster):
                neu = aktuell[:-len(muster)]
                anzeige.setText(neu if neu else "0")
                gefunden = True
                break


        if not gefunden:
            if aktuell not in ("0", "Syntax Error", "Math Error!", "Error!") and len(aktuell) > 1:
                anzeige.setText(aktuell[:-1])
                if aktuell == "":
                    anzeige.setText("0")
            else:
                anzeige.setText("0")


    elif text == "=":
        global deg_mode
        
        try:
            aeval = Interpreter()
            ausdruck = anzeige.text()

            pos = len(ausdruck) - 1
            while pos >= 0:
                if ausdruck[pos] == '!':
                    start, end = finde_ausdruck_vor_fakultaet(ausdruck, pos)
                    if start is not None:
                        teil = ausdruck[start:end]
                        ausdruck = ausdruck[:start] + f"factorial({teil})" + ausdruck[pos+1:]
                        pos = start - 1
                    else:
                        pos -= 1
                else:
                    pos -= 1

            aeval.symtable["factorial"] = factorial
            aeval.symtable["sqrt"] = sqrt
            aeval.symtable["log"] = log
            aeval.symtable["log10"] = log10
            aeval.symtable["sin"] = sin
            aeval.symtable["cos"] = cos
            aeval.symtable["tan"] = tan
            aeval.symtable["asin"] = asin
            aeval.symtable["acos"] = acos
            aeval.symtable["atan"] = atan

            ausdruck = ausdruck.replace("^", "**")
            ausdruck = ausdruck.replace("ANS", ans)
            ausdruck = ausdruck.replace("%", "/100")
            ausdruck = ausdruck.replace("²", "**2")
            ausdruck = ausdruck.replace("√", "sqrt") 
            ausdruck = ausdruck.replace("⁻¹", "**-1")
            ausdruck = ausdruck.replace("log", "log10")
            ausdruck = ausdruck.replace("ln", "log")
            ausdruck = ausdruck.replace(",", ".") 
            ausdruck = ausdruck.replace("π", "3.141592653589793")
            ausdruck = ausdruck.replace("e", "2.718281828459045")
            
            if deg_mode:
                ausdruck = ausdruck.replace("sin(", "sin(radians(")
                ausdruck = ausdruck.replace("cos(", "cos(radians(")
                ausdruck = ausdruck.replace("tan(", "tan(radians(")
                ausdruck = ausdruck.replace("sin⁻¹(", "degrees(asin(")
                ausdruck = ausdruck.replace("cos⁻¹(", "degrees(acos(")
                ausdruck = ausdruck.replace("tan⁻¹(", "degrees(atan(")
                
                ausdruck = trig_klammer_zu(ausdruck)
            else:
                ausdruck = ausdruck.replace("sin⁻¹(", "asin(")
                ausdruck = ausdruck.replace("cos⁻¹(", "acos(")
                ausdruck = ausdruck.replace("tan⁻¹(", "atan(")

            ergebnis = str(aeval(ausdruck))
            ans = ergebnis
            if ergebnis == "None":
                anzeige.setText("Syntax Error")
            else:
                anzeige.setText(ergebnis)
        except Exception as e:
            if isinstance(e, SyntaxError):
                anzeige.setText("Syntax Error!")
            elif isinstance(e, OverflowError):
                anzeige.setText("Math Error!")
            else:
                anzeige.setText("Error!")
    else:
        aktuell = anzeige.text()
        if aktuell in ("0", "Syntax Error", "Math Error!", "Error!"):
            anzeige.setText(text)
        else:
            anzeige.setText(aktuell + text)
    
def main():
    app = QApplication(sys.argv)

    settings = QSettings("Minirechner", "Settings")
    global theme
    theme = int(settings.value("theme", 0))

    window = QWidget()
    window.setWindowTitle("Calculator")
    window.setFixedSize(450, 600)

    einstellungen = QWidget()
    einstellungen.setWindowTitle("Settings")
    einstellungen.setFixedSize(300, 300)
    

    layout = QGridLayout()

    einstellungs_btn = QPushButton("⚙")
    einstellungs_btn.clicked.connect(lambda: einstellungen_oeffnen(window, app))
    layout.addWidget(einstellungs_btn, 0, 3)


    anzeige = QLabel("0")
    anzeige.setObjectName("DisplayLabel")
    anzeige.setMinimumHeight(50)

    layout.addWidget(anzeige, 0, 0, 1, 3)

    btns = [
        ("7",     1, 0), ("8",     1, 1), ("9",     1, 2), ("+", 1, 3),
        ("4",     2, 0), ("5",     2, 1), ("6",     2, 2), ("-", 2, 3),
        ("1",     3, 0), ("2",     3, 1), ("3",     3, 2), ("*", 3, 3),
        ("0",     4, 0), ("(",     4, 1), (")",     4, 2), ("/", 4, 3),
        ("^",     5, 0), ("x²",    5, 1), ("x⁻¹",   5, 2), ("√", 5, 3),
        ("log",   6, 0), ("ln",    6, 1), ("%",     6, 2), ("!", 6, 3),
        ("sin",   7, 0), ("cos",   7, 1), ("tan",   7, 2), ("π", 7, 3), 
        ("sin⁻¹", 8, 0), ("cos⁻¹", 8, 1), ("tan⁻¹", 8, 2), ("e", 8, 3),
        ("ANS",   9, 0), ("C",     9, 1), ("⌫",     9, 2), ("=", 9, 3)
    ]

    for text, row, col in btns:
        btn = QPushButton(text)
        btn.clicked.connect(lambda _, t=text: button_gedrueckt(t, anzeige))
        layout.addWidget(btn, row, col)

    window.setLayout(layout)
    window.show()

    if theme == 2:
        app.setStyleSheet(dark_theme)
    elif theme == 1:
        app.setStyleSheet(grey_theme)
    else:
        app.setStyleSheet(light_theme)

    def save_settings():
        settings.setValue("theme", theme)
    app.aboutToQuit.connect(save_settings)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
