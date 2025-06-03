import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
from collections import defaultdict

# ---------- Tooltip-Klasse ----------
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _event):
        if self.tooltip or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tooltip,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Arial", 9),
        )
        label.pack(ipadx=3, ipady=2)

    def hide(self, _event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


# ---------- Datenstrukturen ----------
noten_daten = {}

allgemein_faecher = ["Deutsch", "Religion/Ethik", "Sozialkunde", "Sport", "Wirtschaftslehre"]
beruflich_faecher = [f"LF{i}" for i in range(1, 13)]
faecher_liste = ["de", "et", "sk", "sp", "wl"] + [f"LF{i}" for i in range(1, 13)]
fach_map = {
    "Deutsch": "de",
    "Religion/Ethik": "et",
    "Sozialkunde": "sk",
    "Sport": "sp",
    "Wirtschaftslehre": "wl",
}
reverse_map = {v: k for k, v in fach_map.items()}
reverse_map.update({lf: lf for lf in beruflich_faecher})

current_filename = None

# ---------- Funktionen ----------
def check_name(*_args):
    name = name_var.get().strip()
    add_btn["state"] = "normal" if name else "disabled"

def validate_note(entry):
    val = entry.get().strip()
    if not val:
        entry.configure(background="white")
    elif val.isdigit() and 1 <= int(val) <= 6:
        entry.configure(background="white")
    else:
        entry.configure(background="#fbb")

def noten_hinzufuegen(_event=None):
    name = name_var.get().strip()
    if not name:
        return

    fehler = False
    grades = []
    for fach, entry in note_eingaben.items():
        val = entry.get().strip()
        validate_note(entry)
        if val:
            if val.isdigit() and 1 <= int(val) <= 6:
                kuerzel = fach_map.get(fach, fach)
                grades.append({"Fach": kuerzel, "Note": int(val)})
            else:
                fehler = True

    if fehler:
        messagebox.showerror("Ungültige Eingabe", "Noten müssen Zahlen von 1 bis 6 sein.")
        return
    if not grades:
        messagebox.showinfo("Keine Note", "Bitte mindestens eine Note eingeben.")
        return

    noten_daten[name] = grades
    name_var.set("")
    for entry in note_eingaben.values():
        entry.delete(0, tk.END)
        entry.configure(background="white")

    csv_speichern_btn["state"] = "normal"
    daten_anzeigen()
    name_entry.focus_set()

def berechne_durchschnitt(name, fachgruppe):
    kuerzel_gruppe = [fach_map.get(f, f) for f in fachgruppe]
    noten = [e["Note"] for e in noten_daten.get(name, []) if e["Fach"] in kuerzel_gruppe]
    return round(sum(noten) / len(noten), 1) if noten else 0

def berechne_gesamtnote(name):
    dn1 = berechne_durchschnitt(name, allgemein_faecher)
    dn2 = berechne_durchschnitt(name, beruflich_faecher)
    g = round((dn1 + 2 * dn2) / 3, 1)
    return dn1, dn2, g

def daten_anzeigen():
    ausgabe.configure(state="normal")
    ausgabe.delete("1.0", tk.END)
    for name in noten_daten:
        dn1, dn2, g = berechne_gesamtnote(name)
        ausgabe.insert(tk.END, f"{name}:\n")
        for eintrag in noten_daten[name]:
            fach_name = reverse_map.get(eintrag["Fach"], eintrag["Fach"])
            ausgabe.insert(tk.END, f"  {fach_name}: {eintrag['Note']}\n")
        ausgabe.insert(tk.END, f"  → DN1: {dn1} | DN2: {dn2} | Gesamtnote: {g}\n\n")
    ausgabe.configure(state="disabled")

def csv_laden():
    global current_filename
    file = filedialog.askopenfilename(filetypes=[("CSV Dateien", "*.csv")])
    if not file:
        return
    current_filename = file.split("/")[-1]
    noten_daten.clear()
    with open(file, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("Name") or row.get("\ufeffName")
            if not name:
                continue
            noten_daten[name] = []
            for fach in faecher_liste:
                val = row.get(fach)
                if val and val.isdigit():
                    noten_daten[name].append({"Fach": fach, "Note": int(val)})
    datei_label.configure(text=f"Datei geladen: {current_filename}")
    csv_speichern_btn["state"] = "normal" if noten_daten else "disabled"
    daten_anzeigen()

def csv_speichern():
    if not noten_daten:
        return
    progress_win = tk.Toplevel(root)
    progress_win.title("Speichern...")
    progress_win.geometry("300x80")
    ttk.Label(progress_win, text="CSV wird gespeichert...").pack(pady=10)
    prog = ttk.Progressbar(progress_win, mode="indeterminate")
    prog.pack(fill="x", padx=20, pady=5)
    prog.start(10)
    progress_win.transient(root)
    root.update_idletasks()

    file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Dateien", "*.csv")])
    if not file:
        prog.stop()
        progress_win.destroy()
        return
    with open(file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name"] + faecher_liste)
        for name, notenliste in noten_daten.items():
            noten_map = {e["Fach"]: e["Note"] for e in notenliste}
            zeile = [name] + [noten_map.get(fach, "") for fach in faecher_liste]
            writer.writerow(zeile)

    prog.stop()
    progress_win.destroy()
    messagebox.showinfo("Erfolg", "CSV wurde gespeichert.")


# ---------- GUI ----------
root = tk.Tk()
root.title("Notenrechner Abschlusszeugnis")
root.geometry("520x700")

# Azure-Theme einbinden (azure.tcl liegt in „azure/azure.tcl“ neben diesem Skript)
root.tk.call("source", "azure/azure.tcl")
root.tk.call("set_theme", "dark")
ttk.Style().theme_use("azure-dark")

# Name-Eingabe
ttk.Label(root, text="Name:").pack(pady=(10, 0))
name_var = tk.StringVar()
name_var.trace_add("write", check_name)
name_entry = ttk.Entry(root, textvariable=name_var)
name_entry.pack(pady=5)
name_entry.bind("<Return>", lambda e: grade_entries[0].focus_set())

# Grade-Bereich mit Scrollbar
container = ttk.Frame(root)
container.pack(fill="both", expand=True, padx=10, pady=(5, 0))

canvas = tk.Canvas(container, height=300)
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Fach-Gruppen beschriften und Einträge anlegen
ttk.Label(scrollable_frame, text="Allgemein:", font=("Arial", 10, "bold")).pack(anchor="center", pady=(5, 0))
note_eingaben = {}
grade_entries = []

for fach in allgemein_faecher:
    frame = ttk.Frame(scrollable_frame)
    frame.pack(pady=2)  # nicht mehr fill="x", damit der Frame nur so breit wie nötig ist
    lbl = ttk.Label(frame, text=fach + ":", width=20, anchor="w")
    lbl.pack(side="left")
    Tooltip(lbl, "Gib eine Zahl von 1 bis 6 ein")
    entry = ttk.Entry(frame, width=5)
    entry.pack(side="left")
    entry.bind("<KeyRelease>", lambda e, en=entry: validate_note(en))
    note_eingaben[fach] = entry
    grade_entries.append(entry)

ttk.Label(scrollable_frame, text="Beruflich:", font=("Arial", 10, "bold")).pack(anchor="center", pady=(10, 0))
for fach in beruflich_faecher:
    frame = ttk.Frame(scrollable_frame)
    frame.pack(pady=2)  # nicht mehr fill="x"
    lbl = ttk.Label(frame, text=fach + ":", width=20, anchor="w")
    lbl.pack(side="left")
    Tooltip(lbl, "Gib eine Zahl von 1 bis 6 ein")
    entry = ttk.Entry(frame, width=5)
    entry.pack(side="left")
    entry.bind("<KeyRelease>", lambda e, en=entry: validate_note(en))
    note_eingaben[fach] = entry
    grade_entries.append(entry)

# Buttons
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)
add_btn = ttk.Button(button_frame, text="➕ Hinzufügen", state="disabled", command=noten_hinzufuegen)
add_btn.grid(row=0, column=0, padx=5)
load_btn = ttk.Button(button_frame, text="📂 CSV Laden", command=csv_laden)
load_btn.grid(row=0, column=1, padx=5)
csv_speichern_btn = ttk.Button(button_frame, text="💾 CSV Speichern", state="disabled", command=csv_speichern)
csv_speichern_btn.grid(row=0, column=2, padx=5)

# Tastenkürzel
root.bind_all("<Control-h>", noten_hinzufuegen)

# Label für geladene Datei
datei_label = ttk.Label(root, text="Keine Datei geladen", font=("Arial", 9, "italic"))
datei_label.pack(pady=(0, 10))

# Ausgabe-Feld
ausgabe = tk.Text(root, height=12, width=65, state="disabled")
ausgabe.pack(pady=5)

root.mainloop()
