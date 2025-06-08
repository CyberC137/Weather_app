import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import requests
from datetime import datetime

API_KEY = "API-KEY"
DB_NAME = "weather_data.db"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


# ---------- DB Setup ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            date TEXT NOT NULL,
            temperature REAL NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# ---------- API ----------
def get_forecast_from_api(location, start, end):
    try:
        params = {"q": location, "appid": API_KEY, "units": "metric"}
        res = requests.get(FORECAST_URL, params=params)
        res.raise_for_status()
        data = res.json()
        forecasts = []
        for item in data["list"]:
            date_str = item["dt_txt"].split()[0]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            if start <= date_obj <= end:
                forecasts.append({
                    "date": date_str,
                    "temp": item["main"]["temp"],
                    "description": item["weather"][0]["description"]
                })
        return forecasts
    except Exception as e:
        messagebox.showerror("API Error", str(e))
        return []


# ---------- CRUD Logic ----------
def create_forecast():
    location = create_loc.get()
    start = create_start.get()
    end = create_end.get()

    try:
        start_d = datetime.strptime(start, "%Y-%m-%d").date()
        end_d = datetime.strptime(end, "%Y-%m-%d").date()
        if end_d < start_d:
            raise ValueError("End date must be after start date.")
    except ValueError as e:
        messagebox.showerror("Date Error", str(e))
        return

    forecasts = get_forecast_from_api(location, start_d, end_d)
    if forecasts:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        for f in forecasts:
            cursor.execute('INSERT INTO weather (location, date, temperature, description) VALUES (?, ?, ?, ?)',
                           (location, f["date"], f["temp"], f["description"]))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Stored {len(forecasts)} entries.")
    else:
        messagebox.showinfo("Info", "No forecast data found.")
    read_forecast()



def read_forecast(loc=None, start=None, end=None):
    output_read.delete(1.0, tk.END)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = "SELECT * FROM weather WHERE 1=1"
    params = []
    if loc:
        query += " AND location LIKE ?"
        params.append(f"%{loc}%")
    if start:
        query += " AND date >= ?"
        params.append(start)
    if end:
        query += " AND date <= ?"
        params.append(end)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if rows:
        for row in rows:
            output_read.insert(tk.END, f"{row[0]} | {row[1]} | {row[2]} | {row[3]}°C | {row[4].title()}\n")
    else:
        output_read.insert(tk.END, "No records found.")



def update_forecast():
    loc = update_loc.get()
    date = update_date.get()
    temp = update_temp.get()
    desc = update_desc.get()

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Date Error", "Invalid date.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM weather WHERE location LIKE ? AND date = ?", (f"%{loc}%", date))
    if not cursor.fetchall():
        messagebox.showinfo("Not Found", "No matching record.")
        conn.close()
        return

    query = "UPDATE weather SET "
    params = []
    if temp:
        query += "temperature = ?, "
        params.append(float(temp))
    if desc:
        query += "description = ?, "
        params.append(desc)
    query = query.rstrip(", ") + " WHERE location LIKE ? AND date = ?"
    params.append(f"%{loc}%")
    params.append(date)

    cursor.execute(query, params)
    conn.commit()
    conn.close()
    messagebox.showinfo("Updated", "Record updated.")
    read_forecast()


def delete_forecast():
    loc = delete_loc.get()
    date = delete_date.get()

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Date Error", "Invalid date.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM weather WHERE location LIKE ? AND date = ?", (f"%{loc}%", date))
    count = cursor.rowcount
    conn.commit()
    conn.close()

    messagebox.showinfo("Deleted", f"{count} record(s) deleted." if count else "No matching records.")
    read_forecast()

# ---------- GUI Setup ----------
init_db()
root = tk.Tk()
root.title("Weather App (Dropdown CRUD)")
root.geometry("700x700")

# Dropdown selector
def show_frame(*args):
    option = selected.get()
    for name, frame in frames.items():
        frame.pack_forget()
    frames[option].pack(pady=10)

selected = tk.StringVar()
selected.trace('w', show_frame)

ttk.Label(root, text="Select Operation:", font=("Arial", 14)).pack(pady=10)
crud_options = ["Create", "Read", "Update", "Delete"]
crud_menu = ttk.Combobox(root, textvariable=selected, values=crud_options, state="readonly")
crud_menu.set("Create")
crud_menu.pack()

frames = {}

# CREATE
frame_create = tk.Frame(root)
tk.Label(frame_create, text="Location:").pack()
create_loc = tk.Entry(frame_create); create_loc.pack()
tk.Label(frame_create, text="Start Date (YYYY-MM-DD):").pack()
create_start = tk.Entry(frame_create); create_start.pack()
tk.Label(frame_create, text="End Date (YYYY-MM-DD):").pack()
create_end = tk.Entry(frame_create); create_end.pack()
tk.Button(frame_create, text="Fetch & Save", command=create_forecast).pack(pady=5)
output_create = tk.Text(frame_create, height=10, width=70)
output_create.pack()
frames["Create"] = frame_create

# READ
frame_read = tk.Frame(root)
tk.Label(frame_read, text="Location (optional):").pack()
read_loc = tk.Entry(frame_read); read_loc.pack()
tk.Label(frame_read, text="Start Date (optional):").pack()
read_start = tk.Entry(frame_read); read_start.pack()
tk.Label(frame_read, text="End Date (optional):").pack()
read_end = tk.Entry(frame_read); read_end.pack()
tk.Button(frame_read, text="Read", command=lambda: read_forecast(read_loc.get(), read_start.get(), read_end.get())).pack(pady=5)
output_read = tk.Text(frame_read, height=10, width=70)
output_read.pack()
frames["Read"] = frame_read

# UPDATE
frame_update = tk.Frame(root)
tk.Label(frame_update, text="Location:").pack()
update_loc = tk.Entry(frame_update); update_loc.pack()
tk.Label(frame_update, text="Date (YYYY-MM-DD):").pack()
update_date = tk.Entry(frame_update); update_date.pack()
tk.Label(frame_update, text="New Temperature:").pack()
update_temp = tk.Entry(frame_update); update_temp.pack()
tk.Label(frame_update, text="New Description:").pack()
update_desc = tk.Entry(frame_update); update_desc.pack()
tk.Button(frame_update, text="Update", command=update_forecast).pack(pady=5)
frames["Update"] = frame_update

# DELETE
frame_delete = tk.Frame(root)
tk.Label(frame_delete, text="Location:").pack()
delete_loc = tk.Entry(frame_delete); delete_loc.pack()
tk.Label(frame_delete, text="Date (YYYY-MM-DD):").pack()
delete_date = tk.Entry(frame_delete); delete_date.pack()
tk.Button(frame_delete, text="Delete", command=delete_forecast).pack(pady=5)
output_delete = tk.Text(frame_delete, height=10, width=70)
output_delete.pack()
frames["Delete"] = frame_delete

# Start with "Create" frame visible
frames["Create"].pack()

root.mainloop()
