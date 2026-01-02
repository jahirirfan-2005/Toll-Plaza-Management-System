import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class TollPlazaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Toll Plaza Management System")
        self.root.geometry("950x600")
        self.root.configure(bg="#0f172a")
        self.root.resizable(False, False)

        # ---------- DATABASE ----------
        self.conn = sqlite3.connect("toll_plaza.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS toll_records (
                vehicle_number TEXT PRIMARY KEY,
                toll_paid REAL
            )
        """)

        # ---------- STYLES ----------
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Header.TLabel",
            font=("Segoe UI", 24, "bold"),
            background="#020617",
            foreground="#e5e7eb",
            padding=20)

        style.configure("Card.TFrame",
            background="#020617",
            relief="flat")

        style.configure("Field.TLabel",
            font=("Segoe UI", 12),
            background="#020617",
            foreground="#cbd5f5")

        style.configure("TEntry",
            font=("Segoe UI", 12),
            padding=10)

        style.configure("Accent.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=12,
            background="#2563eb",
            foreground="white")

        style.map("Accent.TButton",
            background=[("active", "#1d4ed8")])

        # ---------- HEADER ----------
        header = ttk.Label(
            self.root,
            text="🚧 Toll Plaza Management Dashboard",
            style="Header.TLabel",
            anchor="center"
        )
        header.pack(fill="x")

        # ---------- MAIN CARD ----------
        card = tk.Frame(
            self.root,
            bg="#020617",
            highlightbackground="#1e293b",
            highlightthickness=2
        )
        card.place(relx=0.5, rely=0.48, anchor="center", width=720, height=380)

        # ---------- FORM ----------
        ttk.Label(card, text="Vehicle Number", style="Field.TLabel")\
            .place(x=60, y=60)

        self.vehicle_entry = ttk.Entry(card, width=28)
        self.vehicle_entry.place(x=250, y=55)

        ttk.Label(card, text="Toll Amount (₹)", style="Field.TLabel")\
            .place(x=60, y=120)

        self.toll_entry = ttk.Entry(card, width=28)
        self.toll_entry.place(x=250, y=115)

        # ---------- BUTTONS ----------
        ttk.Button(card, text="➕ Add Entry", style="Accent.TButton",
                   command=self.add_entry)\
            .place(x=80, y=200, width=150)

        ttk.Button(card, text="📋 View Records", style="Accent.TButton",
                   command=self.view_entries)\
            .place(x=280, y=200, width=150)

        ttk.Button(card, text="📊 Summary", style="Accent.TButton",
                   command=self.show_summary)\
            .place(x=480, y=200, width=150)

        # ---------- TOTAL BOX ----------
        self.total_var = tk.StringVar(value="₹ 0.00")

        total_box = tk.Frame(
            self.root,
            bg="#020617",
            highlightbackground="#2563eb",
            highlightthickness=2
        )
        total_box.place(relx=0.5, rely=0.85, anchor="center", width=350, height=80)

        tk.Label(total_box, text="TOTAL COLLECTION",
                 bg="#020617", fg="#94a3b8",
                 font=("Segoe UI", 11, "bold")).pack(pady=5)

        tk.Label(total_box, textvariable=self.total_var,
                 bg="#020617", fg="#22c55e",
                 font=("Segoe UI", 20, "bold")).pack()

        self.update_total()

        # Enter key support
        self.root.bind("<Return>", lambda e: self.add_entry())

    # ---------- FUNCTIONS ----------
    def add_entry(self):
        vehicle = self.vehicle_entry.get().upper().strip()
        toll = self.toll_entry.get().strip()

        if not vehicle or not toll:
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            toll = float(toll)
            self.cursor.execute(
                "INSERT INTO toll_records VALUES (?, ?)",
                (vehicle, toll)
            )
            self.conn.commit()
            self.vehicle_entry.delete(0, tk.END)
            self.toll_entry.delete(0, tk.END)
            self.update_total()
            messagebox.showinfo("Success", "Entry Added")

        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Vehicle already exists")

    def view_entries(self):
        top = tk.Toplevel(self.root)
        top.title("Toll Records")
        top.geometry("650x400")
        top.configure(bg="#020617")

        tree = ttk.Treeview(top, columns=("Vehicle", "Toll"), show="headings")
        tree.heading("Vehicle", text="Vehicle Number")
        tree.heading("Toll", text="Toll Paid (₹)")
        tree.pack(fill="both", expand=True, padx=15, pady=15)

        self.cursor.execute("SELECT * FROM toll_records")
        for rec in self.cursor.fetchall():
            tree.insert("", "end", values=(rec[0], f"₹{rec[1]:.2f}"))

    def show_summary(self):
        self.cursor.execute("SELECT COUNT(*), SUM(toll_paid) FROM toll_records")
        count, total = self.cursor.fetchone()
        total = total or 0

        messagebox.showinfo(
            "Summary",
            f"Vehicles Passed: {count}\nTotal Collection: ₹{total:.2f}"
        )

    def update_total(self):
        self.cursor.execute("SELECT SUM(toll_paid) FROM toll_records")
        total = self.cursor.fetchone()[0] or 0
        self.total_var.set(f"₹ {total:.2f}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TollPlazaApp(root)
    root.mainloop()
