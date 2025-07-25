import sqlite3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import openpyxl
import os

# ------------------ DATABASE SETUP ------------------
def connect_db():
    conn = sqlite3.connect("car_info.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT,
            model TEXT,
            year INTEGER,
            price REAL
        )
    """)
    conn.commit()
    return conn

# ------------------ FUNCTIONS ------------------
def add_car():
    make = combo_make.get()
    model = combo_model.get()
    year = combo_year.get()
    price = entry_price.get().replace(",", "")
    if not (make and model and year and price):
        messagebox.showwarning("Missing Info", "Please fill all fields.")
        return
    try:
        cursor.execute("INSERT INTO cars (make, model, year, price) VALUES (?, ?, ?, ?)",
                       (make, model, int(year), float(price)))
        conn.commit()
        show_cars()
        clear_fields()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_cars():
    for i in tree.get_children():
        tree.delete(i)
    cursor.execute("SELECT * FROM cars")
    for row in cursor.fetchall():
        tree.insert("", END, values=(row[0], row[1], row[2], row[3], f"{int(row[4]):,}"))

def clear_fields():
    combo_make.set("")
    combo_model.set("")
    combo_year.set("")
    entry_price.delete(0, END)

def update_model_options(event):
    selected_make = combo_make.get()
    models = car_models.get(selected_make, [])
    combo_model.config(values=models)
    combo_model.set("")

def search_cars():
    keyword = entry_search.get()
    query = f"SELECT * FROM cars WHERE make LIKE ? OR model LIKE ? OR year LIKE ?"
    for i in tree.get_children():
        tree.delete(i)
    cursor.execute(query, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
    for row in cursor.fetchall():
        tree.insert("", END, values=(row[0], row[1], row[2], row[3], f"{int(row[4]):,}"))

def export_to_excel():
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
    if not file_path:
        return
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ID", "Make", "Model", "Year", "Price"])
    for child in tree.get_children():
        ws.append(tree.item(child)['values'])
    wb.save(file_path)
    messagebox.showinfo("Exported", "Data exported to Excel successfully.")

def toggle_theme():
    current = app.style.theme.name
    new_theme = "darkly" if current == "flatly" else "flatly"
    app.style.theme_use(new_theme)

def format_price_input(event):
    value = entry_price.get().replace(",", "")
    if value.isdigit():
        formatted = "{:,}".format(int(value))
        entry_price.delete(0, END)
        entry_price.insert(0, formatted)

# ------------------ CAR MODEL DATA ------------------
car_models = {
    "Toyota": ["Corolla", "Camry", "Innova", "Fortuner", "Etios"],
    "Honda": ["City", "Civic", "Amaze", "Jazz", "WR-V"],
    "Hyundai": ["i10", "i20", "Creta", "Verna", "Tucson"],
    "Tata": ["Nexon", "Harrier", "Punch", "Tiago", "Safari"],
    "Mahindra": ["XUV700", "Thar", "Scorpio", "Bolero", "XUV300"],
    "Maruti Suzuki": ["Swift", "Baleno", "WagonR", "Ertiga", "Dzire"],
    "Ford": ["Figo", "EcoSport", "Endeavour", "Freestyle"],
    "BMW": ["X1", "X3", "X5", "3 Series", "5 Series"],
    "Mercedes": ["A-Class", "C-Class", "E-Class", "GLA", "GLE"],
    "Kia": ["Seltos", "Sonet", "Carens"],
    "MG": ["Hector", "Astor", "Gloster"],
    "Volkswagen": ["Polo", "Vento", "Taigun"],
    "Skoda": ["Rapid", "Octavia", "Kushaq"],
    "Nissan": ["Magnite", "Kicks"],
    "Renault": ["Kwid", "Triber", "Duster"]
}

# ------------------ UI SETUP ------------------
app = ttk.Window(themename="flatly")
app.title("Car Information Manager")
app.geometry("1000x600")
app.resizable(False, False)

conn = connect_db()
cursor = conn.cursor()

# ------------------ Logo ------------------
try:
    logo_img = Image.open("logo_converted.png").resize((80, 80))
    logo = ImageTk.PhotoImage(logo_img)
    logo_label = ttk.Label(app, image=logo)
    logo_label.place(x=10, y=10)
except Exception as e:
    print("Logo not found or failed to load:", e)

# ------------------ Form Fields ------------------
ttk.Label(app, text="Brand:").place(x=120, y=20)
combo_make = ttk.Combobox(app, values=list(car_models.keys()), state="readonly")
combo_make.place(x=180, y=20)
combo_make.bind("<<ComboboxSelected>>", update_model_options)

ttk.Label(app, text="Model:").place(x=400, y=20)
combo_model = ttk.Combobox(app, state="readonly")
combo_model.place(x=470, y=20)

ttk.Label(app, text="Year:").place(x=120, y=60)
combo_year = ttk.Combobox(app, values=[str(y) for y in range(2000, 2026)], state="readonly")
combo_year.place(x=180, y=60)

ttk.Label(app, text="Price:").place(x=400, y=60)
entry_price = ttk.Entry(app)
entry_price.place(x=470, y=60)
entry_price.bind("<KeyRelease>", format_price_input)

# ------------------ Buttons ------------------
ttk.Button(app, text="Add Car", command=add_car, bootstyle="success").place(x=700, y=20)
ttk.Button(app, text="Export to Excel", command=export_to_excel, bootstyle="info").place(x=700, y=60)
ttk.Button(app, text="Toggle Theme", command=toggle_theme, bootstyle="secondary").place(x=850, y=60)

# ------------------ Search ------------------
ttk.Label(app, text="Search:").place(x=20, y=120)
entry_search = ttk.Entry(app, width=30)
entry_search.place(x=90, y=120)
ttk.Button(app, text="Search", command=search_cars, bootstyle="primary").place(x=320, y=115)

# ------------------ Table ------------------
tree = ttk.Treeview(app, columns=("ID", "Make", "Model", "Year", "Price"), show="headings")
for col in ("ID", "Make", "Model", "Year", "Price"):
    tree.heading(col, text=col)
    tree.column(col, anchor="center")
tree.place(x=20, y=170, width=960, height=400)

# ------------------ Init ------------------
show_cars()
app.mainloop()
