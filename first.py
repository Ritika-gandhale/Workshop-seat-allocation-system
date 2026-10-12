import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error


# ---------- DATABASE CONNECTION ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456789",
    "database": "workshop_db"
}


def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


def setup_database():
    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS workshop_seats (
            seat_id INT AUTO_INCREMENT PRIMARY KEY,
            participant_name VARCHAR(100) NOT NULL,
            phone VARCHAR(10) NOT NULL,
            workshop_name VARCHAR(100) NOT NULL,
            seat_number INT NOT NULL,
            UNIQUE (workshop_name, seat_number)
        )
    """)

    cur.execute("""
        INSERT IGNORE INTO users (username, password)
        VALUES ('admin', 'admin123')
    """)

    con.commit()
    cur.close()
    con.close()


# ---------- MAIN APPLICATION ----------
root = tk.Tk()
root.title("Workshop Seat Allocation System")
root.geometry("1050x700")
root.configure(bg="#edf2f7")

current_user = None
selected_id = None


def db_error(error):
    messagebox.showerror("Database Error", str(error), parent=root)


# ---------- LOGIN PAGE ----------
def login_page():
    global current_user

    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="#eaf2f8")

    box = tk.Frame(root, bg="white", padx=40, pady=35)
    box.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        box, text="WORKSHOP SEAT ALLOCATION",
        font=("Arial", 20, "bold"),
        bg="white", fg="#154360"
    ).pack(pady=15)

    tk.Label(box, text="Username", bg="white").pack(anchor="w")
    username = tk.Entry(box, width=32, font=("Arial", 12))
    username.pack(pady=7)

    tk.Label(box, text="Password", bg="white").pack(anchor="w")
    password = tk.Entry(box, width=32, show="*", font=("Arial", 12))
    password.pack(pady=7)

    def check_login():
        global current_user

        u = username.get().strip()
        p = password.get()

        if not u or not p:
            messagebox.showwarning(
                "Validation", "Enter username and password", parent=box
            )
            return

        try:
            con = connect_db()
            cur = con.cursor()
            cur.execute(
                "SELECT id FROM users WHERE username=%s AND password=%s",
                (u, p)
            )
            result = cur.fetchone()
            cur.close()
            con.close()

            if result:
                current_user = u
                dashboard()
            else:
                messagebox.showerror(
                    "Login Failed", "Invalid username or password",
                    parent=box
                )

        except Error as e:
            messagebox.showerror("Database Error", str(e), parent=box)

    tk.Button(
        box, text="Login", command=check_login,
        bg="#2471a3", fg="white",
        font=("Arial", 12, "bold"), width=25
    ).pack(pady=18)

    tk.Label(
        box, text="Default login: admin / admin123",
        bg="white", fg="#666666"
    ).pack()


# ---------- DASHBOARD ----------
def dashboard():
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="#edf2f7")

    header = tk.Frame(root, bg="#154360", pady=15)
    header.pack(fill="x")

    tk.Label(
        header, text="WORKSHOP SEAT ALLOCATION SYSTEM",
        font=("Arial", 20, "bold"),
        bg="#154360", fg="white"
    ).pack()

    tk.Label(
        header, text=f"Logged in: {current_user}",
        bg="#154360", fg="white"
    ).pack(pady=5)

    global name_entry, phone_entry, workshop_entry
    global seat_entry, search_entry, tree

    form = tk.LabelFrame(
        root, text="Participant Details",
        font=("Arial", 12, "bold"), padx=12, pady=12,
        bg="#edf2f7"
    )
    form.pack(fill="x", padx=15, pady=10)

    tk.Label(form, text="Participant Name", bg="#edf2f7").grid(
        row=0, column=0, sticky="w", padx=5, pady=5
    )
    name_entry = tk.Entry(form, width=25)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(form, text="Phone Number", bg="#edf2f7").grid(
        row=0, column=2, sticky="w", padx=5, pady=5
    )
    phone_entry = tk.Entry(form, width=22)
    phone_entry.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(form, text="Workshop Name", bg="#edf2f7").grid(
        row=1, column=0, sticky="w", padx=5, pady=5
    )
    workshop_entry = tk.Entry(form, width=25)
    workshop_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(form, text="Seat Number", bg="#edf2f7").grid(
        row=1, column=2, sticky="w", padx=5, pady=5
    )
    seat_entry = tk.Entry(form, width=22)
    seat_entry.grid(row=1, column=3, padx=5, pady=5)

    tk.Label(
        form,
        text="Leave Seat Number empty for automatic allocation.",
        bg="#edf2f7", fg="#555555"
    ).grid(row=2, column=0, columnspan=4, sticky="w", padx=5)

    # ---------- RECORD TABLE ----------
    table_frame = tk.Frame(root, bg="#edf2f7")
    table_frame.pack(fill="both", expand=True, padx=15, pady=5)

    columns = (
        "seat_id", "participant_name", "phone",
        "workshop_name", "seat_number"
    )

    tree = ttk.Treeview(
        table_frame, columns=columns,
        show="headings", height=12
    )

    headings = {
        "seat_id": "ID",
        "participant_name": "Participant Name",
        "phone": "Phone",
        "workshop_name": "Workshop",
        "seat_number": "Seat Number"
    }

    widths = {
        "seat_id": 50,
        "participant_name": 220,
        "phone": 130,
        "workshop_name": 250,
        "seat_number": 100
    }

    for col in columns:
        tree.heading(col, text=headings[col])
        tree.column(col, width=widths[col], anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame, orient="vertical", command=tree.yview
    )
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    tree.bind("<<TreeviewSelect>>", select_record)

    # ---------- SEARCH ----------
    search_frame = tk.Frame(root, bg="#edf2f7")
    search_frame.pack(fill="x", padx=15, pady=5)

    tk.Label(
        search_frame, text="Search by name, phone or workshop:",
        bg="#edf2f7"
    ).pack(side="left")

    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side="left", padx=8)

    tk.Button(
        search_frame, text="Search",
        command=search_records, bg="#2471a3", fg="white"
    ).pack(side="left", padx=3)

    tk.Button(
        search_frame, text="Show All",
        command=load_records
    ).pack(side="left", padx=3)

    # ---------- BUTTONS ----------
    buttons = tk.Frame(root, bg="#edf2f7")
    buttons.pack(pady=12)

    tk.Button(
        buttons, text="Register / Allocate Seat",
        command=add_record, bg="#229954", fg="white",
        width=22
    ).grid(row=0, column=0, padx=5, pady=4)

    tk.Button(
        buttons, text="Update Selected",
        command=update_record, bg="#2471a3", fg="white",
        width=18
    ).grid(row=0, column=1, padx=5, pady=4)

    tk.Button(
        buttons, text="Delete Selected",
        command=delete_record, bg="#c0392b", fg="white",
        width=17
    ).grid(row=0, column=2, padx=5, pady=4)

    tk.Button(
        buttons, text="Clear / Reset",
        command=clear_form, width=15
    ).grid(row=0, column=3, padx=5, pady=4)

    tk.Button(
        buttons, text="Logout",
        command=login_page, width=12
    ).grid(row=0, column=4, padx=5, pady=4)

    load_records()


# ---------- CLEAR FORM ----------
def clear_form():
    global selected_id
    selected_id = None

    for entry in (
        name_entry, phone_entry, workshop_entry, seat_entry
    ):
        entry.delete(0, tk.END)

    for item in tree.selection():
        tree.selection_remove(item)


# ---------- VIEW RECORDS ----------
def load_records():
    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute("""
            SELECT seat_id, participant_name, phone,
                   workshop_name, seat_number
            FROM workshop_seats
            ORDER BY seat_id DESC
        """)
        rows = cur.fetchall()

        for item in tree.get_children():
            tree.delete(item)

        for row in rows:
            tree.insert("", "end", values=row)

        cur.close()
        con.close()

    except Error as e:
        db_error(e)


# ---------- SELECT RECORD ----------
def select_record(event=None):
    global selected_id

    selection = tree.selection()
    if not selection:
        return

    values = tree.item(selection[0], "values")
    selected_id = int(values[0])

    clear_entries_only()

    name_entry.insert(0, values[1])
    phone_entry.insert(0, values[2])
    workshop_entry.insert(0, values[3])
    seat_entry.insert(0, values[4])


def clear_entries_only():
    for entry in (
        name_entry, phone_entry, workshop_entry, seat_entry
    ):
        entry.delete(0, tk.END)


# ---------- VALIDATE FORM ----------
def get_form_data():
    name = name_entry.get().strip()
    phone = phone_entry.get().strip()
    workshop = workshop_entry.get().strip()
    seat_text = seat_entry.get().strip()

    if not name or not phone or not workshop:
        messagebox.showwarning(
            "Validation", "Fill name, phone and workshop fields",
            parent=root
        )
        return None

    if not phone.isdigit() or len(phone) != 10:
        messagebox.showwarning(
            "Validation", "Phone number must contain 10 digits",
            parent=root
        )
        return None

    if seat_text:
        if not seat_text.isdigit() or int(seat_text) <= 0:
            messagebox.showwarning(
                "Validation", "Seat number must be a positive integer",
                parent=root
            )
            return None
        seat = int(seat_text)
    else:
        seat = None

    return name, phone, workshop, seat


# ---------- ADD / ALLOCATE SEAT ----------
def add_record():
    data = get_form_data()
    if not data:
        return

    name, phone, workshop, seat = data

    try:
        con = connect_db()
        cur = con.cursor()

        if seat is None:
            cur.execute(
                """SELECT COALESCE(MAX(seat_number), 0) + 1
                   FROM workshop_seats WHERE workshop_name=%s""",
                (workshop,)
            )
            seat = cur.fetchone()[0]

        cur.execute(
            """INSERT INTO workshop_seats
               (participant_name, phone, workshop_name, seat_number)
               VALUES (%s, %s, %s, %s)""",
            (name, phone, workshop, seat)
        )

        con.commit()
        cur.close()
        con.close()

        messagebox.showinfo(
            "Success",
            f"Participant registered successfully!\nSeat Number: {seat}",
            parent=root
        )
        clear_form()
        load_records()

    except Error as e:
        try:
            con.rollback()
            con.close()
        except Exception:
            pass
        db_error(e)


# ---------- UPDATE RECORD ----------
def update_record():
    if selected_id is None:
        messagebox.showwarning(
            "Select Record", "Select a participant from the table first",
            parent=root
        )
        return

    data = get_form_data()
    if not data:
        return

    name, phone, workshop, seat = data

    try:
        con = connect_db()
        cur = con.cursor()

        if seat is None:
            cur.execute(
                """SELECT seat_number FROM workshop_seats
                   WHERE seat_id=%s""",
                (selected_id,)
            )
            old = cur.fetchone()
            seat = old[0] if old else None

        cur.execute(
            """UPDATE workshop_seats
               SET participant_name=%s, phone=%s,
                   workshop_name=%s, seat_number=%s
               WHERE seat_id=%s""",
            (name, phone, workshop, seat, selected_id)
        )

        con.commit()
        cur.close()
        con.close()

        messagebox.showinfo(
            "Success", "Record updated successfully", parent=root
        )
        clear_form()
        load_records()

    except Error as e:
        try:
            con.rollback()
            con.close()
        except Exception:
            pass
        db_error(e)


# ---------- DELETE RECORD ----------
def delete_record():
    if selected_id is None:
        messagebox.showwarning(
            "Select Record", "Select a participant from the table first",
            parent=root
        )
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this participant?",
        parent=root
    )

    if not confirm:
        return

    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute(
            "DELETE FROM workshop_seats WHERE seat_id=%s",
            (selected_id,)
        )
        con.commit()
        cur.close()
        con.close()

        messagebox.showinfo(
            "Success", "Participant deleted successfully", parent=root
        )
        clear_form()
        load_records()

    except Error as e:
        db_error(e)


# ---------- SEARCH RECORDS ----------
def search_records():
    keyword = search_entry.get().strip()

    try:
        con = connect_db()
        cur = con.cursor()

        cur.execute(
            """SELECT seat_id, participant_name, phone,
                      workshop_name, seat_number
               FROM workshop_seats
               WHERE participant_name LIKE %s
                  OR phone LIKE %s
                  OR workshop_name LIKE %s
               ORDER BY seat_id DESC""",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        )

        rows = cur.fetchall()

        for item in tree.get_children():
            tree.delete(item)

        for row in rows:
            tree.insert("", "end", values=row)

        cur.close()
        con.close()

        if not rows:
            messagebox.showinfo(
                "Search", "No matching records found", parent=root
            )

    except Error as e:
        db_error(e)


# ---------- START ----------
try:
    setup_database()
    login_page()
    root.mainloop()

except Error as e:
    messagebox.showerror(
        "Startup Error",
        f"Could not connect to MySQL.\n\n{e}\n\n"
        "Check DB_CONFIG password and MySQL Server."
    )