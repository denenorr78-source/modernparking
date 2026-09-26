import datetime as dt
import tkinter as tk
from tkinter import ttk, messagebox

from security import LoginLimiter, verify_password
from validation import (
    clean_text,
    normalize_registration,
    valid_name,
    valid_password,
    valid_phone,
    valid_registration,
    valid_username,
)


# Cinematic black + burnt-orange palette inspired by the supplied reference UI.
COLORS = {
    "bg": "#050505",
    "card": "#111111",
    "card2": "#18100E",
    "accent": "#9E2F12",
    "accent2": "#C43A16",
    "accent3": "#B33A17",
    "danger": "#A52A20",
    "success": "#A9481D",
    "text": "#F3E8E2",
    "subtext": "#9C8B83",
    "input_bg": "#211714",
    "border": "#3B2119",
    "white": "#FFFFFF",
}

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_HEAD = ("Segoe UI", 13, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BTN = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)


class ParkingApp:
    def __init__(self, db):
        self.db = db
        self.root = tk.Tk()
        self.root.title("Modern Parking Management System")
        self.root.geometry("1180x720")
        self.root.minsize(1000, 650)
        self.root.configure(bg=COLORS["bg"])

        self.current_user = None
        self.limiter = LoginLimiter()

    def run(self):
        self.show_login()
        self.root.mainloop()

    # ==================== GENERAL HELPERS ====================

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def add_footer(self, parent):
        footer = tk.Frame(parent, bg=COLORS["card"], height=30)
        footer.pack(side="bottom", fill="x")
        footer.pack_propagate(False)
        tk.Label(
            footer,
            text="@2026 Modern Parking system. Developed by Dennis Kipkoech",
            bg=COLORS["card"],
            fg=COLORS["subtext"],
            font=FONT_SMALL,
        ).pack(expand=True)

    def make_button(self, parent, text, command, color=None, width=None):
        color = color or COLORS["accent"]
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=COLORS["white"],
            activebackground=COLORS["accent2"],
            activeforeground=COLORS["white"],
            font=FONT_BTN,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=9,
            width=width,
        )

        button.bind(
            "<Enter>",
            lambda event: button.configure(bg=self.lighten(color)),
        )
        button.bind(
            "<Leave>",
            lambda event: button.configure(bg=color),
        )
        return button

    def lighten(self, hex_color):
        hex_color = hex_color.lstrip("#")
        r, g, b = (
            int(hex_color[i:i + 2], 16)
            for i in (0, 2, 4)
        )
        r, g, b = (
            min(255, x + 25)
            for x in (r, g, b)
        )
        return f"#{r:02x}{g:02x}{b:02x}"

    def label(self, parent, text, font=FONT_BODY, fg=None, bg=None):
        return tk.Label(
            parent,
            text=text,
            bg=bg or COLORS["card"],
            fg=fg or COLORS["text"],
            font=font,
        )

    def entry(self, parent, width=30, show=None):
        field = tk.Entry(
            parent,
            width=width,
            font=FONT_BODY,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["accent2"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent2"],
        )
        if show:
            field.configure(show=show)
        return field

    def configure_tree_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=COLORS["input_bg"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["input_bg"],
            rowheight=30,
            font=FONT_BODY,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["accent"],
            foreground=COLORS["white"],
            font=FONT_BTN,
            borderwidth=0,
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["accent2"])],
            foreground=[("selected", COLORS["white"])],
        )

    def card(self, parent, padx=20, pady=20):
        frame = tk.Frame(
            parent,
            bg=COLORS["card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        frame.pack(fill="both", expand=True, padx=padx, pady=pady)
        return frame

    # ==================== LOGIN ====================

    def show_login(self):
        self.clear_root()

        self.add_footer(self.root)
        container = tk.Frame(self.root, bg=COLORS["bg"])
        container.pack(fill="both", expand=True)

        panel = tk.Frame(
            container,
            bg=COLORS["card"],
            width=430,
            height=470,
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        panel.place(relx=0.5, rely=0.5, anchor="center")
        panel.pack_propagate(False)

        tk.Label(
            panel,
            text="◉",
            bg=COLORS["card"],
            fg=COLORS["accent2"],
            font=("Segoe UI", 40, "bold"),
        ).pack(pady=(30, 0))

        self.label(
            panel,
            "PARKING MANAGEMENT",
            font=("Segoe UI", 20, "bold"),
        ).pack(pady=(5, 0))

        self.label(
            panel,
            "Secure staff access",
            fg=COLORS["subtext"],
        ).pack(pady=(3, 25))

        self.label(panel, "Username").pack(anchor="w", padx=55)
        self.login_user = self.entry(panel, width=32)
        self.login_user.pack(padx=55, pady=(5, 15))

        self.label(panel, "Password").pack(anchor="w", padx=55)
        self.login_password = self.entry(
            panel, width=32, show="*"
        )
        self.login_password.pack(padx=55, pady=(5, 20))

        actions = tk.Frame(panel, bg=COLORS["card"])
        actions.pack(pady=(0, 10))

        self.make_button(
            actions,
            "LOGIN",
            self.login,
            COLORS["accent"],
            width=16,
        ).pack(side="left", padx=(0, 10))

        self.make_button(
            actions,
            "CREATE ACCOUNT",
            self.show_customer_signup,
            COLORS["accent3"],
            width=16,
        ).pack(side="left")

        self.login_password.bind("<Return>", lambda event: self.login())
        self.login_user.focus_set()

    def show_customer_signup(self):
        signup = tk.Toplevel(self.root)
        signup.title("Create Customer Account")
        signup.geometry("430x460")
        signup.minsize(430, 460)
        signup.configure(bg=COLORS["bg"])
        signup.transient(self.root)
        signup.grab_set()

        self.add_footer(signup)
        tk.Label(
            signup,
            text="Create Customer Account",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            font=FONT_TITLE,
        ).pack(pady=(20, 15))

        form = tk.Frame(signup, bg=COLORS["bg"])
        form.pack(padx=20, pady=10, fill="x")

        self.label(form, "Full Name").pack(anchor="w")
        full_name = self.entry(form, width=32)
        full_name.pack(fill="x", pady=(5, 10))

        self.label(form, "Username").pack(anchor="w")
        username = self.entry(form, width=32)
        username.pack(fill="x", pady=(5, 10))

        self.label(form, "Password").pack(anchor="w")
        password = self.entry(form, width=32, show="*")
        password.pack(fill="x", pady=(5, 10))

        def submit():
            name = clean_text(full_name.get(), 80)
            user = username.get().strip()
            pwd = password.get()

            if not valid_name(name):
                messagebox.showwarning(
                    "Invalid Name",
                    "Enter a valid full name.",
                )
                return

            if not valid_username(user):
                messagebox.showwarning(
                    "Invalid Username",
                    "Username must be 3–30 characters using letters, numbers, _, -, or .",
                )
                return

            if not valid_password(pwd):
                messagebox.showwarning(
                    "Weak Password",
                    "Password must contain at least 8 characters.",
                )
                return

            try:
                self.db.create_user(user, pwd, name, "customer", None)
            except ValueError as error:
                messagebox.showerror("Account Creation Failed", str(error))
                return

            messagebox.showinfo(
                "Account Created",
                f"Customer account {user} was created successfully.",
            )
            signup.destroy()

        actions = tk.Frame(form, bg=COLORS["bg"])
        actions.pack(fill="x", pady=(12, 18))

        self.make_button(
            actions,
            "CANCEL",
            signup.destroy,
            COLORS["danger"],
            width=12,
        ).pack(side="left")

        self.make_button(
            actions,
            "OK",
            submit,
            COLORS["accent"],
            width=12,
        ).pack(side="right", padx=(10, 0))

        full_name.bind("<Return>", lambda event: submit())
        username.bind("<Return>", lambda event: submit())
        password.bind("<Return>", lambda event: submit())
        full_name.focus_set()

    def login(self):
        username = self.login_user.get().strip()

        locked, seconds = self.limiter.is_locked(username)
        if locked:
            messagebox.showwarning(
                "Temporarily Locked",
                f"Too many failed attempts.\nTry again in {seconds} seconds.",
            )
            return

        password = self.login_password.get()

        if not username or not password:
            messagebox.showwarning(
                "Missing Information",
                "Enter both username and password.",
            )
            return

        user = self.db.authenticate(username)

        if not user or not verify_password(
            password, user["password_hash"]
        ):
            self.limiter.failed(username)
            messagebox.showerror(
                "Login Failed",
                "Invalid username or password.",
            )
            return

        self.limiter.success(username)
        self.current_user = dict(user)
        self.db.record_login(user["id"])
        self.db.log(
            user["id"],
            "LOGIN",
            "Successful login",
        )

        self.show_main_app()

    def logout(self):
        if self.current_user:
            self.db.log(
                self.current_user["id"],
                "LOGOUT",
                "User logged out",
            )
        self.current_user = None
        self.show_login()

    # ==================== MAIN SHELL ====================

    def show_main_app(self):
        self.clear_root()

        header = tk.Frame(
            self.root,
            bg=COLORS["card"],
            height=70,
        )
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        self.add_footer(self.root)

        tk.Label(
            header,
            text="🚗  MODERN PARKING MANAGEMENT",
            bg=COLORS["card"],
            fg=COLORS["text"],
            font=FONT_TITLE,
        ).pack(side="left", padx=22)

        user_text = (
            f"{self.current_user['full_name']}  •  "
            f"{self.current_user['role'].upper()}"
        )

        tk.Label(
            header,
            text=user_text,
            bg=COLORS["card"],
            fg=COLORS["accent2"],
            font=FONT_BTN,
        ).pack(side="right", padx=22)

        self.sidebar = tk.Frame(
            self.root,
            bg=COLORS["card"],
            width=220,
        )
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)

        self.main = tk.Frame(
            self.root,
            bg=COLORS["bg"],
        )
        self.main.pack(
            fill="both",
            expand=True,
        )

        self.build_sidebar()
        self.show_dashboard()

    def build_sidebar(self):
        role = self.current_user["role"]

        if role == "admin":
            items = [
                ("🏠  Dashboard", self.show_dashboard),
                ("🅿️  Park Vehicle", self.show_park),
                ("📋  Parked Vehicles", self.show_parked),
                ("💳  Checkout", self.show_checkout),
                ("🔎  Search", self.show_search),
                ("💰  Payments", self.show_payments),
                ("📊  Reports", self.show_reports),
                ("📝  Activity Log", self.show_activity),
                ("👥  Users", self.show_users),
                ("⚙  Settings", self.show_settings),
            ]
        elif role == "attendant":
            items = [
                ("🏠  Dashboard", self.show_dashboard),
                ("🅿️  Park Vehicle", self.show_park),
                ("📋  Parked Vehicles", self.show_parked),
                ("💳  Checkout", self.show_checkout),
                ("🔎  Search", self.show_search),
                ("💰  Payments", self.show_payments),
                ("📊  Reports", self.show_reports),
                ("📝  Activity Log", self.show_activity),
            ]
        else:
            items = [
                ("🏠  Dashboard", self.show_dashboard),
                ("🅿️  Park Vehicle", self.show_park),
                ("💳  Checkout", self.show_checkout),
            ]

        for text, command in items:
            button = tk.Button(
                self.sidebar,
                text=text,
                command=command,
                bg=COLORS["card"],
                fg=COLORS["text"],
                activebackground=COLORS["accent"],
                activeforeground=COLORS["white"],
                font=FONT_BTN,
                anchor="w",
                padx=18,
                pady=11,
                bd=0,
                cursor="hand2",
            )
            button.pack(fill="x")
            button.bind(
                "<Enter>",
                lambda event, w=button:
                w.configure(bg=COLORS["accent"]),
            )
            button.bind(
                "<Leave>",
                lambda event, w=button:
                w.configure(bg=COLORS["card"]),
            )

        tk.Frame(
            self.sidebar,
            bg=COLORS["card"],
        ).pack(fill="both", expand=True)

        self.make_button(
            self.sidebar,
            "🚪  Logout",
            self.logout,
            COLORS["danger"],
        ).pack(fill="x", padx=12, pady=12)

    # ==================== DASHBOARD ====================

    def show_dashboard(self):
        self.clear_main()

        stats = self.db.dashboard_stats()

        top = tk.Frame(self.main, bg=COLORS["bg"])
        top.pack(fill="x", padx=25, pady=(25, 10))

        self.label(
            top,
            "Dashboard",
            font=FONT_TITLE,
            bg=COLORS["bg"],
        ).pack(side="left")

        self.label(
            top,
            dt.datetime.now().strftime("%d %b %Y  •  %H:%M"),
            fg=COLORS["subtext"],
            bg=COLORS["bg"],
        ).pack(side="right")

        subtitle = self.label(
            self.main,
            "Live overview of your parking facility",
            fg=COLORS["subtext"],
            bg=COLORS["bg"],
        )
        subtitle.pack(anchor="w", padx=25)

        tiles = tk.Frame(
            self.main,
            bg=COLORS["bg"],
        )
        tiles.pack(fill="x", padx=25, pady=20)

        self.stat_tile(
            tiles, "AVAILABLE", stats["available"], COLORS["accent2"]
        )
        self.stat_tile(
            tiles, "OCCUPIED", stats["occupied"], COLORS["danger"]
        )
        self.stat_tile(
            tiles, "TOTAL SLOTS", stats["total"], COLORS["accent"]
        )
        if self.current_user["role"] != "customer":
            self.stat_tile(
                tiles, "REVENUE", f"KSh {stats['revenue']:,}", COLORS["accent3"]
            )

        lower = tk.Frame(self.main, bg=COLORS["bg"])
        lower.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        left = tk.Frame(
            lower,
            bg=COLORS["card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10),
        )

        self.label(
            left,
            "PARKING STATUS",
            font=FONT_HEAD,
        ).pack(anchor="w", padx=18, pady=(18, 10))

        grid = tk.Frame(left, bg=COLORS["card"])
        grid.pack(padx=15, pady=5)

        for index, slot in enumerate(self.db.slot_status()):
            row = index // 5
            col = index % 5

            occupied = slot["status"] == "occupied"
            color = COLORS["danger"] if occupied else COLORS["accent3"]
            text = "BUSY" if occupied else "FREE"

            tile = tk.Frame(
                grid,
                bg=color,
                width=90,
                height=58,
            )
            tile.grid(row=row, column=col, padx=5, pady=5)
            tile.pack_propagate(False)

            tk.Label(
                tile,
                text=slot["slot_code"],
                bg=color,
                fg="white",
                font=FONT_BTN,
            ).pack(pady=(8, 0))

            tk.Label(
                tile,
                text=text,
                bg=color,
                fg="white",
                font=FONT_SMALL,
            ).pack()

        if self.current_user["role"] != "customer":
            right = tk.Frame(
                lower,
                bg=COLORS["card"],
                highlightbackground=COLORS["border"],
                highlightthickness=1,
                width=350,
            )
            right.pack(
                side="right",
                fill="y",
                padx=(10, 0),
            )
            right.pack_propagate(False)

            self.label(
                right,
                "RECENT ACTIVITY",
                font=FONT_HEAD,
            ).pack(anchor="w", padx=18, pady=(18, 10))

            logs = self.db.logs(8)

            for log in logs:
                text = (
                    f"{log['created_at'][11:16]}  "
                    f"{log['action']}\n"
                    f"{log['details'][:45]}"
                )
                self.label(
                    right,
                    text,
                    font=FONT_SMALL,
                    fg=COLORS["subtext"],
                ).pack(anchor="w", padx=18, pady=5)

    def stat_tile(self, parent, title, value, color):
        tile = tk.Frame(
            parent,
            bg=COLORS["card"],
            width=190,
            height=105,
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        tile.pack(side="left", padx=(0, 12))
        tile.pack_propagate(False)

        tk.Label(
            tile,
            text=str(value),
            bg=COLORS["card"],
            fg=color,
            font=("Segoe UI", 21, "bold"),
        ).pack(pady=(16, 0))

        tk.Label(
            tile,
            text=title,
            bg=COLORS["card"],
            fg=COLORS["subtext"],
            font=FONT_SMALL,
        ).pack()

    # ==================== PARK ====================

    def show_park(self):
        self.clear_main()
        card = self.card(self.main)

        self.label(
            card, "Park a Vehicle", font=FONT_TITLE
        ).pack(anchor="w", padx=25, pady=(25, 5))

        self.label(
            card,
            "Register a vehicle and automatically assign an available slot.",
            fg=COLORS["subtext"],
        ).pack(anchor="w", padx=25, pady=(0, 20))

        form = tk.Frame(card, bg=COLORS["card"])
        form.pack(anchor="w", padx=25)

        self.park_owner = self.form_field(form, "Owner Name", 0)
        self.park_phone = self.form_field(form, "Phone Number", 1)
        self.park_reg = self.form_field(form, "Registration No.", 2)

        self.label(
            form,
            "Vehicle Type",
        ).grid(row=3, column=0, sticky="w", pady=9)

        self.park_type = ttk.Combobox(
            form,
            values=["car", "bike", "truck", "bus"],
            state="readonly",
            width=28,
            font=FONT_BODY,
        )
        self.park_type.set("car")
        self.park_type.grid(
            row=3, column=1, padx=12, pady=9
        )

        self.make_button(
            card,
            "🅿️  PARK VEHICLE",
            self.park_action,
            COLORS["accent"],
        ).pack(anchor="w", padx=25, pady=25)

    def form_field(self, parent, text, row):
        self.label(parent, text).grid(
            row=row,
            column=0,
            sticky="w",
            pady=9,
        )
        field = self.entry(parent, width=30)
        field.grid(row=row, column=1, padx=12, pady=9)
        return field

    def park_action(self):
        owner = clean_text(self.park_owner.get(), 80)
        phone = self.park_phone.get().strip()
        reg = normalize_registration(self.park_reg.get())
        vehicle_type = self.park_type.get()

        if not valid_name(owner):
            messagebox.showwarning(
                "Invalid Owner",
                "Enter a valid owner name.",
            )
            return

        if not valid_phone(phone):
            messagebox.showwarning(
                "Invalid Phone",
                "Use a Kenyan mobile number such as 0712345678 or +254712345678.",
            )
            return

        if not valid_registration(reg):
            messagebox.showwarning(
                "Invalid Registration",
                "Use 3–12 letters, numbers, spaces or hyphens.",
            )
            return

        try:
            session_id, slot, arrival = self.db.park_vehicle(
                reg,
                owner,
                phone,
                vehicle_type,
                self.current_user["id"],
            )
        except ValueError as error:
            messagebox.showerror("Unable to Park", str(error))
            return

        messagebox.showinfo(
            "Vehicle Parked",
            f"Vehicle: {reg}\n"
            f"Owner: {owner}\n"
            f"Slot: {slot}\n"
            f"Arrival: {arrival}",
        )
        self.show_dashboard()

    # ==================== PARKED ====================

    def show_parked(self):
        self.clear_main()
        card = self.card(self.main)

        self.label(
            card,
            "Currently Parked Vehicles",
            font=FONT_TITLE,
        ).pack(anchor="w", padx=20, pady=(20, 15))

        self.configure_tree_style()

        cols = (
            "reg", "owner", "phone",
            "type", "slot", "arrival"
        )

        tree = ttk.Treeview(
            card,
            columns=cols,
            show="headings",
        )

        headings = {
            "reg": "Registration",
            "owner": "Owner",
            "phone": "Phone",
            "type": "Type",
            "slot": "Slot",
            "arrival": "Arrival",
        }

        widths = {
            "reg": 110,
            "owner": 160,
            "phone": 120,
            "type": 80,
            "slot": 70,
            "arrival": 160,
        }

        for col in cols:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="w")

        tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        for row in self.db.parked_vehicles():
            tree.insert(
                "",
                "end",
                values=(
                    row["reg_no"],
                    row["owner_name"],
                    row["phone"],
                    row["vehicle_type"],
                    row["slot_code"],
                    row["arrival"],
                ),
            )

    # ==================== CHECKOUT ====================

    def show_checkout(self):
        self.clear_main()
        card = self.card(self.main)

        self.label(
            card,
            "Checkout Vehicle",
            font=FONT_TITLE,
        ).pack(anchor="w", padx=25, pady=(25, 5))

        self.label(
            card,
            "Calculate the bill, record payment and release the parking slot.",
            fg=COLORS["subtext"],
        ).pack(anchor="w", padx=25, pady=(0, 20))

        form = tk.Frame(card, bg=COLORS["card"])
        form.pack(anchor="w", padx=25)

        self.checkout_reg = self.form_field(
            form, "Registration No.", 0
        )

        self.label(
            form,
            "Payment Method",
        ).grid(row=1, column=0, sticky="w", pady=9)

        self.payment_method = ttk.Combobox(
            form,
            values=["Cash", "M-Pesa", "Card"],
            state="readonly",
            width=28,
            font=FONT_BODY,
        )
        self.payment_method.set("Cash")
        self.payment_method.grid(
            row=1, column=1, padx=12, pady=9
        )

        self.checkout_info = self.label(
            card,
            "Enter a registration number and click Find.",
            fg=COLORS["subtext"],
        )
        self.checkout_info.pack(anchor="w", padx=25, pady=20)

        actions = tk.Frame(card, bg=COLORS["card"])
        actions.pack(anchor="w", padx=25)

        self.make_button(
            actions,
            "🔎  FIND VEHICLE",
            self.preview_checkout,
            COLORS["accent3"],
        ).pack(side="left", padx=(0, 10))

        self.make_button(
            actions,
            "💳  CHECKOUT & PAY",
            self.checkout_action,
            COLORS["accent"],
        ).pack(side="left")

    def preview_checkout(self):
        reg = normalize_registration(self.checkout_reg.get())

        if not valid_registration(reg):
            messagebox.showwarning(
                "Invalid Registration",
                "Enter a valid registration number.",
            )
            return

        row = self.db.find_active_vehicle(reg)

        if not row:
            self.checkout_info.config(
                text="Vehicle not found or already checked out.",
                fg=COLORS["danger"],
            )
            return

        self.checkout_info.config(
            text=(
                f"Owner: {row['owner_name']}    "
                f"Type: {row['vehicle_type']}    "
                f"Slot: {row['slot_code']}    "
                f"Arrival: {row['arrival']}"
            ),
            fg=COLORS["accent2"],
        )

    def checkout_action(self):
        reg = normalize_registration(self.checkout_reg.get())

        if not valid_registration(reg):
            messagebox.showwarning(
                "Invalid Registration",
                "Enter a valid registration number.",
            )
            return

        if not self.db.find_active_vehicle(reg):
            messagebox.showerror(
                "Not Found",
                "No active vehicle was found.",
            )
            return

        method = self.payment_method.get()

        if not messagebox.askyesno(
            "Confirm Checkout",
            f"Checkout {reg} and record payment using {method}?",
        ):
            return

        try:
            receipt = self.db.checkout(
                reg,
                self.current_user["id"],
                method,
            )
        except ValueError as error:
            messagebox.showerror(
                "Checkout Failed",
                str(error),
            )
            return

        receipt_text = (
            f"MODERN PARKING SYSTEM\n"
            f"{'=' * 32}\n"
            f"Receipt: {receipt['receipt_no']}\n"
            f"Registration: {receipt['reg_no']}\n"
            f"Owner: {receipt['owner']}\n"
            f"Vehicle: {receipt['vehicle_type']}\n"
            f"Slot: {receipt['slot']}\n"
            f"Arrival: {receipt['arrival']}\n"
            f"Departure: {receipt['departure']}\n"
            f"Hours: {receipt['hours']}\n"
            f"Rate: KSh {receipt['rate']}/hr\n"
            f"Payment: {receipt['payment_method']}\n"
            f"{'=' * 32}\n"
            f"TOTAL: KSh {receipt['amount']:,}"
        )

        messagebox.showinfo("Payment Receipt", receipt_text)
        self.show_dashboard()

    # ==================== SEARCH ====================

    def show_search(self):
        self.clear_main()
        card = self.card(self.main)

        self.label(
            card,
            "Search Vehicle",
            font=FONT_TITLE,
        ).pack(anchor="w", padx=25, pady=(25, 5))

        self.label(
            card,
            "Search by registration, owner name or phone number.",
            fg=COLORS["subtext"],
        ).pack(anchor="w", padx=25, pady=(0, 15))

        controls = tk.Frame(card, bg=COLORS["card"])
        controls.pack(anchor="w", padx=25, pady=10)

        self.search_input = self.entry(controls, width=35)
        self.search_input.pack(side="left", padx=(0, 10))

        self.make_button(
            controls,
            "🔎 SEARCH",
            self.search_action,
        ).pack(side="left")

        self.configure_tree_style()

        cols = (
            "reg", "owner", "phone",
            "type", "status", "slot", "arrival"
        )

        self.search_tree = ttk.Treeview(
            card,
            columns=cols,
            show="headings",
        )

        headings = {
            "reg": "Registration",
            "owner": "Owner",
            "phone": "Phone",
            "type": "Type",
            "status": "Status",
            "slot": "Slot",
            "arrival": "Arrival",
        }

        for col in cols:
            self.search_tree.heading(col, text=headings[col])

        self.search_tree.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20,
        )

    def search_action(self):
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)

        term = self.search_input.get().strip()

        if not term:
            return

        for row in self.db.search(term):
            self.search_tree.insert(
                "",
                "end",
                values=(
                    row["reg_no"],
                    row["owner_name"],
                    row["phone"],
                    row["vehicle_type"],
                    row["status"],
                    row["slot_code"] or "-",
                    row["arrival"] or "-",
                ),
            )

    # ==================== PAYMENTS ====================

    def show_payments(self):
        self.clear_main()
        card = self.card(self.main)

        self.label(
            card,
            "Payment History",
            font=FONT_TITLE,
        ).pack(anchor="w", padx=20, pady=(20, 15))

        self.configure_tree_style()

        cols = (
            "receipt", "reg", "owner",
            "hours", "amount", "method",
            "paid", "staff"
        )

        tree = ttk.Treeview(
            card,
            columns=cols,
            show="headings",
        )

        headings = {
            "receipt": "Receipt",
            "reg": "Registration",
            "owner": "Owner",
            "hours": "Hours",
            "amount": "Amount",
            "method": "Method",
            "paid": "Paid At",
            "staff": "Staff",
        }

        for col in cols:
            tree.heading(col, text=headings[col])

        tree.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20),
        )

        for row in self.db.payments():
            tree.insert(
                "",
                "end",
                values=(
                    row["receipt_no"],
                    row["reg_no"],
                    row["owner_name"],
                    row["billable_hours"],
                    f"KSh {row['amount']:,}",
                    row["payment_method"],
                    row["paid_at"],
                    row["username"],
                ),
            )

    # ==================== REPORTS ====================

    def show_reports(self):
        self.clear_main()
        card = self.card(self.main)

        self.label(
            card,
            "Reports",
            font=FONT_TITLE,
        ).pack(anchor="w", padx=25, pady=(25, 5))

        self.label(
            card,
            "Revenue and transaction summary.",
            fg=COLORS["subtext"],
        ).pack(anchor="w", padx=25, pady=(0, 20))

        report = self.db.report(30)

        data = [
            ("Transactions", report["transactions"]),
            ("Total Revenue", f"KSh {report['revenue']:,}"),
            ("Cash", f"KSh {report['cash']:,}"),
            ("M-Pesa", f"KSh {report['mpesa']:,}"),
            ("Card", f"KSh {report['card']:,}"),
        ]

        for title, value in data:
            row = tk.Frame(card, bg=COLORS["input_bg"])
            row.pack(fill="x", padx=25, pady=5)

            self.label(
                row,
                title,
                bg=COLORS["input_bg"],
            ).pack(side="left", padx=15, pady=12)

            self.label(
                row,
                str(value),
                font=FONT_HEAD,
                fg=COLORS["accent2"],
                bg=COLORS["input_bg"],
            ).pack(side="right", padx=15, pady=12)

        self.label(
            card,
            "Report period: last 30 days",
            font=FONT_SMALL,
            fg=COLORS["subtext"],
        ).pack(anchor="w", padx=25, pady=15)

    # ==================== ACTIVITY ====================

    def show_activity(self):
        self.clear_main()
        card = self.card(self.main)

        self.label(
            card,
            "Activity Log",
            font=FONT_TITLE,
        ).pack(anchor="w", padx=20, pady=(20, 15))

        self.configure_tree_style()

        cols = ("time", "user", "action", "details")
        tree = ttk.Treeview(
            card,
            columns=cols,
            show="headings",
        )

        for col, heading in zip(
            cols,
            ["Time", "User", "Action", "Details"],
        ):
            tree.heading(col, text=heading)

        tree.column("time", width=160)
        tree.column("user", width=120)
        tree.column("action", width=120)
        tree.column("details", width=500)

        tree.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20),
        )

        for row in self.db.logs():
            tree.insert(
                "",
                "end",
                values=(
                    row["created_at"],
                    row["username"],
                    row["action"],
                    row["details"],
                ),
            )

    # ==================== USERS ====================

    def show_users(self):
        if self.current_user["role"] != "admin":
            messagebox.showerror(
                "Access Denied",
                "Administrator access is required.",
            )
            return

        self.clear_main()
        card = self.card(self.main)

        self.label(
            card,
            "User Management",
            font=FONT_TITLE,
        ).pack(anchor="w", padx=20, pady=(20, 15))

        form = tk.Frame(card, bg=COLORS["card"])
        form.pack(anchor="w", padx=20, pady=5)

        self.user_full_name = self.entry(form, 18)
        self.user_username = self.entry(form, 15)
        self.user_password = self.entry(form, 15, show="*")

        fields = [
            ("Full Name", self.user_full_name),
            ("Username", self.user_username),
            ("Password", self.user_password),
        ]

        for col, (title, field) in enumerate(fields):
            self.label(form, title).grid(
                row=0, column=col, padx=5, sticky="w"
            )
            field.grid(
                row=1, column=col, padx=5, pady=5
            )

        self.user_role = ttk.Combobox(
            form,
            values=["admin", "attendant", "customer"],
            state="readonly",
            width=12,
        )
        self.user_role.set("customer")
        self.user_role.grid(row=1, column=3, padx=5)

        self.make_button(
            form,
            "CREATE USER",
            self.create_user,
        ).grid(row=1, column=4, padx=10)

        self.configure_tree_style()

        cols = (
            "id", "username", "name",
            "role", "active", "last_login"
        )

        tree = ttk.Treeview(
            card,
            columns=cols,
            show="headings",
        )

        for col, heading in zip(
            cols,
            ["ID", "Username", "Full Name", "Role", "Active", "Last Login"],
        ):
            tree.heading(col, text=heading)

        tree.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20,
        )

        for row in self.db.users():
            tree.insert(
                "",
                "end",
                values=(
                    row["id"],
                    row["username"],
                    row["full_name"],
                    row["role"],
                    "YES" if row["active"] else "NO",
                    row["last_login"] or "-",
                ),
            )

        self.make_button(
            card,
            "ENABLE / DISABLE SELECTED USER",
            lambda: self.toggle_selected_user(tree),
            COLORS["danger"],
        ).pack(anchor="w", padx=20, pady=(0, 15))

    def create_user(self):
        name = clean_text(self.user_full_name.get(), 80)
        username = self.user_username.get().strip()
        password = self.user_password.get()
        role = self.user_role.get()

        if not valid_name(name):
            messagebox.showwarning(
                "Invalid Name",
                "Enter a valid full name.",
            )
            return

        if not valid_username(username):
            messagebox.showwarning(
                "Invalid Username",
                "Username must be 3–30 characters using letters, numbers, _, -, or .",
            )
            return

        if not valid_password(password):
            messagebox.showwarning(
                "Weak Password",
                "Password must contain at least 8 characters.",
            )
            return

        try:
            self.db.create_user(
                username,
                password,
                name,
                role,
                self.current_user["id"],
            )
        except ValueError as error:
            messagebox.showerror("Cannot Create User", str(error))
            return

        messagebox.showinfo(
            "User Created",
            f"User {username} was created successfully.",
        )
        self.show_users()

    def toggle_selected_user(self, tree):
        selection = tree.selection()

        if not selection:
            messagebox.showwarning(
                "Select User",
                "Select a user first.",
            )
            return

        values = tree.item(selection[0], "values")
        user_id = int(values[0])

        if user_id == self.current_user["id"]:
            messagebox.showwarning(
                "Not Allowed",
                "You cannot disable your own account.",
            )
            return

        try:
            self.db.toggle_user(
                user_id,
                self.current_user["id"],
            )
        except ValueError as error:
            messagebox.showerror(
                "Operation Failed",
                str(error),
            )
            return

        self.show_users()

    # ==================== SETTINGS ====================

    def show_settings(self):
        if self.current_user["role"] != "admin":
            messagebox.showerror(
                "Access Denied",
                "Administrator access is required.",
            )
            return

        self.clear_main()
        card = self.card(self.main)

        self.label(
            card,
            "System Settings",
            font=FONT_TITLE,
        ).pack(anchor="w", padx=25, pady=(25, 5))

        self.label(
            card,
            "Configure hourly parking rates and create database backups.",
            fg=COLORS["subtext"],
        ).pack(anchor="w", padx=25, pady=(0, 20))

        rates = self.db.get_rates()
        self.rate_entries = {}

        form = tk.Frame(card, bg=COLORS["card"])
        form.pack(anchor="w", padx=25)

        for row, vehicle_type in enumerate(
            ["car", "bike", "truck", "bus"]
        ):
            self.label(
                form,
                f"{vehicle_type.title()} rate / hour",
            ).grid(row=row, column=0, sticky="w", pady=8)

            field = self.entry(form, width=15)
            field.insert(0, str(rates[vehicle_type.upper()]))
            field.grid(row=row, column=1, padx=15, pady=8)

            self.rate_entries[vehicle_type] = field

        self.make_button(
            card,
            "SAVE RATES",
            self.save_rates,
            COLORS["accent"],
        ).pack(anchor="w", padx=25, pady=20)

        backup_frame = tk.Frame(
            card,
            bg=COLORS["input_bg"],
        )
        backup_frame.pack(
            fill="x",
            padx=25,
            pady=10,
        )

        self.label(
            backup_frame,
            "Database backup",
            font=FONT_HEAD,
            bg=COLORS["input_bg"],
        ).pack(side="left", padx=15, pady=15)

        self.make_button(
            backup_frame,
            "CREATE BACKUP",
            self.create_backup,
            COLORS["accent3"],
        ).pack(side="right", padx=15, pady=10)

    def save_rates(self):
        rates = {}

        for vehicle_type, field in self.rate_entries.items():
            try:
                value = int(field.get())
                if value <= 0 or value > 100000:
                    raise ValueError
            except ValueError:
                messagebox.showwarning(
                    "Invalid Rate",
                    "Rates must be positive whole numbers.",
                )
                return

            rates[vehicle_type] = value

        self.db.update_rates(
            rates,
            self.current_user["id"],
        )

        messagebox.showinfo(
            "Settings Saved",
            "Parking rates have been updated.",
        )

    def create_backup(self):
        try:
            path = self.db.backup()
        except Exception as error:
            messagebox.showerror(
                "Backup Failed",
                str(error),
            )
            return

        self.db.log(
            self.current_user["id"],
            "BACKUP",
            f"Database backup created: {path.name}",
        )

        messagebox.showinfo(
            "Backup Created",
            f"Backup saved as:\n{path.name}",
        )
