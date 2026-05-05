import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
# ---------------- DATABASE CONNECTION ----------------
conn = sqlite3.connect("sleep.db")
cursor = conn.cursor()
# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS sleep (
    date TEXT,
    hours REAL,
    note TEXT
)
""")
conn.commit()
# ---------------- FUNCTIONS ----------------
def add_data():
    date = date_box.get()
    hours = hours_box.get()
    note = note_box.get()
    if date and hours and note:
        try:
            hours = float(hours)
            # Insert into database
            cursor.execute("INSERT INTO sleep VALUES (?, ?, ?)", (date, hours, note))
            conn.commit()
            messagebox.showinfo("Success", "Sleep data added")
            clear_fields()
            show_data()
        except ValueError:
            messagebox.showerror("Error", "Sleep hours must be a number")
    else:
        messagebox.showwarning("Warning", "Please fill all fields")
def clear_fields():
    date_box.delete(0, tk.END)
    hours_box.delete(0, tk.END)
    note_box.delete(0, tk.END)
def show_data():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM sleep")
    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", tk.END, values=row)
def delete_data():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Select", "Please select a record")
        return
    values = tree.item(selected, "values")

    # Delete from database
    cursor.execute("DELETE FROM sleep WHERE date=? AND hours=? AND note=?",
                   (values[0], float(values[1]), values[2]))
    conn.commit()
    messagebox.showinfo("Deleted", "Record deleted")
    show_data()
def analyze_sleep():
    cursor.execute("SELECT hours FROM sleep")
    data = cursor.fetchall()
    if not data:
        messagebox.showinfo("No Data", "No sleep records available")
        return
    hours_list = [row[0] for row in data]
    avg = np.mean(hours_list)
    if avg >= 7:
        status = "Good Sleep 😊"
    elif avg >= 5:
        status = "Average Sleep 😐"
    else:
        status = "Poor Sleep 😴"
    messagebox.showinfo("Sleep Analysis",
                        f"Average Sleep: {avg:.2f} hours\nStatus: {status}")
def show_graph():
    cursor.execute("SELECT date, hours FROM sleep")
    data = cursor.fetchall()
    if not data:
        messagebox.showinfo("No Data", "No records to show")
        return

    dates = [row[0] for row in data]
    hours = [row[1] for row in data]

    plt.bar(dates, hours)
    plt.title("Sleep Pattern Analysis")
    plt.xlabel("Date")
    plt.ylabel("Sleep Hours")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
# ---------------- GUI ----------------
root = tk.Tk()
root.title("Sleep Analyzer System (SQLite)")
root.geometry("700x500")
# Inputs
tk.Label(root, text="Date (DD-MM-YYYY)").pack()
date_box = tk.Entry(root)
date_box.pack()
tk.Label(root, text="Sleep Hours").pack()
hours_box = tk.Entry(root)
hours_box.pack()

tk.Label(root, text="Note (Good/Bad)").pack()
note_box = tk.Entry(root)
note_box.pack()
# Buttons
tk.Button(root, text="Add Data", bg="green", fg="white", command=add_data).pack(pady=5)
tk.Button(root, text="Analyze Sleep", command=analyze_sleep).pack(pady=5)
tk.Button(root, text="Show Graph", command=show_graph).pack(pady=5)
tk.Button(root, text="Delete Selected", bg="red", fg="white", command=delete_data).pack(pady=5)
# Table
tree = ttk.Treeview(root, columns=("Date", "Hours", "Note"), show="headings")
for col in ("Date", "Hours", "Note"):
    tree.heading(col, text=col)
    tree.column(col, width=150)
tree.pack(fill=tk.BOTH, expand=True)
# Load data
show_data()
# Run GUI
root.mainloop()
# Close DB when app closes
conn.close()
