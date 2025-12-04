# seed_data.py
import random

from db import get_connection, add_log


def seed_test_data():
    """
    Заповнити БД тестовими товарами (близько 50 позицій меблів),
    якщо таблиця products порожня.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM products")
        count = cur.fetchone()[0]
        if count > 0:
            # Уже є дані – нічого не робимо
            return

        categories = [
            ("Шафа купе", "Шафа"),
            ("Шафа кутова", "Шафа"),
            ("Стіл письмовий", "Стіл"),
            ("Стіл обідній", "Стіл"),
            ("Стіл журнальний", "Стіл"),
            ("Стілець кухонний", "Стілець"),
            ("Стілець офісний", "Стілець"),
            ("Комод вузький", "Комод"),
            ("Комод широкий", "Комод"),
            ("Диван кутовий", "Диван"),
            ("Диван розкладний", "Диван"),
            ("Крісло м'яке", "Крісло"),
            ("Крісло офісне", "Крісло"),
            ("Ліжко односпальне", "Ліжко"),
            ("Ліжко двоспальне", "Ліжко"),
            ("Тумба приліжкова", "Тумба"),
            ("Тумба під ТВ", "Тумба"),
            ("Полиці настінні", "Полиці"),
            ("Кухонний гарнітур малий", "Кухня"),
            ("Кухонний гарнітур великий", "Кухня"),
        ]
        materials = ["ДСП", "Масив", "МДФ+шпон", "Метал+тканина"]
        colors = ["білий", "дуб сонома", "горіх", "сірий", "чорний"]

        random.seed(1)

        products_data = []
        for i in range(50):
            base_name, cat = categories[i % len(categories)]
            variant = i // len(categories) + 1
            name = f"{base_name} #{variant}"
            material = random.choice(materials)
            color = random.choice(colors)
            width = random.choice([60, 80, 100, 120, 140, 160, 180, 200])
            height = random.choice([40, 50, 75, 90, 200])
            depth = random.choice([35, 40, 45, 60])
            base_price = random.choice([2500, 3200, 4500, 5200, 6300, 7800, 9100])
            stock_qty = random.randint(0, 20)
            products_data.append(
                (name, cat, material, color, width, height, depth, base_price, stock_qty)
            )

        cur.executemany("""
            INSERT INTO products
            (name, category, material, color,
             width, height, depth, base_price, stock_qty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, products_data)

        conn.commit()

    add_log("seed_test_data", "Заповнення БД ~50 тестовими товарами")
