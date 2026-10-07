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
        SELECT avtokolik_id, marka, model, memlekettik_nomer,
               zhyl, bagasy_kunine, kui, filial_id
        FROM Avtokolikter
        ORDER BY avtokolik_id
    """)

    cars = cursor.fetchall()

    print("\n===== АВТОКӨЛІКТЕР =====")

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


# 2. Жаңа автокөлік қосу
def add_car():
    print("\n===== ЖАҢА АВТОКӨЛІК ҚОСУ =====")

    marka = input("Марка: ")
    model = input("Модель: ")
    nomer = input("Мемлекеттік нөмір: ")
    zhyl = int(input("Жылы: "))
    baga = float(input("Күніне бағасы: "))
    kui = input("Күйі (Бос/Брондалды): ")
    filial = int(input("Филиал ID (1 немесе 2): "))

    cursor.execute("""
        INSERT INTO Avtokolikter
        (marka, model, memlekettik_nomer,
         zhyl, bagasy_kunine, kui, filial_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, marka, model, nomer, zhyl, baga, kui, filial)

    conn.commit()

    print("✅ Автокөлік сәтті қосылды!")


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
        print("✅ Автокөлік бағасы өзгертілді!")
    else:
        print("❌ Мұндай ID табылмады.")


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
        print("✅ Автокөлік өшірілді!")
    else:
        print("❌ Мұндай ID табылмады.")


# Негізгі мәзір
while True:

    print("\n================================")
    print("   АВТОКӨЛІКТІ ЖАЛҒА БЕРУ ЖҮЙЕСІ")
    print("================================")
    print("1 - Автокөліктерді көрсету")
    print("2 - Жаңа автокөлік қосу")
    print("3 - Автокөлік бағасын өзгерту")
    print("4 - Автокөлікті өшіру")
    print("5 - Шығу")

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
        print("Бағдарлама аяқталды.")
        break

    else:
        print("❌ Қате таңдау!")

conn.close()