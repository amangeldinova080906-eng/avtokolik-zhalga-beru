import pyodbc
import hashlib
import hmac
import getpass

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


# Құпиясөзді тексеру
def check_password(password, stored_hash):
    try:
        salt_hex, hash_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        correct_hash = bytes.fromhex(hash_hex)

        entered_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            600000
        )

        return hmac.compare_digest(entered_hash, correct_hash)
    except (ValueError, AttributeError):
        return False


# Жүйеге кіру
def login():
    print("\n===== ЖҮЙЕГЕ КІРУ =====")

    for attempt in range(3):
        username = input("Логин: ")
        password = getpass.getpass("Құпиясөз: ")

        cursor.execute("""
            SELECT aty_zhoni, password_hash, rol, filial_id
            FROM Qyzmetkerler
            WHERE login = ?
        """, username)

        user = cursor.fetchone()

        if user and check_password(password, user[1]):
            print(f"\nҚош келдіңіз, {user[0]}!")
            print(f"Рөліңіз: {user[2]}")

            return {
                "name": user[0],
                "role": user[2],
                "filial_id": user[3]
            }

        print("Логин немесе құпиясөз қате.")

    print("Кіру әрекеттері аяқталды.")
    return None


# Рұқсатты тексеру
def allowed(user, roles):
    if user["role"] not in roles:
        print("Бұл әрекетті орындауға рұқсатыңыз жоқ.")
        return False
    return True


# Автокөліктерді көрсету
def show_cars(user):
    if user["role"] in ("Директор"):
        cursor.execute("""
            SELECT a.avtokolik_id, a.marka, a.model,
                   a.memlekettik_nomer, a.zhyl,
                   a.bagasy_kunine, a.kui, f.qala
            FROM Avtokolikter a
            JOIN Filialdar f ON a.filial_id = f.filial_id
            ORDER BY a.avtokolik_id
        """)
    else:
        cursor.execute("""
            SELECT a.avtokolik_id, a.marka, a.model,
                   a.memlekettik_nomer, a.zhyl,
                   a.bagasy_kunine, a.kui, f.qala
            FROM Avtokolikter a
            JOIN Filialdar f ON a.filial_id = f.filial_id
            WHERE a.filial_id = ?
            ORDER BY a.avtokolik_id
        """, user["filial_id"])

    cars = cursor.fetchall()

    print("\n===== АВТОКӨЛІКТЕР =====")

    if not cars:
        print("Автокөліктер табылмады.")

    for car in cars:
        print(
            f"ID: {car[0]} | {car[1]} {car[2]} | "
            f"Нөмірі: {car[3]} | Жылы: {car[4]} | "
            f"Бағасы: {car[5]} тг | "
            f"Күйі: {car[6]} | Филиал: {car[7]}"
        )


# Филиалдарды көрсету
def show_filials():
    cursor.execute("""
        SELECT filial_id, qala
        FROM Filialdar
        ORDER BY filial_id
    """)

    print("\n===== ФИЛИАЛДАР =====")

    for filial in cursor.fetchall():
        print(f"{filial[0]} - {filial[1]}")


# Автокөлік қосу
def add_car(user):
    if not allowed(user, ("Директор",)):
        return

    print("\n===== АВТОКӨЛІК ҚОСУ =====")

    marka = input("Марка: ")
    model = input("Модель: ")
    nomer = input("Мемлекеттік нөмір: ")
    zhyl = int(input("Жылы: "))
    baga = float(input("Күндік бағасы: "))

    show_filials()
    filial = int(input("Филиал ID: "))

    cursor.execute(
        "SELECT 1 FROM Filialdar WHERE filial_id = ?",
        filial
    )

    if cursor.fetchone() is None:
        print("Мұндай филиал жоқ.")
        return

    cursor.execute("""
        INSERT INTO Avtokolikter
        (marka, model, memlekettik_nomer,
         zhyl, bagasy_kunine, kui, filial_id)
        VALUES (?, ?, ?, ?, ?, N'Бос', ?)
    """, marka, model, nomer, zhyl, baga, filial)

    conn.commit()
    print("Автокөлік қосылды!")


# Автокөлік бағасын өзгерту
def update_car(user):
    if not allowed(user, ("Директор",)):
        return

    car_id = int(input("Автокөлік ID: "))
    price = float(input("Жаңа бағасы: "))

    cursor.execute("""
        UPDATE Avtokolikter
        SET bagasy_kunine = ?
        WHERE avtokolik_id = ?
    """, price, car_id)

    changed = cursor.rowcount
    conn.commit()

    print("Баға өзгертілді!" if changed else "Автокөлік табылмады.")


# Автокөлікті өшіру
def delete_car(user):
    if not allowed(user, ("Директор",)):
        return

    car_id = int(input("Өшірілетін автокөлік ID: "))

    try:
        cursor.execute("""
            DELETE FROM Avtokolikter
            WHERE avtokolik_id = ?
        """, car_id)

        changed = cursor.rowcount
        conn.commit()

        print("Автокөлік өшірілді!" if changed else "Автокөлік табылмады.")
    except pyodbc.IntegrityError:
        conn.rollback()
        print("Автокөлікке байланысты брондау немесе жалға алу жазбасы бар.")


# Брондауларды көрсету
def show_bookings(user):
    if not allowed(user, ("Директор", "Менеджер")):
        return

    sql = """
        SELECT b.bron_id, k.aty_zhoni,
               a.marka, a.model, f.qala,
               b.alu_kuni, b.kui
        FROM Brondau b
        JOIN Klientter k ON b.klient_id = k.klient_id
        JOIN Avtokolikter a ON b.avtokolik_id = a.avtokolik_id
        JOIN Filialdar f ON b.filial_id = f.filial_id
    """

    if user["role"] == "Менеджер":
        sql += " WHERE b.filial_id = ?"
        cursor.execute(sql, user["filial_id"])
    else:
        cursor.execute(sql)

    print("\n===== БРОНДАУЛАР =====")

    bookings = cursor.fetchall()

    if not bookings:
        print("Брондаулар табылмады.")

    for b in bookings:
        print(
            f"Бронь ID: {b[0]} | Клиент: {b[1]} | "
            f"{b[2]} {b[3]} | Қала: {b[4]} | "
            f"Күні: {b[5]} | Күйі: {b[6]}"
        )


# Брондауды растау
def confirm_booking(user):
    if not allowed(user, ("Директор", "Менеджер")):
        return

    show_bookings(user)

    bron_id = int(input("\nРасталатын бронь ID: "))

    sql = """
        SELECT b.avtokolik_id, b.kui
        FROM Brondau b
        WHERE b.bron_id = ?
    """
    params = [bron_id]

    if user["role"] == "Менеджер":
        sql += " AND b.filial_id = ?"
        params.append(user["filial_id"])

    cursor.execute(sql, *params)
    booking = cursor.fetchone()

    if booking is None:
        print("Брондау табылмады немесе рұқсат жоқ.")
        return

    if booking[1] != "Брондалды":
        print("Бұл брондау растауға дайын емес.")
        return

    cursor.execute("""
        UPDATE Brondau
        SET kui = N'Расталды'
        WHERE bron_id = ? AND kui = N'Брондалды'
    """, bron_id)

    conn.commit()
    print("Брондау расталды!")


# Автокөлікті басқа қалаға қайтару
def return_car(user):
    if not allowed(user, ("Директор", "Сотрудник")):
        return

    show_cars(user)

    car_id = int(input("\nҚайтарылатын автокөлік ID: "))

    cursor.execute("""
        SELECT filial_id
        FROM Avtokolikter
        WHERE avtokolik_id = ?
    """, car_id)

    car = cursor.fetchone()

    if car is None:
        print("Автокөлік табылмады.")
        return

    if user["role"] == "Сотрудник":
        if car[0] != user["filial_id"]:
            print("Бұл автокөлік сіздің филиалда емес.")
            return

    show_filials()
    filial_id = int(input("Жаңа филиал ID: "))

    cursor.execute(
        "SELECT qala FROM Filialdar WHERE filial_id = ?",
        filial_id
    )

    filial = cursor.fetchone()

    if filial is None:
        print("Филиал табылмады.")
        return

    cursor.execute("""
        UPDATE Avtokolikter
        SET filial_id = ?, kui = N'Бос'
        WHERE avtokolik_id = ?
    """, filial_id, car_id)

    conn.commit()

    print(f"Автокөлік {filial[0]} қаласына қайтарылды!")


# Жалға алу тарихы
def rental_history(user):
    if not allowed(user, ("Директор", "Сотрудник", "Проверяющий")):
        return

    sql = """
        SELECT z.zhalga_id, k.aty_zhoni,
               a.marka, a.model,
               f1.qala, f2.qala, z.kui
        FROM ZhalgaAlu z
        JOIN Klientter k ON z.klient_id = k.klient_id
        JOIN Avtokolikter a ON z.avtokolik_id = a.avtokolik_id
        JOIN Filialdar f1 ON z.alu_filial_id = f1.filial_id
        LEFT JOIN Filialdar f2 ON z.qaitaru_filial_id = f2.filial_id
    """

    if user["role"] == "Сотрудник":
        sql += """
            WHERE z.alu_filial_id = ?
               OR z.qaitaru_filial_id = ?
        """
        cursor.execute(
            sql, user["filial_id"], user["filial_id"]
        )
    else:
        cursor.execute(sql)

    print("\n===== ЖАЛҒА АЛУ ТАРИХЫ =====")

    for item in cursor.fetchall():
        print(
            f"ID: {item[0]} | Клиент: {item[1]} | "
            f"{item[2]} {item[3]} | "
            f"Алған қала: {item[4]} | "
            f"Қайтарған қала: {item[5]} | "
            f"Күйі: {item[6]}"
        )


# Әр рөлге арналған мәзір
def main_menu(user):
    actions = {
        "Автокөліктерді көрсету": show_cars
    }

    if user["role"] == "Директор":
        actions.update({
            "Автокөлік қосу": add_car,
            "Бағасын өзгерту": update_car,
            "Автокөлікті өшіру": delete_car,
            "Брондауларды көрсету": show_bookings,
            "Брондауды растау": confirm_booking,
            "Басқа қалаға қайтару": return_car,
            "Жалға алу тарихы": rental_history
        })

    elif user["role"] == "Менеджер":
        actions.update({
            "Брондауларды көрсету": show_bookings,
            "Брондауды растау": confirm_booking
        })

    elif user["role"] == "Сотрудник":
        actions.update({
            "Басқа қалаға қайтару": return_car,
            "Жалға алу тарихы": rental_history
        })

    elif user["role"] == "Проверяющий":
        actions.update({
            "Брондауларды көрсету": show_bookings,
            "Жалға алу тарихы": rental_history
        })

    names = list(actions.keys())

    while True:
        print("\n===== АВТОКӨЛІКТІ ЖАЛҒА БЕРУ ЖҮЙЕСІ =====")
        print(f"Пайдаланушы: {user['name']}")
        print(f"Рөлі: {user['role']}")

        for number, name in enumerate(names, 1):
            print(f"{number} - {name}")

        print(f"{len(names) + 1} - Шығу")

        choice = input("\nТаңдаңыз: ")

        if not choice.isdigit():
            print("Қате таңдау!")
            continue

        number = int(choice)

        if number == len(names) + 1:
            print("Жүйеден шығу.")
            break

        if 1 <= number <= len(names):
            action = actions[names[number - 1]]

            try:
                action(user)
            except ValueError:
                print("Сан дұрыс енгізілмеді.")
            except pyodbc.Error as error:
                conn.rollback()
                print("SQL қатесі:", error)
        else:
            print("Қате таңдау!")


# Бағдарламаны іске қосу
try:
    user = login()

    if user:
        main_menu(user)
finally:
    conn.close()