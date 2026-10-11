import pyodbc
import hashlib
import os

server = r'Admin\SQLEXPRESS'
database = 'AvtokolikZhalgaBeru'

conn = pyodbc.connect(
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'Trusted_Connection=yes;'
    f'TrustServerCertificate=yes;'
)

cursor = conn.cursor()


def hash_password(password):
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        600000
    )
    return salt.hex() + ':' + password_hash.hex()


users = [
    ("Директор", "director", "Директор", None),
    ("Менеджер Алматы", "manager", "Менеджер", 1),
    ("Сотрудник Алматы", "employee", "Сотрудник", 1)
]

for name, login, role, filial_id in users:
    cursor.execute(
        "SELECT 1 FROM Qyzmetkerler WHERE login = ?",
        login
    )

    if cursor.fetchone():
        print(f"{login}: уже существует")
        continue

    password = input(f"Придумайте пароль для {login}: ")
    password_hash = hash_password(password)

    cursor.execute("""
        INSERT INTO Qyzmetkerler
        (aty_zhoni, login, password_hash, rol, filial_id)
        VALUES (?, ?, ?, ?, ?)
    """, name, login, password_hash, role, filial_id)

    print(f"{login}: добавлен")

conn.commit()
conn.close()

print("Создание сотрудников завершено.")