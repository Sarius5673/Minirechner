from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QGridLayout
from asteval import Interpreter
import sys
from math import sqrt, log, log10, factorial

ans = "0"

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
    elif text == "⌫":
        aktuell = anzeige.text()

        spezial_muster = ["ln(", "log(", "⁻¹", "√(", "(1/", "ANS"]
        gefunden = False

        for muster in spezial_muster:
            if aktuell.endswith(muster):
                anzeige.setText(aktuell[:-len(muster)])
                gefunden = True
                break

        if not gefunden:
            if aktuell not in ("0", "Syntax Error", "Math Error!", "Error!") and len(aktuell) > 1:
                anzeige.setText(aktuell[:-1])
            else:
                anzeige.setText("0")

    elif text == "=":
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

    window = QWidget()
    window.setWindowTitle("Mein Taschenrechner")
    window.setFixedSize(300, 400)

    layout = QGridLayout()

    anzeige = QLabel("0")
    layout.addWidget(anzeige, 0, 0, 1, 3)

    btns = [
        ("7", 1, 0),   ("8", 1, 1),   ("9", 1, 2),   ("+", 1, 3),
        ("4", 2, 0),   ("5", 2, 1),   ("6", 2, 2),   ("-", 2, 3),
        ("1", 3, 0),   ("2", 3, 1),   ("3", 3, 2),   ("*", 3, 3),
        ("0", 4, 0),   ("(", 4, 1),   (")", 4, 2),   ("/", 4, 3),
        ("^", 5, 0),   ("x²", 5, 1),  ("x⁻¹", 5, 2), ("√", 5, 3),
        ("log", 6, 0), ("ln", 6, 1),  ("%", 6, 2),   ("!", 6, 3),
        ("π", 7, 0),   ("e", 7, 1),
        ("ANS", 8, 0), ("C", 8, 1),   ("⌫", 8, 2),   ("=", 8, 3)
    ]

    for text, row, col in btns:
        btn = QPushButton(text)
        btn.clicked.connect(lambda _, t=text: button_gedrueckt(t, anzeige))
        layout.addWidget(btn, row, col)

    window.setLayout(layout)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
