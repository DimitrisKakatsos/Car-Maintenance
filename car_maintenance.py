import tkinter as tk
from tkinter import ttk, messagebox  # Import messagebox directly
from datetime import datetime, timedelta
from tkinter import font
import pandas as pd


csv_file = "Cars_updated2.csv"
current_font_size = 10

def load_data():
    """Load data from the CSV file into a DataFrame and format dates."""
    try:
        df = pd.read_csv(csv_file, encoding="utf-8-sig")
        if "Συνολικά Χιλιόμετρα" not in df.columns:
            df["Συνολικά Χιλιόμετρα"] = 0

        # Normalize date formats
        date_columns = ["Ημερομηνία", "3μηναια", "2χρονια λαδια", "2χρονια βαλβ"]
        df = normalize_date_format(df, date_columns)
        return df
    except FileNotFoundError:
        print(f"{csv_file} not found. Starting with an empty dataset.")
        return pd.DataFrame(columns=["Αυτοκίνητα", "Αριθμός αυ/του", "Χιλιόμετρα", "Ημερομηνία(ΤΠΣ)", "Ημερομηνία ΑΕΚΟ", "3μηναια", "5κ χλμ", "2χρονια λαδια", "2χρονια βαλβ"])

def update_treeview():
    """Refresh the Treeview to display the current DataFrame."""
    global df
    date_columns = ["Ημερομηνία(ΤΠΣ)", "Ημερομηνία ΑΕΚΟ", "3μηναια", "2χρονια λαδια", "2χρονια βαλβ"]

    df = normalize_date_format(df, date_columns)  # Normalize before display
    tree.delete(*tree.get_children())
    for index, row in df.iterrows():
        tree.insert("", "end", iid=index, values=list(row))

def normalize_date_format(df, date_columns):
    """Ensure all specified date columns are in DD-MM-YYYY format."""
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="%d-%m-%Y", errors="coerce").dt.strftime("%d-%m-%Y")
    return df


def select_car(event):
    selected_item = tree.selection()
    if not selected_item:
        return
    index = int(selected_item[0])
    row = df.iloc[index]
    car_entry.delete(0, tk.END)
    car_entry.insert(0, row["Αυτοκίνητα"])
    number_entry.delete(0, tk.END)
    number_entry.insert(0, row["Αριθμός αυ/του"])
    km_entry.delete(0, tk.END)
    km_entry.insert(0, row["Χιλιόμετρα"])
    date_entry.delete(0, tk.END)
    date_entry.insert(0, row["Ημερομηνία(ΤΠΣ)"])

def add_car():
    global df
    try:
        # Εισαγωγή πεδίων
        car_name = car_entry.get()
        number = int(number_entry.get()) if number_entry.get().isdigit() else None
        kilometers = int(km_entry.get()) if km_entry.get().isdigit() else None
        date = date_entry.get()
        aeko_date = aeko_entry.get()

        # Έλεγχος υποχρεωτικών πεδίων
        if car_name == "" or number is None or kilometers is None or date == "":
            raise ValueError("Συμπλήρωσε όλα τα πεδία.")

        # Έλεγχος μορφής ημερομηνιών
        try:
            valid_date = datetime.strptime(date, "%d-%m-%Y")
        except ValueError:
            raise ValueError("Λάθος μορφή Ημερομηνίας. Χρησιμοποίησε DD-MM-YYYY.")
        
        three_months_later = (valid_date + timedelta(days=90)).strftime("%d-%m-%Y")

        # Αν υπάρχει ημερομηνία ΑΕΚΟ, υπολόγισε 2 χρόνια
        if aeko_date:
            try:
                valid_aeko = datetime.strptime(aeko_date, "%d-%m-%Y")
                two_years_later = (valid_aeko + timedelta(days=730)).strftime("%d-%m-%Y")
            except ValueError:
                raise ValueError("Λάθος μορφή Ημερομηνίας ΑΕΚΟ. Χρησιμοποίησε DD-MM-YYYY.")
        else:
            valid_aeko = None
            two_years_later = ""

        # Δημιουργία γραμμής
        new_row = {
            "Αυτοκίνητα": car_name,
            "Αριθμός αυ/του": number,
            "Χιλιόμετρα": kilometers,
            "Ημερομηνία(ΤΠΣ)": date,
            "Ημερομηνία ΑΕΚΟ": aeko_date,
            "3μηναια": three_months_later,
            "5κ χλμ": kilometers + 5000,
            "2χρονια λαδια": two_years_later,
            "2χρονια βαλβ": two_years_later,
        }

        # Προσθήκη
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        update_treeview()
        messagebox.showinfo("Επιτυχία", "Το αυτοκίνητο προστέθηκε.")

    except ValueError as e:
        messagebox.showerror("Σφάλμα {0}", format.str(e))

def update_kilometers():
    global df
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Καμία Επιλογή", "Επίλεξε ένα αυτοκίνητο για ενημέρωση.")
        return

    index = int(selected_item[0])

    try:
        added_km = int(km_entry.get())
        if added_km < 0:
            raise ValueError("Τα χιλιόμετρα πρέπει να είναι θετικός αριθμός.")

        old_km = int(df.loc[index, "Χιλιόμετρα"])
        new_km = old_km + added_km
        target_km = int(df.loc[index, "5κ χλμ"])

        # ✅ Υπολογισμός/ενημέρωση συνολικών χιλιομέτρων
        try:
            total_km = int(df.loc[index, "Συνολικά Χιλιόμετρα"])
        except:
            total_km = 0  # Αν δεν υπάρχει τιμή

        new_total_km = total_km + added_km
        df.loc[index, "Συνολικά Χιλιόμετρα"] = new_total_km

        # Συντήρηση λαδιών
        if new_km >= target_km:
            if messagebox.askyesno("🔧 Συντήρηση", f"{df.loc[index, 'Αυτοκίνητα']} έφτασε τα {new_km}χλμ. Έγινε αλλαγή λαδιών;"):
                df.loc[index, "5κ χλμ"] = new_km + 5000

        # Ενημέρωση πεδίου χιλιομέτρων
        df.loc[index, "Χιλιόμετρα"] = new_km

        update_treeview()
        messagebox.showinfo("✅ Ενημερώθηκε", f"Τα χιλιόμετρα ενημερώθηκαν σε {new_km}.\nΣύνολο χιλιομέτρων: {new_total_km}")

    except ValueError as e:
        messagebox.showerror("Σφάλμα", f"Μη έγκυρη είσοδος: {e}")



def update_car():
    """Update selected car information."""
    global df
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("No Selection", "Please select a car to update.")
        return

    index = int(selected_item[0])

    try:
        # Πάρε τιμές από τα πεδία εισόδου
        car_name = car_entry.get()
        number = int(number_entry.get()) if number_entry.get().isdigit() else None
        kilometers = int(km_entry.get()) if km_entry.get().isdigit() else None
        date = date_entry.get()
        aeko_date = aeko_entry.get()

        if car_name == "" or number is None or kilometers is None or date == "":
            raise ValueError("Συμπλήρωσε όλα τα υποχρεωτικά πεδία.")

        # Έλεγχος και υπολογισμός 3μηνης συντήρησης
        try:
            valid_date = datetime.strptime(date, "%d-%m-%Y")
            three_months_later = (valid_date + timedelta(days=90)).strftime("%d-%m-%Y")
        except ValueError:
            raise ValueError("Λάθος μορφή Ημερομηνίας. Χρησιμοποίησε DD-MM-YYYY.")

        # Έλεγχος και υπολογισμός 2ετίας από ΑΕΚΟ (αν υπάρχει)
        if aeko_date:
            try:
                valid_aeko = datetime.strptime(aeko_date, "%d-%m-%Y")
                two_years_later = (valid_aeko + timedelta(days=730)).strftime("%d-%m-%Y")
            except ValueError:
                raise ValueError("Λάθος μορφή Ημερομηνίας ΑΕΚΟ. Χρησιμοποίησε DD-MM-YYYY.")
        else:
            two_years_later = ""

        # Ενημέρωση DataFrame
        df.loc[index, "Αυτοκίνητα"] = car_name
        df.loc[index, "Αριθμός αυ/του"] = number
        df.loc[index, "Χιλιόμετρα"] = kilometers
        df.loc[index, "Ημερομηνία(ΤΠΣ)"] = date
        df.loc[index, "3μηναια"] = three_months_later
        df.loc[index, "5κ χλμ"] = kilometers + 5000
        df.loc[index, "Ημερομηνία ΑΕΚΟ"] = aeko_date
        df.loc[index, "2χρονια λαδια"] = two_years_later
        df.loc[index, "2χρονια βαλβ"] = two_years_later

        update_treeview()
        messagebox.showinfo("Επιτυχία", "Τα στοιχεία ενημερώθηκαν.")

    except ValueError as e:
        messagebox.showerror("Σφάλμα", str(e))

        
def save_to_csv():
    """Save the updated DataFrame to a CSV file with normalized dates."""
    global df
    try:
        # Normalize dates before saving
        date_columns = ["Ημερομηνία(ΤΠΣ)", "Ημερομηνία ΑΕΚΟ", "3μηναια", "2χρονια λαδια", "2χρονια βαλβ"]

        df = normalize_date_format(df, date_columns)
        df.to_csv(csv_file, index=False, encoding="utf-8-sig")
        messagebox.showinfo("Success", f"Data saved successfully to {csv_file}.")
    except PermissionError:
        backup_file = "Cars_updated2.csv"
        df.to_csv(backup_file, index=False, encoding="utf-8-sig")
        messagebox.showwarning(
            "Permission Denied",
            f"Permission denied for {csv_file}. Data saved to {backup_file}.",
        )
    except Exception as e:
        messagebox.showerror("Error", f"Error saving to CSV: {e}")

def check_warnings():
    """Check for any cars requiring maintenance and display warnings."""
    global df
    warnings = []
    today = datetime.today()

    for index, row in df.iterrows():
        car_name = row["Αυτοκίνητα"]
        car_id=row["Αριθμός αυ/του"]
        # Έλεγχος 3μηνης συντήρησης
        if not pd.isna(row["3μηναια"]):
            three_months_date = datetime.strptime(row["3μηναια"], "%d-%m-%Y")
            if today >= three_months_date:
                warnings.append(f"{car_name,car_id} χρειάζεται 3μηνη συντήρηση (Ημερομηνία: {three_months_date.strftime('%d-%m-%Y')}).")

        # Έλεγχος αλλαγής λαδιών στα 5.000 χλμ
        if not pd.isna(row["Χιλιόμετρα"]) and not pd.isna(row["5κ χλμ"]):
            mileage = int(row["Χιλιόμετρα"])
            next_mileage = int(row["5κ χλμ"])
            if mileage >= next_mileage:
                warnings.append(f"{car_name,car_id} έχει φτάσει τα {mileage}χλμ και χρειάζεται αλλαγή λαδιών (Όριο: {next_mileage}χλμ).")

        # Έλεγχος 2ετούς αλλαγής λαδιών και βαλβίδων
        if not pd.isna(row["2χρονια λαδια"]):
            two_years_date = datetime.strptime(row["2χρονια λαδια"], "%d-%m-%Y")
            if today >= two_years_date:
                warnings.append(f"{car_name,car_id} χρειάζεται αλλαγή λαδιών & βαλβίδων (Ημερομηνία: {two_years_date.strftime('%d-%m-%Y')}).")

    # Εμφάνιση προειδοποιήσεων
    if warnings:
        messagebox.showwarning("🔧 Συντήρηση Απαιτείται", "\n".join(warnings))
    else:
        messagebox.showinfo("✅ Όλα καλά!", "Όλα τα αυτοκίνητα είναι εντός προδιαγραφών!")


def setup_form():
    """Create input fields and buttons for adding and updating cars with scrollable frame."""
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

    # Add buttons below
    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)

    tk.Button(button_frame, text="Προσθήκη Οχήματος", command=add_car).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Ενημέρωση Οχήματος", command=update_car).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Ενημέρωση Χιλιομέτρων", command=update_kilometers).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Check Warnings", command=check_warnings).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="📊 Μεταφορά Χλμ τον Μήνα", command=transfer_monthly_km).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Αποθήκευση στο EXCEL", command=save_to_csv).pack(side=tk.LEFT, padx=5)

# Load data from the CSV file
df = load_data()

# Set up the Tkinter window
root = tk.Tk()
root.title("Car Maintenance Tracker")
root.geometry("1200x600")

# Create a frame to hold the Treeview
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# Create Treeview widget
tree = ttk.Treeview(frame)
tree.pack(fill=tk.BOTH, expand=True)
tree.bind("<<TreeviewSelect>>", select_car)

# Add scrollbars
scrollbar_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
scrollbar_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

# Define columns
tree["columns"] = list(df.columns)
tree["show"] = "headings"

# Add column headings
for col in df.columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER, width=150)

# Populate initial data
update_treeview()

def transfer_monthly_km():
    """Μεταφέρει τα συνολικά χλμ στη στήλη 'Χλμ τον Μηνα' και μηδενίζει τα 'Συνολικά Χιλιόμετρα'."""
    global df

    if "Συνολικά Χιλιόμετρα" not in df.columns:
        messagebox.showerror("Σφάλμα", "Η στήλη 'Συνολικά Χιλιόμετρα' δεν υπάρχει.")
        return

    if "Χλμ τον Μηνα" not in df.columns:
        df["Χλμ τον Μηνα"] = 0  # Αν δεν υπάρχει, δημιουργείται

    # Μεταφορά τιμών και μηδενισμός
    df["Χλμ τον Μηνα"] = df["Συνολικά Χιλιόμετρα"]
    df["Συνολικά Χιλιόμετρα"] = 0

    update_treeview()
    messagebox.showinfo("Επιτυχία", "Τα χλμ του μήνα ενημερώθηκαν και τα συνολικά μηδενίστηκαν.")


# Add input form and buttons
setup_form()
def apply_font_size():
    """Apply the current font size to all widgets, including Treeview."""
    f = font.Font(size=current_font_size)

    style = ttk.Style()
    style.configure("Treeview", font=(None, current_font_size))
    style.configure("Treeview.Heading", font=(None, current_font_size, 'bold'))

    for widget in root.winfo_children():
        apply_font_to_widget(widget, f)

def apply_font_to_widget(widget, font_obj):
    """Recursively apply font to widget and its children."""
    try:
        widget.configure(font=font_obj)
    except:
        pass  # Ignore widgets that don't support font

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

# Κουμπιά Zoom
zoom_frame = tk.Frame(root)
zoom_frame.pack(pady=5)

tk.Button(zoom_frame, text="🔍 Zoom In", command=zoom_in).pack(side=tk.LEFT, padx=5)
tk.Button(zoom_frame, text="🔎 Zoom Out", command=zoom_out).pack(side=tk.LEFT, padx=5)
# Run the Tkinter event loop
root.mainloop()
