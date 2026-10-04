/* =========================================================
   АВТОК?ЛІКТІ ЖАЛ?А БЕРУ А?ПАРАТТЫ? Ж?ЙЕСІ
   Деректер базасы: AvtokolikZhalgaBeru
   ========================================================= */

-- Деректер базасын ??ру
CREATE DATABASE AvtokolikZhalgaBeru;
GO

USE AvtokolikZhalgaBeru;
GO


/* =========================================================
   1. ФИЛИАЛДАР
   ========================================================= */

CREATE TABLE Filialdar (
    filial_id INT PRIMARY KEY IDENTITY(1,1),
    qala NVARCHAR(50) NOT NULL,
    mekenzhai NVARCHAR(200) NOT NULL
);
GO

INSERT INTO Filialdar (qala, mekenzhai)
VALUES
(N'Алматы', N'Абай да??ылы, 50'),
(N'Семей', N'?абанбай батыр к?шесі, 25');
GO


/* =========================================================
   2. АВТОК?ЛІКТЕР
   ========================================================= */

CREATE TABLE Avtokolikter (
    avtokolik_id INT PRIMARY KEY IDENTITY(1,1),
    marka NVARCHAR(50) NOT NULL,
    model NVARCHAR(50) NOT NULL,
    memlekettik_nomer NVARCHAR(20) NOT NULL UNIQUE,
    zhyl INT,
    bagasy_kunine DECIMAL(10,2),
    kui NVARCHAR(30) NOT NULL,
    filial_id INT NOT NULL,

    CONSTRAINT FK_Avtokolikter_Filialdar
        FOREIGN KEY (filial_id)
        REFERENCES Filialdar(filial_id)
);
GO

INSERT INTO Avtokolikter
(marka, model, memlekettik_nomer, zhyl, bagasy_kunine, kui, filial_id)
VALUES
(N'Toyota', N'Camry', N'777AAA02', 2023, 25000, N'Бос', 1),
(N'Hyundai', N'Elantra', N'555BBB02', 2022, 20000, N'Бос', 1),
(N'Kia', N'K5', N'111CCC18', 2023, 23000, N'Бос', 2),
(N'Chevrolet', N'Cobalt', N'222DDD18', 2022, 15000, N'Бос', 2);
GO


/* =========================================================
   3. КЛИЕНТТЕР
   ========================================================= */

CREATE TABLE Klientter (
    klient_id INT PRIMARY KEY IDENTITY(1,1),
    aty_zhoni NVARCHAR(100) NOT NULL,
    telefon NVARCHAR(20) NOT NULL
);
GO

INSERT INTO Klientter (aty_zhoni, telefon)
VALUES
(N'Айдос Н?рлан?лы', N'+77011234567'),
(N'Аружан Серік?ызы', N'+77077654321');
GO


/* =========================================================
   4. ЖАЛ?А АЛУ
   ========================================================= */

CREATE TABLE ZhalgaAlu (
    zhalga_id INT PRIMARY KEY IDENTITY(1,1),
    klient_id INT NOT NULL,
    avtokolik_id INT NOT NULL,
    alu_filial_id INT NOT NULL,
    qaitaru_filial_id INT NULL,
    alu_kuni DATE NOT NULL,
    qaitaru_kuni DATE NULL,
    kui NVARCHAR(30) NOT NULL,

    CONSTRAINT FK_Zhalga_Klient
        FOREIGN KEY (klient_id)
        REFERENCES Klientter(klient_id),

    CONSTRAINT FK_Zhalga_Avtokolik
        FOREIGN KEY (avtokolik_id)
        REFERENCES Avtokolikter(avtokolik_id),

    CONSTRAINT FK_Zhalga_AluFilial
        FOREIGN KEY (alu_filial_id)
        REFERENCES Filialdar(filial_id),

    CONSTRAINT FK_Zhalga_QaitaruFilial
        FOREIGN KEY (qaitaru_filial_id)
        REFERENCES Filialdar(filial_id)
);
GO


/* =========================================================
   5. БРОНДАУ
   ========================================================= */

CREATE TABLE Brondau (
    bron_id INT PRIMARY KEY IDENTITY(1,1),
    klient_id INT NOT NULL,
    avtokolik_id INT NOT NULL,
    filial_id INT NOT NULL,
    bron_kuni DATE NOT NULL,
    alu_kuni DATE NOT NULL,
    kui NVARCHAR(30) NOT NULL,

    CONSTRAINT FK_Brondau_Klient
        FOREIGN KEY (klient_id)
        REFERENCES Klientter(klient_id),

    CONSTRAINT FK_Brondau_Avtokolik
        FOREIGN KEY (avtokolik_id)
        REFERENCES Avtokolikter(avtokolik_id),

    CONSTRAINT FK_Brondau_Filial
        FOREIGN KEY (filial_id)
        REFERENCES Filialdar(filial_id)
);
GO


/* =========================================================
   6. АВТОК?ЛІКТІ ЖАЛ?А АЛУ
   Toyota Camry Алматы филиалынан алынады
   ========================================================= */

INSERT INTO ZhalgaAlu
(
    klient_id,
    avtokolik_id,
    alu_filial_id,
    alu_kuni,
    kui
)
VALUES
(
    1,
    1,
    1,
    CAST(GETDATE() AS DATE),
    N'Жал?а берілді'
);
GO

UPDATE Avtokolikter
SET kui = N'Жал?а берілді'
WHERE avtokolik_id = 1;
GO


/* =========================================================
   7. БАС?А ?АЛАДА ?АЙТАРУ
   Toyota Camry Алматыдан алынып,
   Семей филиалына ?айтарылады
   ========================================================= */

UPDATE ZhalgaAlu
SET
    qaitaru_filial_id = 2,
    qaitaru_kuni = CAST(GETDATE() AS DATE),
    kui = N'Ая?талды'
WHERE zhalga_id = 1;
GO

-- Авток?лікті? орналас?ан жері Семей болып ?згереді
-- ж?не авток?лік ?айтадан бос болады

UPDATE Avtokolikter
SET
    filial_id = 2,
    kui = N'Бос'
WHERE avtokolik_id = 1;
GO


/* =========================================================
   8. АВТОК?ЛІКТІ БРОНДАУ
   Аружан Hyundai Elantra авток?лігін брондайды
   ========================================================= */

INSERT INTO Brondau
(
    klient_id,
    avtokolik_id,
    filial_id,
    bron_kuni,
    alu_kuni,
    kui
)
VALUES
(
    2,
    2,
    1,
    CAST(GETDATE() AS DATE),
    DATEADD(DAY, 2, CAST(GETDATE() AS DATE)),
    N'Брондалды'
);
GO

UPDATE Avtokolikter
SET kui = N'Брондалды'
WHERE avtokolik_id = 2;
GO


/* =========================================================
   9. АВТОК?ЛІКТЕРДІ? А?ЫМДА?Ы К?ЙІ
   ========================================================= */

SELECT
    a.avtokolik_id,
    a.marka,
    a.model,
    a.memlekettik_nomer,
    a.bagasy_kunine,
    a.kui,
    f.qala AS ornalasqan_qala
FROM Avtokolikter a
JOIN Filialdar f
    ON a.filial_id = f.filial_id;
GO


/* =========================================================
   10. ЖАЛ?А АЛУ ТАРИХЫ
   ========================================================= */

SELECT
    z.zhalga_id,
    k.aty_zhoni AS klient,
    a.marka,
    a.model,
    f1.qala AS algan_qala,
    f2.qala AS qaitargan_qala,
    z.alu_kuni,
    z.qaitaru_kuni,
    z.kui AS zhalga_kui
FROM ZhalgaAlu z
JOIN Klientter k
    ON z.klient_id = k.klient_id
JOIN Avtokolikter a
    ON z.avtokolik_id = a.avtokolik_id
JOIN Filialdar f1
    ON z.alu_filial_id = f1.filial_id
LEFT JOIN Filialdar f2
    ON z.qaitaru_filial_id = f2.filial_id;
GO


/* =========================================================
   11. БРОНДАУ ТІЗІМІ
   ========================================================= */

SELECT
    b.bron_id,
    k.aty_zhoni AS klient,
    a.marka,
    a.model,
    f.qala AS filial,
    b.bron_kuni,
    b.alu_kuni,
    b.kui AS bron_kui
FROM Brondau b
JOIN Klientter k
    ON b.klient_id = k.klient_id
JOIN Avtokolikter a
    ON b.avtokolik_id = a.avtokolik_id
JOIN Filialdar f
    ON b.filial_id = f.filial_id;
GO