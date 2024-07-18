import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import mysql.connector

TASA_CAMBIO = 600

class ATM:
    def __init__(self, root):
        self.root = root
        self.root.title("Cajero Automático")
        self.root.geometry("1020x680")
        
        # Configuración de la imagen de fondo
        try:
            self.background_image = Image.open("C:\\Users\\eniga\\OneDrive\\Pictures\\background.jpg")
            self.background_photo = ImageTk.PhotoImage(self.background_image)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen de fondo: {e}")
            self.background_photo = None
        
        self.canvas = tk.Canvas(self.root, width=1020, height=680)
        self.canvas.pack(fill="both", expand=True)
        if self.background_photo:
            self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
        
        # Conectar a la base de datos y crear tablas
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="atm_db"
        )
        self.create_tables()

        self.balance = random.uniform(1000, 100000) / TASA_CAMBIO  # Saldo inicial aleatorio
        self.users = {
            'alex': {'password': '1234', 'balance': random.uniform(1000, 10000) / TASA_CAMBIO},
            'diego': {'password': '2345', 'balance': random.uniform(1000, 10000) / TASA_CAMBIO},
            'ander': {'password': '3456', 'balance': random.uniform(1000, 10000) / TASA_CAMBIO},
            'manuel': {'password': '4567', 'balance': random.uniform(1000, 10000) / TASA_CAMBIO}
        }

        self.admin_password = "2018"  # Contraseña del administrador
        self.totalCaja = 0
        self.estado = False
        self.username = ''
        self.admin_entered_password = ''  # Almacena la contraseña ingresada por el admin

        self.bills = {
            5: 0,
            10: 0,
            20: 0,
            50: 0
        }

        self.insert_initial_users()
        self.choose_user_type_screen()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            username VARCHAR(255) PRIMARY KEY,
                            password VARCHAR(255),
                            balance FLOAT
                          )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS bills (
                            denomination INT PRIMARY KEY,
                            count INT
                          )''')
        self.conn.commit()

    def insert_initial_users(self):
        cursor = self.conn.cursor()
        for username, data in self.users.items():
            cursor.execute("INSERT INTO users (username, password, balance) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE balance=%s",
                           (username, data['password'], data['balance'], data['balance']))
        self.conn.commit()

    def choose_user_type_screen(self):
        self.clear_screen()

        tk.Label(self.canvas, text="Seleccione el tipo de usuario:", bg='white',font=('Arial', 18)).place(relx=0.5, rely=0.1, anchor="center")

        tk.Button(self.canvas, text="Cliente", command=self.client_login_screen, bg='lightblue', fg='black', font=('Arial', 16)).place(relx=0.5, rely=0.3, anchor="center")
        tk.Button(self.canvas, text="Administrador", command=self.admin_login, bg='lightgreen', fg='black', font=('Arial', 16)).place(relx=0.5, rely=0.4, anchor="center")

    def client_login_screen(self):
        self.clear_screen()

        tk.Label(self.canvas, text='Ingrese su nombre de usuario', bg='white',font=('Arial', 12)).place(relx=0.5, rely=0.3, anchor="center")
        username_entry = tk.Entry(self.canvas)
        username_entry.place(relx=0.5, rely=0.4, anchor="center")
        
        tk.Label(self.canvas, text='Ingrese su contraseña', bg='white',font=('Arial', 12)).place(relx=0.5, rely=0.5, anchor="center")
        password_entry = tk.Entry(self.canvas, show='*')
        password_entry.place(relx=0.5, rely=0.6, anchor="center")

        tk.Button(self.canvas, text='Ingresar', command=lambda: self.client_login(username_entry.get(), password_entry.get()), bg='lightblue', fg='black', font=('Arial', 16)).place(relx=0.5, rely=0.7, anchor="center")

    def client_login(self, username, password):
        self.username = username.lower()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (self.username,))
        user = cursor.fetchone()
        if user:
            if password == user[1]:  # user[1] is the password
                messagebox.showinfo("Acceso", "Acceso Habilitado")
                self.balance = user[2]  # user[2] is the balance
                self.main_screen()
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")

    def admin_login(self):
        self.get_admin_password()

    def get_admin_password(self):
        self.pwd_window = tk.Toplevel(self.root)
        self.pwd_window.title("Sistema de seguridad")
        self.pwd_window.geometry("300x150")
        self.pwd_window.resizable(0, 0)

        tk.Label(self.pwd_window, text='Ingrese la contraseña de administrador',font=('Arial', 18)).pack(pady=10)
        self.pwdbox = tk.Entry(self.pwd_window, show='*')
        self.pwdbox.pack(pady=5)
        tk.Button(self.pwd_window, text='Ingresar', command=self.on_password_enter, bg='lightblue', fg='black', font=('Arial', 12)).pack(pady=10)

    def on_password_enter(self):
        self.admin_entered_password = self.pwdbox.get()
        self.pwd_window.destroy()
        if self.admin_entered_password == self.admin_password:
            self.admin_screen()
        else:
            messagebox.showerror("Error", "Clave incorrecta")
            self.choose_user_type_screen()

    def admin_screen(self):
        self.clear_screen()

        tk.Label(self.canvas, text="Acceso de Administrador", bg='white',font=('Arial', 18)).place(relx=0.5, rely=0.1, anchor="center")
        tk.Button(self.canvas, text="Abrir Cajero", command=self.open_atm_screen, bg='lightblue', fg='black', font=('Arial', 16)).place(relx=0.5, rely=0.3, anchor="center")
        tk.Button(self.canvas, text="Cerrar Cajero", command=self.close_atm, bg='lightgreen', fg='black', font=('Arial', 16)).place(relx=0.5, rely=0.4, anchor="center")
        tk.Button(self.canvas, text="Volver", command=self.choose_user_type_screen, bg='lightgray', fg='black', font=('Arial', 16)).place(relx=0.5, rely=0.6, anchor="center")

    def open_atm_screen(self):
        self.clear_screen()

        tk.Label(self.canvas, text="Ingrese la cantidad de billetes", bg='white',font=('Arial', 18)).place(relx=0.5, rely=0.1, anchor="center")

        self.bill_entries = {}
        for bill in [5, 10, 20, 50]:
            tk.Label(self.canvas, text=f"Billetes de {bill}:", bg='white').place(relx=0.3, rely=0.2 + bill * 0.05, anchor="center")
            self.bill_entries[bill] = tk.Entry(self.canvas)
            self.bill_entries[bill].place(relx=0.5, rely=0.2 + bill * 0.05, anchor="center")

        tk.Button(self.canvas, text="Añadir Billetes", command=self.add_bills, bg='lightblue', fg='black', font=('Arial', 16)).place(relx=0.5, rely=0.8, anchor="center")
        tk.Button(self.canvas, text="Abrir Cajero", command=self.open_atm, bg='lightblue', fg='black', font=('Arial', 16)).place(relx=0.9, rely=0.1, anchor="center")
        tk.Button(self.canvas, text="Volver", command=self.admin_screen, bg='lightgray', fg='black', font=('Arial', 16)).place(relx=0.1, rely=0.1, anchor="center")

    def add_bills(self):
        cursor = self.conn.cursor()
        for bill in self.bill_entries:
            try:
                count = int(self.bill_entries[bill].get())
                if count < 0:
                    raise ValueError("Cantidad negativa")
                cursor.execute("INSERT INTO bills (denomination, count) VALUES (%s, %s) ON DUPLICATE KEY UPDATE count=count+%s", (bill, count, count))
                self.bills[bill] += count
            except ValueError:
                messagebox.showerror("Error", f"Ingrese una cantidad válida para los billetes de {bill}")

        self.conn.commit()
        self.totalCaja = sum(denomination * count for denomination, count in self.bills.items())
        messagebox.showinfo("Éxito", "Billetes añadidos correctamente")

    def open_atm(self):
        self.estado = True
        messagebox.showinfo("Éxito", "Cajero abierto")

    def close_atm(self):
        self.estado = False
        messagebox.showinfo("Éxito", "Cajero cerrado")

    def main_screen(self):
        self.clear_screen()

        tk.Label(self.canvas, text=f"Bienvenido {self.username}", bg='white',font=('Arial', 22)).place(relx=0.5, rely=0.1, anchor="center", )
        tk.Button(self.canvas, text="Consultar Saldo", command=self.check_balance, bg='lightblue', fg='black', font=('Arial', 16)).place(relx=0.5, rely=0.3, anchor="center")
        tk.Button(self.canvas, text="Retirar Dinero", command=self.withdraw_screen, bg='lightgreen', fg='black', font=('Arial', 16)).place(relx=0.5, rely=0.4, anchor="center")
        tk.Button(self.canvas, text="Cerrar Sesión", command=self.choose_user_type_screen, bg='lightgray', fg='black', font=('Arial', 16)).place(relx=0.5, rely=0.6, anchor="center")

    def check_balance(self):
        messagebox.showinfo("Saldo", f"Su saldo es: {self.balance * TASA_CAMBIO:.2f} colones")

    def withdraw_screen(self):
        self.clear_screen()

        tk.Label(self.canvas, text="Ingrese la cantidad a retirar:", bg='white').place(relx=0.5, rely=0.4, anchor="center")
        self.amount_entry = tk.Entry(self.canvas)
        self.amount_entry.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Button(self.canvas, text="Retirar", command=self.withdraw, bg='lightblue', fg='black', font=('Arial', 16)).place(relx=0.5, rely=0.6, anchor="center")
        tk.Button(self.canvas, text="Volver", command=self.main_screen, bg='lightgray', fg='black', font=('Arial', 16)).place(relx=0.5, rely=0.7, anchor="center")

    def withdraw(self):
        amount = float(self.amount_entry.get())
        if amount <= self.balance * TASA_CAMBIO:
            if self.can_dispense_amount(amount):
                self.balance -= amount / TASA_CAMBIO
                self.dispense_cash(amount)
                cursor = self.conn.cursor()
                cursor.execute("UPDATE users SET balance=%s WHERE username=%s", (self.balance, self.username))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Retiro exitoso")
                self.main_screen()
            else:
                messagebox.showerror("Error", "No hay suficientes billetes para dispensar esta cantidad")
        else:
            messagebox.showerror("Error", "Fondos insuficientes")

    def can_dispense_amount(self, amount):
        # Implement logic to check if the ATM can dispense the requested amount with available bills
        return True

    def dispense_cash(self, amount):
        # Implement logic to dispense the cash from the ATM
        pass

    def clear_screen(self):
        for widget in self.canvas.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    atm = ATM(root)
    root.mainloop()
