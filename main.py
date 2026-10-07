import pyodbc

server = r'Admin\SQLEXPRESS'
database = 'AvtokolikZhalgaBeru'

# SQL Server-ге қосылу
conn = pyodbc.connect(
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'Trusted_Connection=yes;'
    f'TrustServerCertificate=yes;'
)

cursor = conn.cursor()


# 1. Автокөліктерді көрсету
def show_cars():
    cursor.execute("""
        SELECT
            a.avtokolik_id,
            a.marka,
            a.model,
            a.memlekettik_nomer,
            a.zhyl,
            a.bagasy_kunine,
            a.kui,
            f.qala
        FROM Avtokolikter a
        JOIN Filialdar f
            ON a.filial_id = f.filial_id
        ORDER BY a.avtokolik_id
    """)

    cars = cursor.fetchall()

    print("\n===== АВТОКӨЛІКТЕР =====")

    if not cars:
        print("Автокөліктер табылмады.")
        return

    for car in cars:
        print(
            f"ID: {car[0]} | "
            f"{car[1]} {car[2]} | "
            f"Нөмірі: {car[3]} | "
            f"Жылы: {car[4]} | "
            f"Бағасы: {car[5]} тг | "
            f"Күйі: {car[6]} | "
            f"Филиал: {car[7]}"
        )


# Филиалдарды көрсету
def show_filials():
    cursor.execute("""
        SELECT filial_id, qala
        FROM Filialdar
        ORDER BY filial_id
    """)

    filials = cursor.fetchall()

    print("\n===== ФИЛИАЛДАР =====")

    for filial in filials:
        print(f"{filial[0]} - {filial[1]}")


# 2. Жаңа автокөлік қосу
def add_car():
    print("\n===== ЖАҢА АВТОКӨЛІК ҚОСУ =====")

    marka = input("Марка: ")
    model = input("Модель: ")
    nomer = input("Мемлекеттік нөмір: ")
    zhyl = int(input("Жылы: "))
    baga = float(input("Күніне бағасы: "))
    kui = input("Күйі (Бос/Брондалды): ")

    show_filials()

    filial = int(input("\nФилиал ID таңдаңыз: "))

    cursor.execute("""
        SELECT qala
        FROM Filialdar
        WHERE filial_id = ?
    """, filial)

    selected_filial = cursor.fetchone()

    if selected_filial is None:
        print("Мұндай филиал табылмады.")
        return

    cursor.execute("""
        INSERT INTO Avtokolikter
        (marka, model, memlekettik_nomer,
         zhyl, bagasy_kunine, kui, filial_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, marka, model, nomer, zhyl, baga, kui, filial)

    conn.commit()

    print(
        f"Автокөлік сәтті қосылды! "
        f"Филиал: {selected_filial[0]}"
    )


# 3. Автокөліктің бағасын өзгерту
def update_car():
    print("\n===== АВТОКӨЛІКТІ ӨЗГЕРТУ =====")

    car_id = int(input("Автокөлік ID: "))
    new_price = float(input("Жаңа күндік бағасы: "))

    cursor.execute("""
        UPDATE Avtokolikter
        SET bagasy_kunine = ?
        WHERE avtokolik_id = ?
    """, new_price, car_id)

    conn.commit()

    if cursor.rowcount > 0:
        print("Автокөлік бағасы өзгертілді!")
    else:
        print("Мұндай ID табылмады.")


# 4. Автокөлікті өшіру
def delete_car():
    print("\n===== АВТОКӨЛІКТІ ӨШІРУ =====")

    car_id = int(input("Өшірілетін автокөлік ID: "))

    cursor.execute("""
        DELETE FROM Avtokolikter
        WHERE avtokolik_id = ?
    """, car_id)

    conn.commit()

    if cursor.rowcount > 0:
        print("Автокөлік өшірілді!")
    else:
        print("Мұндай ID табылмады.")


# 5. Автокөлікті басқа қалаға қайтару
def return_car_other_city():
    print("\n===== АВТОКӨЛІКТІ БАСҚА ҚАЛАҒА ҚАЙТАРУ =====")

    show_cars()

    car_id = int(input("\nҚайтарылатын автокөлік ID: "))

    cursor.execute("""
        SELECT avtokolik_id
        FROM Avtokolikter
        WHERE avtokolik_id = ?
    """, car_id)

    car = cursor.fetchone()

    if car is None:
        print("Мұндай автокөлік табылмады.")
        return

    show_filials()

    new_filial = int(input("\nҚайтарылатын филиал ID: "))

    cursor.execute("""
        SELECT qala
        FROM Filialdar
        WHERE filial_id = ?
    """, new_filial)

    filial = cursor.fetchone()

    if filial is None:
        print("Мұндай филиал табылмады.")
        return

    cursor.execute("""
        UPDATE Avtokolikter
        SET filial_id = ?, kui = N'Бос'
        WHERE avtokolik_id = ?
    """, new_filial, car_id)

    conn.commit()

    print(
        f"Автокөлік {filial[0]} қаласындағы "
        f"филиалға қайтарылды!"
    )


# Негізгі мәзір
while True:

    print("\n================================")
    print("   АВТОКӨЛІКТІ ЖАЛҒА БЕРУ ЖҮЙЕСІ")
    print("================================")
    print("1 - Автокөліктерді көрсету")
    print("2 - Жаңа автокөлік қосу")
    print("3 - Автокөлік бағасын өзгерту")
    print("4 - Автокөлікті өшіру")
    print("5 - Автокөлікті басқа қалаға қайтару")
    print("6 - Шығу")

    choice = input("\nТаңдаңыз: ")

    if choice == "1":
        show_cars()

    elif choice == "2":
        add_car()

    elif choice == "3":
        update_car()

    elif choice == "4":
        delete_car()

    elif choice == "5":
        return_car_other_city()

    elif choice == "6":
        print("Бағдарлама аяқталды.")
        break

    else:
        print("Қате таңдау!")


conn.close()  