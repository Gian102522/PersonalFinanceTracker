import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
import shutil
from datetime import datetime

# ─── Paths ───────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
DELIMITER = "|"

USERS_FILE = os.path.join(DATA_DIR, "users.csv")
INCOME_FILE = os.path.join(DATA_DIR, "income.csv")
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.csv")
LOGS_FILE = os.path.join(DATA_DIR, "logs.csv")

for d in [DATA_DIR, BACKUP_DIR]:
    os.makedirs(d, exist_ok=True)

# ─── CSV Helpers ─────────────────────────────────────────
def read_csv(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=DELIMITER)
        return list(reader)

def write_csv(filepath, rows, fieldnames):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=DELIMITER)
        writer.writeheader()
        writer.writerows(rows)

def append_csv(filepath, row, fieldnames):
    file_exists = os.path.exists(filepath) and os.path.getsize(filepath) > 0
    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=DELIMITER)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def next_id(filepath, id_field):
    rows = read_csv(filepath)
    if not rows:
        return 1
    return max(int(r[id_field]) for r in rows) + 1

def log_action(user_id, action):
    log_id = next_id(LOGS_FILE, "log_id")
    append_csv(LOGS_FILE, {
        "log_id": log_id,
        "user_id": user_id,
        "action": action,
        "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, ["log_id", "user_id", "action", "date_time"])

# ─── Color Palette ───────────────────────────────────────
BG = "#1a1a2e"
BG_SECONDARY = "#16213e"
CARD_BG = "#0f3460"
ACCENT = "#e94560"
ACCENT_HOVER = "#ff6b6b"
TEXT = "#eaeaea"
TEXT_MUTED = "#a0a0b0"
ENTRY_BG = "#233554"
SUCCESS = "#00b894"
WARNING = "#fdcb6e"

# ─── App ─────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance Tracking Management System")
        self.geometry("1000x650")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.current_user = None
        self.current_role = None
        self.show_login()

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    # ── Styled widgets ───────────────────────────────────
    def styled_label(self, parent, text, size=11, bold=False, color=TEXT):
        weight = "bold" if bold else "normal"
        lbl = tk.Label(parent, text=text, bg=parent["bg"], fg=color,
                       font=("Segoe UI", size, weight))
        return lbl

    def styled_entry(self, parent, show=None, width=30):
        e = tk.Entry(parent, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                     font=("Segoe UI", 11), relief="flat", bd=0,
                     highlightthickness=2, highlightcolor=ACCENT,
                     highlightbackground=BG_SECONDARY, width=width)
        if show:
            e.config(show=show)
        return e

    def styled_button(self, parent, text, command, bg_color=ACCENT, width=18):
        btn = tk.Button(parent, text=text, command=command, bg=bg_color,
                        fg="white", font=("Segoe UI", 11, "bold"),
                        relief="flat", cursor="hand2", width=width,
                        activebackground=ACCENT_HOVER, activeforeground="white",
                        bd=0, pady=8)
        btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg_color))
        return btn

    # ── LOGIN SCREEN ─────────────────────────────────────
    def show_login(self):
        self.clear()
        self.current_user = None

        frame = tk.Frame(self, bg=BG)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        self.styled_label(frame, "💰 PFTMS", size=28, bold=True, color=ACCENT).pack(pady=(0, 5))
        self.styled_label(frame, "Personal Finance Tracking\nManagement System",
                          size=11, color=TEXT_MUTED).pack(pady=(0, 30))

        card = tk.Frame(frame, bg=CARD_BG, padx=40, pady=30)
        card.pack()

        self.styled_label(card, "Sign In", size=16, bold=True).pack(pady=(0, 20))

        self.styled_label(card, "Username", size=10, color=TEXT_MUTED).pack(anchor="w")
        self.login_user = self.styled_entry(card)
        self.login_user.pack(pady=(2, 12), ipady=6)

        self.styled_label(card, "Password", size=10, color=TEXT_MUTED).pack(anchor="w")
        self.login_pass = self.styled_entry(card, show="•")
        self.login_pass.pack(pady=(2, 20), ipady=6)

        self.styled_button(card, "Login", self.do_login, width=25).pack(pady=(0, 10))
        self.styled_button(card, "Register", self.show_register, bg_color=BG_SECONDARY, width=25).pack()

        self.login_user.focus()
        self.bind("<Return>", lambda e: self.do_login())

    def do_login(self):
        username = self.login_user.get().strip()
        password = self.login_pass.get().strip()
        if not username or not password:
            messagebox.showwarning("Warning", "Please fill in all fields.")
            return
        users = read_csv(USERS_FILE)
        for u in users:
            if u["username"] == username and u["password"] == password:
                self.current_user = u["user_id"]
                self.current_role = u["role"]
                log_action(self.current_user, "LOGIN")
                self.show_dashboard()
                return
        messagebox.showerror("Error", "Invalid credentials.")

    # ── REGISTER SCREEN ──────────────────────────────────
    def show_register(self):
        self.clear()
        frame = tk.Frame(self, bg=BG)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(frame, bg=CARD_BG, padx=40, pady=30)
        card.pack()

        self.styled_label(card, "Create Account", size=16, bold=True).pack(pady=(0, 20))

        self.styled_label(card, "Username", size=10, color=TEXT_MUTED).pack(anchor="w")
        self.reg_user = self.styled_entry(card)
        self.reg_user.pack(pady=(2, 12), ipady=6)

        self.styled_label(card, "Password", size=10, color=TEXT_MUTED).pack(anchor="w")
        self.reg_pass = self.styled_entry(card, show="•")
        self.reg_pass.pack(pady=(2, 12), ipady=6)

        self.styled_label(card, "Confirm Password", size=10, color=TEXT_MUTED).pack(anchor="w")
        self.reg_pass2 = self.styled_entry(card, show="•")
        self.reg_pass2.pack(pady=(2, 20), ipady=6)

        self.styled_button(card, "Register", self.do_register, width=25).pack(pady=(0, 10))
        self.styled_button(card, "← Back to Login", self.show_login, bg_color=BG_SECONDARY, width=25).pack()

    def do_register(self):
        username = self.reg_user.get().strip()
        password = self.reg_pass.get().strip()
        password2 = self.reg_pass2.get().strip()
        if not username or not password:
            messagebox.showwarning("Warning", "Please fill in all fields.")
            return
        if password != password2:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        users = read_csv(USERS_FILE)
        if any(u["username"] == username for u in users):
            messagebox.showerror("Error", "Username already exists.")
            return
        uid = next_id(USERS_FILE, "user_id")
        append_csv(USERS_FILE, {
            "user_id": uid, "username": username, "password": password, "role": "user"
        }, ["user_id", "username", "password", "role"])
        log_action(uid, "REGISTER")
        messagebox.showinfo("Success", "Account created! You can now login.")
        self.show_login()

    # ── DASHBOARD ─────────────────────────────────────────
    def show_dashboard(self):
        self.clear()
        self.unbind("<Return>")

        # Sidebar
        sidebar = tk.Frame(self, bg=BG_SECONDARY, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.styled_label(sidebar, "💰 PFTMS", size=16, bold=True, color=ACCENT).pack(pady=(25, 5))

        users = read_csv(USERS_FILE)
        uname = next((u["username"] for u in users if u["user_id"] == self.current_user), "User")
        self.styled_label(sidebar, f"👤 {uname}", size=10, color=TEXT_MUTED).pack(pady=(0, 5))
        self.styled_label(sidebar, f"Role: {self.current_role}", size=9, color=TEXT_MUTED).pack(pady=(0, 25))

        nav_items = [
            ("📊  Dashboard", self.page_dashboard),
            ("➕  Add Income", self.page_add_income),
            ("➖  Add Expense", self.page_add_expense),
            ("📋  View Records", self.page_view_records),
            ("💾  Backup Data", self.page_backup),
        ]
        if self.current_role == "admin":
            nav_items.append(("👥  Manage Users", self.page_manage_users))
            nav_items.append(("📜  View Logs", self.page_view_logs))

        for text, cmd in nav_items:
            btn = tk.Button(sidebar, text=text, command=cmd, bg=BG_SECONDARY,
                            fg=TEXT, font=("Segoe UI", 11), relief="flat",
                            anchor="w", padx=20, pady=10, cursor="hand2",
                            activebackground=CARD_BG, activeforeground=TEXT, bd=0)
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=CARD_BG))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BG_SECONDARY))

        # Logout at bottom
        tk.Frame(sidebar, bg=BG_SECONDARY).pack(fill="both", expand=True)
        logout_btn = tk.Button(sidebar, text="🚪  Logout", command=self.show_login,
                               bg=ACCENT, fg="white", font=("Segoe UI", 11, "bold"),
                               relief="flat", cursor="hand2", pady=10, bd=0)
        logout_btn.pack(fill="x", padx=15, pady=15)

        # Content area
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="right", fill="both", expand=True)

        self.page_dashboard()

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ── PAGE: Dashboard ──────────────────────────────────
    def page_dashboard(self):
        self.clear_content()
        uid = self.current_user

        incomes = [r for r in read_csv(INCOME_FILE) if r["user_id"] == uid]
        expenses = [r for r in read_csv(EXPENSES_FILE) if r["user_id"] == uid]

        total_income = sum(float(r["amount"]) for r in incomes)
        total_expense = sum(float(r["amount"]) for r in expenses)
        balance = total_income - total_expense

        self.styled_label(self.content, "Dashboard", size=20, bold=True).pack(anchor="w", padx=30, pady=(25, 20))

        cards_frame = tk.Frame(self.content, bg=BG)
        cards_frame.pack(padx=30, anchor="w")

        card_data = [
            ("Total Income", f"₱{total_income:,.2f}", SUCCESS),
            ("Total Expenses", f"₱{total_expense:,.2f}", ACCENT),
            ("Balance", f"₱{balance:,.2f}", WARNING if balance >= 0 else ACCENT),
        ]

        for i, (title, value, color) in enumerate(card_data):
            card = tk.Frame(cards_frame, bg=CARD_BG, padx=25, pady=20)
            card.grid(row=0, column=i, padx=(0, 15), sticky="nsew")
            self.styled_label(card, title, size=10, color=TEXT_MUTED).pack(anchor="w")
            self.styled_label(card, value, size=22, bold=True, color=color).pack(anchor="w", pady=(5, 0))

        # Recent transactions
        self.styled_label(self.content, "Recent Transactions", size=14, bold=True).pack(anchor="w", padx=30, pady=(30, 10))

        tree_frame = tk.Frame(self.content, bg=BG)
        tree_frame.pack(padx=30, fill="both", expand=True, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=CARD_BG, foreground=TEXT,
                        fieldbackground=CARD_BG, font=("Segoe UI", 10), rowheight=28)
        style.configure("Treeview.Heading", background=BG_SECONDARY, foreground=TEXT,
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", ACCENT)])

        cols = ("Type", "Amount", "Category", "Date", "Description")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=10)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120)

        all_records = []
        for r in incomes:
            all_records.append(("Income", r["amount"], r["category"], r["date"], r["description"]))
        for r in expenses:
            all_records.append(("Expense", r["amount"], r["category"], r["date"], r["description"]))

        all_records.sort(key=lambda x: x[3], reverse=True)
        for rec in all_records[:20]:
            tree.insert("", "end", values=rec)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ── PAGE: Add Income ─────────────────────────────────
    def page_add_income(self):
        self.clear_content()
        self.styled_label(self.content, "Add Income", size=20, bold=True).pack(anchor="w", padx=30, pady=(25, 20))

        card = tk.Frame(self.content, bg=CARD_BG, padx=30, pady=25)
        card.pack(padx=30, anchor="w")

        categories = ["Salary", "Business", "Freelance", "Investment", "Gift", "Other"]

        self.styled_label(card, "Amount (₱)", size=10, color=TEXT_MUTED).pack(anchor="w")
        amount_entry = self.styled_entry(card)
        amount_entry.pack(pady=(2, 12), ipady=6)

        self.styled_label(card, "Category", size=10, color=TEXT_MUTED).pack(anchor="w")
        cat_var = tk.StringVar(value=categories[0])
        cat_menu = ttk.Combobox(card, textvariable=cat_var, values=categories,
                                font=("Segoe UI", 11), state="readonly", width=28)
        cat_menu.pack(pady=(2, 12), ipady=4)

        self.styled_label(card, "Date (YYYY-MM-DD)", size=10, color=TEXT_MUTED).pack(anchor="w")
        date_entry = self.styled_entry(card)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(pady=(2, 12), ipady=6)

        self.styled_label(card, "Description", size=10, color=TEXT_MUTED).pack(anchor="w")
        desc_entry = self.styled_entry(card)
        desc_entry.pack(pady=(2, 20), ipady=6)

        def save():
            try:
                amt = float(amount_entry.get())
                if amt <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Enter a valid positive amount.")
                return
            iid = next_id(INCOME_FILE, "income_id")
            append_csv(INCOME_FILE, {
                "income_id": iid, "user_id": self.current_user,
                "amount": f"{amt:.2f}", "category": cat_var.get(),
                "date": date_entry.get(), "description": desc_entry.get()
            }, ["income_id", "user_id", "amount", "category", "date", "description"])
            log_action(self.current_user, f"ADD_INCOME ₱{amt:.2f}")
            messagebox.showinfo("Success", "Income recorded!")
            amount_entry.delete(0, "end")
            desc_entry.delete(0, "end")

        self.styled_button(card, "Save Income", save, bg_color=SUCCESS, width=25).pack()

    # ── PAGE: Add Expense ────────────────────────────────
    def page_add_expense(self):
        self.clear_content()
        self.styled_label(self.content, "Add Expense", size=20, bold=True).pack(anchor="w", padx=30, pady=(25, 20))

        card = tk.Frame(self.content, bg=CARD_BG, padx=30, pady=25)
        card.pack(padx=30, anchor="w")

        categories = ["Food", "Transportation", "Utilities", "Rent", "Education",
                       "Health", "Entertainment", "Shopping", "Other"]

        self.styled_label(card, "Amount (₱)", size=10, color=TEXT_MUTED).pack(anchor="w")
        amount_entry = self.styled_entry(card)
        amount_entry.pack(pady=(2, 12), ipady=6)

        self.styled_label(card, "Category", size=10, color=TEXT_MUTED).pack(anchor="w")
        cat_var = tk.StringVar(value=categories[0])
        cat_menu = ttk.Combobox(card, textvariable=cat_var, values=categories,
                                font=("Segoe UI", 11), state="readonly", width=28)
        cat_menu.pack(pady=(2, 12), ipady=4)

        self.styled_label(card, "Date (YYYY-MM-DD)", size=10, color=TEXT_MUTED).pack(anchor="w")
        date_entry = self.styled_entry(card)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(pady=(2, 12), ipady=6)

        self.styled_label(card, "Description", size=10, color=TEXT_MUTED).pack(anchor="w")
        desc_entry = self.styled_entry(card)
        desc_entry.pack(pady=(2, 20), ipady=6)

        def save():
            try:
                amt = float(amount_entry.get())
                if amt <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Enter a valid positive amount.")
                return
            eid = next_id(EXPENSES_FILE, "expense_id")
            append_csv(EXPENSES_FILE, {
                "expense_id": eid, "user_id": self.current_user,
                "amount": f"{amt:.2f}", "category": cat_var.get(),
                "date": date_entry.get(), "description": desc_entry.get()
            }, ["expense_id", "user_id", "amount", "category", "date", "description"])
            log_action(self.current_user, f"ADD_EXPENSE ₱{amt:.2f}")
            messagebox.showinfo("Success", "Expense recorded!")
            amount_entry.delete(0, "end")
            desc_entry.delete(0, "end")

        self.styled_button(card, "Save Expense", save, bg_color=ACCENT, width=25).pack()

    # ── PAGE: View Records ───────────────────────────────
    def page_view_records(self):
        self.clear_content()
        uid = self.current_user

        self.styled_label(self.content, "All Records", size=20, bold=True).pack(anchor="w", padx=30, pady=(25, 10))

        # Filter frame
        filter_frame = tk.Frame(self.content, bg=BG)
        filter_frame.pack(padx=30, anchor="w", pady=(0, 10))

        self.styled_label(filter_frame, "Filter:", size=10, color=TEXT_MUTED).pack(side="left", padx=(0, 8))
        filter_var = tk.StringVar(value="All")
        for val in ["All", "Income", "Expense"]:
            rb = tk.Radiobutton(filter_frame, text=val, variable=filter_var, value=val,
                                bg=BG, fg=TEXT, selectcolor=CARD_BG, font=("Segoe UI", 10),
                                activebackground=BG, activeforeground=TEXT)
            rb.pack(side="left", padx=5)

        tree_frame = tk.Frame(self.content, bg=BG)
        tree_frame.pack(padx=30, fill="both", expand=True, pady=(0, 20))

        cols = ("ID", "Type", "Amount", "Category", "Date", "Description")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)
        for c in cols:
            tree.heading(c, text=c)
        tree.column("ID", width=50)
        tree.column("Type", width=80)
        tree.column("Amount", width=100)
        tree.column("Category", width=120)
        tree.column("Date", width=100)
        tree.column("Description", width=200)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def refresh():
            tree.delete(*tree.get_children())
            ftype = filter_var.get()
            records = []
            if ftype in ("All", "Income"):
                for r in read_csv(INCOME_FILE):
                    if r["user_id"] == uid:
                        records.append((r["income_id"], "Income", f"₱{float(r['amount']):,.2f}",
                                        r["category"], r["date"], r["description"]))
            if ftype in ("All", "Expense"):
                for r in read_csv(EXPENSES_FILE):
                    if r["user_id"] == uid:
                        records.append((r["expense_id"], "Expense", f"₱{float(r['amount']):,.2f}",
                                        r["category"], r["date"], r["description"]))
            records.sort(key=lambda x: x[4], reverse=True)
            for rec in records:
                tree.insert("", "end", values=rec)

        filter_var.trace_add("write", lambda *_: refresh())
        refresh()

    # ── PAGE: Backup ─────────────────────────────────────
    def page_backup(self):
        self.clear_content()
        self.styled_label(self.content, "Backup Data", size=20, bold=True).pack(anchor="w", padx=30, pady=(25, 20))

        card = tk.Frame(self.content, bg=CARD_BG, padx=30, pady=25)
        card.pack(padx=30, anchor="w")

        self.styled_label(card, "Create a backup of all your financial data.\n"
                          "Backups are saved with a timestamp in the backups/ folder.",
                          size=11, color=TEXT_MUTED).pack(pady=(0, 20))

        def do_backup():
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            files = ["users.csv", "income.csv", "expenses.csv", "logs.csv"]
            count = 0
            for fname in files:
                src = os.path.join(DATA_DIR, fname)
                if os.path.exists(src):
                    name, ext = os.path.splitext(fname)
                    dst = os.path.join(BACKUP_DIR, f"{name}_backup_{timestamp}{ext}")
                    shutil.copy2(src, dst)
                    count += 1
            log_action(self.current_user, "BACKUP_CREATED")
            messagebox.showinfo("Backup Complete", f"{count} files backed up to:\nbackups/\n\nTimestamp: {timestamp}")

        self.styled_button(card, "Create Backup Now", do_backup, bg_color=SUCCESS, width=25).pack(pady=(0, 10))

        def export_usb():
            folder = filedialog.askdirectory(title="Select USB or Folder for Export")
            if not folder:
                return
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            files = ["users.csv", "income.csv", "expenses.csv", "logs.csv"]
            for fname in files:
                src = os.path.join(DATA_DIR, fname)
                if os.path.exists(src):
                    name, ext = os.path.splitext(fname)
                    dst = os.path.join(folder, f"{name}_backup_{timestamp}{ext}")
                    shutil.copy2(src, dst)
            log_action(self.current_user, f"EXPORT_TO_{folder}")
            messagebox.showinfo("Export Complete", f"Data exported to:\n{folder}")

        self.styled_button(card, "Export to USB / Folder", export_usb, bg_color=CARD_BG, width=25).pack()

    # ── PAGE: Manage Users (Admin) ───────────────────────
    def page_manage_users(self):
        self.clear_content()
        self.styled_label(self.content, "Manage Users", size=20, bold=True).pack(anchor="w", padx=30, pady=(25, 10))

        tree_frame = tk.Frame(self.content, bg=BG)
        tree_frame.pack(padx=30, fill="both", expand=True, pady=(0, 20))

        cols = ("ID", "Username", "Role")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)
        for c in cols:
            tree.heading(c, text=c)
        tree.column("ID", width=60)
        tree.column("Username", width=200)
        tree.column("Role", width=100)
        tree.pack(side="left", fill="both", expand=True)

        users = read_csv(USERS_FILE)
        for u in users:
            tree.insert("", "end", values=(u["user_id"], u["username"], u["role"]))

        btn_frame = tk.Frame(self.content, bg=BG)
        btn_frame.pack(padx=30, anchor="w", pady=(0, 20))

        def delete_user():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Warning", "Select a user first.")
                return
            vals = tree.item(sel[0])["values"]
            if str(vals[0]) == self.current_user:
                messagebox.showerror("Error", "Cannot delete yourself.")
                return
            if messagebox.askyesno("Confirm", f"Delete user '{vals[1]}'?"):
                users_data = read_csv(USERS_FILE)
                users_data = [u for u in users_data if u["user_id"] != str(vals[0])]
                write_csv(USERS_FILE, users_data, ["user_id", "username", "password", "role"])
                log_action(self.current_user, f"DELETE_USER {vals[1]}")
                self.page_manage_users()

        self.styled_button(btn_frame, "Delete Selected User", delete_user, bg_color=ACCENT).pack(side="left")

    # ── PAGE: View Logs (Admin) ──────────────────────────
    def page_view_logs(self):
        self.clear_content()
        self.styled_label(self.content, "Activity Logs", size=20, bold=True).pack(anchor="w", padx=30, pady=(25, 10))

        tree_frame = tk.Frame(self.content, bg=BG)
        tree_frame.pack(padx=30, fill="both", expand=True, pady=(0, 20))

        cols = ("Log ID", "User ID", "Action", "Date/Time")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=18)
        for c in cols:
            tree.heading(c, text=c)
        tree.column("Log ID", width=60)
        tree.column("User ID", width=80)
        tree.column("Action", width=250)
        tree.column("Date/Time", width=180)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        logs = read_csv(LOGS_FILE)
        logs.reverse()
        for l in logs:
            tree.insert("", "end", values=(l["log_id"], l["user_id"], l["action"], l["date_time"]))


if __name__ == "__main__":
    app = App()
    app.mainloop()
