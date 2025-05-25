import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
from collections import defaultdict

daten = defaultdict(dict)
noten_daten = {}

# Fachgruppen
allgemein_faecher = [
    "Deutsch",
    "Religion/Ethik",
    "Sozialkunde",
    "Sport",
    "Wirtschaftslehre",
]
beruflich_faecher = [
    "LF1",
    "LF2",
    "LF3",
    "LF4",
    "LF5",
    "LF6",
    "LF7",
    "LF8",
    "LF9",
    "LF10",
    "LF11",
    "LF12",
]

# Alle Fächer in gewünschter Reihenfolge
faecher_liste = [
    "de",
    "et",
    "sk",
    "sp",
    "wl",
    "LF1",
    "LF2",
    "LF3",
    "LF4",
    "LF5",
    "LF6",
    "LF7",
    "LF8",
    "LF9",
    "LF10",
    "LF11",
    "LF12",
]

# Mapping von Langnamen auf Kürzel
fach_map = {
    "Deutsch": "de",
    "Religion/Ethik": "et",
    "Sozialkunde": "sk",
    "Sport": "sp",
    "Wirtschaftslehre": "wl",
}

# Reverse Mapping für Anzeige
reverse_map = {v: k for k, v in fach_map.items()}
reverse_map.update({lf: lf for lf in beruflich_faecher})


def noten_hinzufuegen():
    name = name_entry.get().strip()
    if not name:
        messagebox.showerror("Fehler", "Bitte Namen eingeben.")
        return

    noten_daten[name] = []
    for fach, entry in note_eingaben.items():
        val = entry.get().strip()
        if val.isdigit():
            note = int(val)
            if 1 <= note <= 6:
                kuerzel = fach_map.get(fach, fach)
                noten_daten[name].append({"Fach": kuerzel, "Note": note})

    name_entry.delete(0, tk.END)
    for entry in note_eingaben.values():
        entry.delete(0, tk.END)

    daten_anzeigen()


def berechne_durchschnitt(name, fachgruppe):
    kuerzel_gruppe = [fach_map.get(f, f) for f in fachgruppe]
    noten = [
        e["Note"] for e in noten_daten.get(name, []) if e["Fach"] in kuerzel_gruppe
    ]
    if not noten:
        return 0
    return round(sum(noten) / len(noten), 1)


def berechne_gesamtnote(name):
    dn1 = berechne_durchschnitt(name, allgemein_faecher)
    dn2 = berechne_durchschnitt(name, beruflich_faecher)
    gesamt = round((dn1 + 2 * dn2) / 3, 1)
    return dn1, dn2, gesamt


def daten_anzeigen():
    ausgabe.delete(1.0, tk.END)
    for name in noten_daten:
        dn1, dn2, g = berechne_gesamtnote(name)
        ausgabe.insert(tk.END, f"{name}:\n")
        for eintrag in noten_daten[name]:
            fach_name = reverse_map.get(eintrag["Fach"], eintrag["Fach"])
            ausgabe.insert(tk.END, f"  {fach_name}: {eintrag['Note']}\n")
        ausgabe.insert(tk.END, f"  → DN1: {dn1} | DN2: {dn2} | Gesamtnote: {g}\n\n")


def csv_laden():
    file = filedialog.askopenfilename(filetypes=[("CSV Dateien", "*.csv")])
    if not file:
        return

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
    daten_anzeigen()


def csv_speichern():
    file = filedialog.asksaveasfilename(
        defaultextension=".csv", filetypes=[("CSV Dateien", "*.csv")]
    )
    if not file:
        return
    with open(file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name"] + faecher_liste)

        for name, notenliste in noten_daten.items():
            noten_map = {e["Fach"]: e["Note"] for e in notenliste}
            zeile = [name] + [noten_map.get(fach, "") for fach in faecher_liste]
            writer.writerow(zeile)


# GUI
root = tk.Tk()
root.tk.call("source", "azure/azure.tcl")
root.tk.call("set_theme", "dark")
ttk.Style().theme_use("azure-light")
root.title("Notenrechner Abschlusszeugnis")
root.geometry("500x600")
root.configure(bg="#f0f0f0")

ttk.Label(root, text="Name:").pack()
name_entry = ttk.Entry(root)
name_entry.pack(pady=5)

note_eingaben = {}

ttk.Label(root, text="Noten eingeben:").pack()

for fach in allgemein_faecher + beruflich_faecher:
    frame = ttk.Frame(root)
    frame.pack(pady=2)
    ttk.Label(frame, text=fach + ":", width=20, anchor="w").pack(side="left")
    entry = ttk.Entry(frame, width=5)
    entry.pack(side="left")
    note_eingaben[fach] = entry

ttk.Button(root, text="➕ Hinzufügen", command=noten_hinzufuegen).pack(pady=10)
ttk.Button(root, text="📂 CSV Laden", command=csv_laden).pack(pady=2)
ttk.Button(root, text="💾 CSV Speichern", command=csv_speichern).pack(pady=2)

ausgabe = tk.Text(root, height=20, width=60)
ausgabe.pack(pady=10)

root.mainloop()
