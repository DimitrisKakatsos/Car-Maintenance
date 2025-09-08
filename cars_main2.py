# -*- coding: utf-8 -*-
# Compatible with Python 3.4 and Windows XP, using only the Python standard library
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkinter import font
import csv
import os

csv_file = "Cars_updated.csv"
current_font_size = 10

# Column names
COLUMNS = [
    "Αυτοκίνητα", "Αριθμός αυ/του", "Χιλιόμετρα", "Ημερομηνία(ΤΠΣ)", "Ημερομηνία ΑΕΚΟ",
    "3μηναια", "5κ χλμ", "2χρονια λαδια", "2χρονια βαλβ", "Συνολικά Χιλιόμετρα", "Χλμ τον Μηνα"
]

# Data storage: list of dicts
cars = []

def load_data():
    global cars
    cars = []
    if not os.path.exists(csv_file):
        return
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Ensure all columns exist
            for col in COLUMNS:
                if col not in row:
                    row[col] = "" if col not in ["Συνολικά Χιλιόμετρα", "Χλμ τον Μηνα"] else 0
            # Convert numeric fields
            for col in ["Αριθμός αυ/του", "Χιλιόμετρα", "5κ χλμ", "Συνολικά Χιλιόμετρα", "Χλμ τον Μηνα"]:
                try:
                    row[col] = int(row[col])
                except:
                    row[col] = 0
            cars.append(row)

def save_to_csv():
    global cars
    with open(csv_file, "w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for car in cars:
            writer.writerow(car)
    messagebox.showinfo(u"Success", u"Data saved successfully to {}.".format(csv_file))

def update_treeview():
    tree.delete(*tree.get_children())
    for idx, car in enumerate(cars):
        values = [car.get(col, "") for col in tree["columns"]]
        tree.insert("", "end", iid=str(idx), values=values)

def select_car(event):
    selected_item = tree.selection()
    if not selected_item:
        return
    index = int(selected_item[0])
    car = cars[index]
    car_entry.delete(0, tk.END)
    car_entry.insert(0, car["Αυτοκίνητα"])
    number_entry.delete(0, tk.END)
    number_entry.insert(0, car["Αριθμός αυ/του"])
    km_entry.delete(0, tk.END)
    km_entry.insert(0, car["Χιλιόμετρα"])
    date_entry.delete(0, tk.END)
    date_entry.insert(0, car["Ημερομηνία(ΤΠΣ)"])
    aeko_entry.delete(0, tk.END)
    aeko_entry.insert(0, car["Ημερομηνία ΑΕΚΟ"])

def add_car():
    global cars
    try:
        car_name = car_entry.get()
        number = int(number_entry.get()) if number_entry.get().isdigit() else None
        kilometers = int(km_entry.get()) if km_entry.get().isdigit() else None
        date = date_entry.get()
        aeko_date = aeko_entry.get()
        if car_name == "" or number is None or kilometers is None or date == "":
            raise ValueError(u"Symplirose ola ta pedia.")
        try:
            valid_date = datetime.strptime(date, "%d-%m-%Y")
        except ValueError:
            raise ValueError(u"Lathos morfi Imerominias. Xrisimopoiese DD-MM-YYYY.")
        three_months_later = (valid_date + timedelta(days=90)).strftime("%d-%m-%Y")
        if aeko_date:
            try:
                valid_aeko = datetime.strptime(aeko_date, "%d-%m-%Y")
                two_years_later = (valid_aeko + timedelta(days=730)).strftime("%d-%m-%Y")
            except ValueError:
                raise ValueError(u"Λάθος μορφή Ημερομηνίας ΑΕΚΟ. Χρησιμοποίησε DD-MM-YYYY.")
        else:
            two_years_later = ""
        new_car = {
            "Αυτοκίνητα": car_name,
            "Αριθμός αυ/του": number,
            "Χιλιόμετρα": kilometers,
            "Ημερομηνία(ΤΠΣ)": date,
            "Ημερομηνία ΑΕΚΟ": aeko_date,
            "3μηναια": three_months_later,
            "5κ χλμ": kilometers + 5000,
            "2χρονια λαδια": two_years_later,
            "2χρονια βαλβ": two_years_later,
            "Συνολικά Χιλιόμετρα": 0,
            "Χλμ τον Μηνα": 0
        }
        cars.append(new_car)
        update_treeview()
        messagebox.showinfo(u"Epitixia", u"To aftokinito prostethike.")
    except ValueError as e:
        messagebox.showerror(u"Σφάλμα", str(e))

def update_kilometers():
    global cars
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror(u"Καμία Επιλογή", u"Επίλεξε ένα αυτοκίνητο για ενημέρωση.")
        return
    index = int(selected_item[0])
    try:
        added_km = int(km_entry.get())
        if added_km < 0:
            raise ValueError(u"Τα χιλιόμετρα πρέπει να είναι θετικός αριθμός.")
        car = cars[index]
        old_km = int(car["Χιλιόμετρα"])
        new_km = old_km + added_km
        target_km = int(car["5κ χλμ"])
        total_km = int(car.get("Συνολικά Χιλιόμετρα", 0))
        new_total_km = total_km + added_km
        car["Συνολικά Χιλιόμετρα"] = new_total_km
        if new_km >= target_km:
            if messagebox.askyesno(u"Syntirisi", u"{} eftase ta {}xlm. Egine allagi ladion;".format(car["Αυτοκίνητα"], new_km)):
                car["5κ χλμ"] = new_km + 5000
        car["Χιλιόμετρα"] = new_km
        update_treeview()
        messagebox.showinfo(u"Enimerothike", u"Ta xiliometra enimerothikan se {}.\nSynolo xiliometron: {}".format(new_km, new_total_km))
    except ValueError as e:
        messagebox.showerror(u"Σφάλμα", u"Μη έγκυρη είσοδος: {}".format(e))

def update_car():
    global cars
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror(u"No Selection", u"Please select a car to update.")
        return
    index = int(selected_item[0])
    try:
        car_name = car_entry.get()
        number = int(number_entry.get()) if number_entry.get().isdigit() else None
        kilometers = int(km_entry.get()) if km_entry.get().isdigit() else None
        date = date_entry.get()
        aeko_date = aeko_entry.get()
        if car_name == "" or number is None or kilometers is None or date == "":
            raise ValueError(u"Symplirose ola ta ypoxreotika pedia.")
        try:
            valid_date = datetime.strptime(date, "%d-%m-%Y")
            three_months_later = (valid_date + timedelta(days=90)).strftime("%d-%m-%Y")
        except ValueError:
            raise ValueError(u"Lathos morfi Imerominias. Xrisimopoiese DD-MM-YYYY.")
        if aeko_date:
            try:
                valid_aeko = datetime.strptime(aeko_date, "%d-%m-%Y")
                two_years_later = (valid_aeko + timedelta(days=730)).strftime("%d-%m-%Y")
            except ValueError:
                raise ValueError(u"Λάθος μορφή Ημερομηνίας ΑΕΚΟ. Χρησιμοποίησε DD-MM-YYYY.")
        else:
            two_years_later = ""
        car = cars[index]
        car["Αυτοκίνητα"] = car_name
        car["Αριθμός αυ/του"] = number
        car["Χιλιόμετρα"] = kilometers
        car["Ημερομηνία(ΤΠΣ)"] = date
        car["3μηναια"] = three_months_later
        car["5κ χλμ"] = kilometers + 5000
        car["Ημερομηνία ΑΕΚΟ"] = aeko_date
        car["2χρονια λαδια"] = two_years_later
        car["2χρονια βαλβ"] = two_years_later
        update_treeview()
        messagebox.showinfo(u"Epitixia", u"Ta stoixeia enimerothikan.")
    except ValueError as e:
        messagebox.showerror(u"Σφάλμα", str(e))

def check_warnings():
    global cars
    warnings = []
    today = datetime.today()
    for car in cars:
        car_name = car["Αυτοκίνητα"]
        car_id = car["Αριθμός αυ/του"]
        # 3μηνη συντήρηση
        val_3m = car["3μηναια"]
        if isinstance(val_3m, str) and val_3m.strip() != "" and val_3m != "nan":
            try:
                three_months_date = datetime.strptime(val_3m, "%d-%m-%Y")
                if today >= three_months_date:
                    warnings.append(u"({}, {}) xreiazetai 3mini syntirisi (Imerominia: {}).".format(car_name, car_id, three_months_date.strftime('%d-%m-%Y')))
            except Exception:
                pass
        # 5κ χλμ
        val_km = car["Χιλιόμετρα"]
        val_5k = car["5κ χλμ"]
        if val_km is not None and val_5k is not None and str(val_km) != 'nan' and str(val_5k) != 'nan':
            try:
                mileage = int(val_km)
                next_mileage = int(val_5k)
                if mileage >= next_mileage:
                    warnings.append(u"({}, {}) exei ftasei ta {}xlm kai xreiazetai allagi ladion (Orio: {}xlm).".format(car_name, car_id, mileage, next_mileage))
            except Exception:
                pass
        # 2ετής αλλαγή λαδιών/βαλβίδων
        val_2y = car["2χρονια λαδια"]
        if isinstance(val_2y, str) and val_2y.strip() != "" and val_2y != "nan":
            try:
                two_years_date = datetime.strptime(val_2y, "%d-%m-%Y")
                if today >= two_years_date:
                    warnings.append(u"({}, {}) xreiazetai allagi ladion & valvidon (Imerominia: {}).".format(car_name, car_id, two_years_date.strftime('%d-%m-%Y')))
            except Exception:
                pass
    if warnings:
        big_warning("Syntirisi Apiteitai", "\n".join(warnings))
    else:
        messagebox.showinfo(u"Ola kala!", u"Ola ta aftokinita einai entos prodiagrafon!")

def transfer_monthly_km():
    global cars
    for car in cars:
        car["Month KM"] = car.get("Total KM", 0)
        car["Total KM"] = 0
    update_treeview()
    messagebox.showinfo("Success", "Month KM updated and Total KM reset to zero.")


def setup_form():
    outer_frame = tk.Frame(root)
    outer_frame.pack(fill=tk.X, pady=10)
    canvas = tk.Canvas(outer_frame, height=100)
    scrollbar = tk.Scrollbar(outer_frame, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    canvas.pack(side=tk.TOP, fill=tk.X, expand=True)
    form_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=form_frame, anchor="nw")
    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    form_frame.bind("<Configure>", on_configure)
    labels = ["Αυτοκίνητα", "Αριθμός αυ/του", "Νέα Χλμ (προσθήκη)", "Ημερομηνία(ΤΠΣ)(DD-MM-YYYY)", "Ημερομηνία ΑΕΚΟ (DD-MM-YYYY)"]
    entries = []
    for i, label in enumerate(labels):
        tk.Label(form_frame, text=label).grid(row=0, column=i, padx=10)
        entry = tk.Entry(form_frame, width=25)
        entry.grid(row=1, column=i, padx=10)
        entries.append(entry)
    global car_entry, number_entry, km_entry, date_entry, aeko_entry
    car_entry, number_entry, km_entry, date_entry, aeko_entry = entries
    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)
    tk.Button(button_frame, text="Προσθήκη Οχήματος", command=add_car).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Ενημέρωση Οχήματος", command=update_car).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Ενημέρωση Χιλιομέτρων", command=update_kilometers).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Check Warnings", command=check_warnings).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Metaforesa Xlm ton Mina", command=transfer_monthly_km).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Αποθήκευση στο EXCEL", command=save_to_csv).pack(side=tk.LEFT, padx=5)

# Load data from the CSV file
load_data()

# Set up the Tkinter window
root = tk.Tk()
root.title("Car Maintenance Tracker")
root.geometry("800x600")

# Create a frame to hold the Treeview
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# Create Treeview widget
columns_to_show = COLUMNS  # Show all columns, including 'Month KM'
tree = ttk.Treeview(frame, columns=columns_to_show, show="headings")
tree.pack(fill=tk.BOTH, expand=True)
tree.bind("<<TreeviewSelect>>", select_car)

# Add scrollbars
scrollbar_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
scrollbar_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

# Add column headings
for col in columns_to_show:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER, width=150)

# Populate initial data
update_treeview()

# Add input form and buttons
setup_form()

def apply_font_size():
    f = font.Font(size=current_font_size)
    style = ttk.Style()
    style.configure("Treeview", font=(None, current_font_size))
    style.configure("Treeview.Heading", font=(None, current_font_size, 'bold'))
    for widget in root.winfo_children():
        apply_font_to_widget(widget, f)

def apply_font_to_widget(widget, font_obj):
    try:
        widget.configure(font=font_obj)
    except:
        pass
    for child in widget.winfo_children():
        apply_font_to_widget(child, font_obj)

def zoom_in():
    global current_font_size
    current_font_size += 1
    apply_font_size()

def zoom_out():
    global current_font_size
    if current_font_size > 6:
        current_font_size -= 1
        apply_font_size()

zoom_frame = tk.Frame(root)
zoom_frame.pack(pady=5)
tk.Button(zoom_frame, text="Zoom In", command=zoom_in).pack(side=tk.LEFT, padx=5)
tk.Button(zoom_frame, text="Zoom Out", command=zoom_out).pack(side=tk.LEFT, padx=5)

def big_warning(title, message):
    win = tk.Toplevel(root)
    win.title(title)
    win.grab_set()
    win.geometry("600x300")
    win.attributes('-topmost', True)
    label = tk.Label(win, text=message, font=("Arial", 18, "bold"), fg="red", wraplength=550, justify="left")
    label.pack(padx=20, pady=40)
    btn = tk.Button(win, text="OK", font=("Arial", 16), command=win.destroy)
    btn.pack(pady=10)
    win.focus_set()

root.mainloop()
