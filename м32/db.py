import sqlite3
import datetime
import random

DB_NAME = "furniture_sales.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Створення таблиць для меблевого магазину, якщо їх ще немає."""
    with get_connection() as conn:
        cur = conn.cursor()

   
        cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            material TEXT,
            color TEXT,
            width REAL,
            height REAL,
            depth REAL,
            base_price REAL NOT NULL CHECK(base_price >= 0),
            stock_qty INTEGER NOT NULL DEFAULT 0
        );
        """)

  
        cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            sale_price REAL NOT NULL CHECK(sale_price >= 0),
            discount_percent REAL NOT NULL DEFAULT 0,
            sale_date TEXT NOT NULL,
            customer_name TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
        """)

        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            user TEXT,
            action TEXT NOT NULL,
            details TEXT
        );
        """)

        conn.commit()




def add_log(action, details="", user="operator"):
    """Записати подію в журнал."""
    with get_connection() as conn:
        cur = conn.cursor()
        ts = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
        cur.execute("""
            INSERT INTO logs (ts, user, action, details)
            VALUES (?, ?, ?, ?)
        """, (ts, user, action, details))
        conn.commit()


def list_logs(limit=200):
    """Отримати останні події журналу."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT ts, user, action, details
            FROM logs
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        return cur.fetchall()




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



def add_product(name, category, material, color,
                width, height, depth, base_price, stock_qty):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO products
            (name, category, material, color,
             width, height, depth, base_price, stock_qty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, category, material, color,
              width, height, depth, base_price, stock_qty))
        conn.commit()
    add_log("add_product", f"{name} ({category}), stock={stock_qty}")


def update_product(product_id, name, category, material, color,
                   width, height, depth, base_price, stock_qty):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE products
            SET name = ?, category = ?, material = ?, color = ?,
                width = ?, height = ?, depth = ?, base_price = ?, stock_qty = ?
            WHERE id = ?
        """, (name, category, material, color,
              width, height, depth, base_price, stock_qty, product_id))
        conn.commit()
    add_log("update_product", f"id={product_id}, {name} ({category}), stock={stock_qty}")


def delete_product(product_id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sales WHERE product_id = ?", (product_id,))
        sales_count = cur.fetchone()[0]
        if sales_count > 0:
            raise ValueError("Неможливо видалити товар: існують пов'язані продажі.")
        cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
    add_log("delete_product", f"id={product_id}")


def list_products():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, category, material, color,
                   width, height, depth, base_price, stock_qty
            FROM products
            ORDER BY id
        """)
        return cur.fetchall()


def list_products_filtered(name_substr=None, category=None,
                           price_min=None, price_max=None):
    """Повертає товари з фільтрацією по назві / категорії / ціні."""
    with get_connection() as conn:
        cur = conn.cursor()
        sql = """
            SELECT id, name, category, material, color,
                   width, height, depth, base_price, stock_qty
            FROM products
            WHERE 1=1
        """
        params = []
        if name_substr:
            sql += " AND name LIKE ?"
            params.append(f"%{name_substr}%")
        if category:
            sql += " AND category LIKE ?"
            params.append(f"%{category}%")
        if price_min is not None:
            sql += " AND base_price >= ?"
            params.append(price_min)
        if price_max is not None:
            sql += " AND base_price <= ?"
            params.append(price_max)

        sql += " ORDER BY id"
        cur.execute(sql, params)
        return cur.fetchall()


def list_low_stock(threshold=5):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, category, stock_qty
            FROM products
            WHERE stock_qty <= ?
            ORDER BY stock_qty ASC
        """, (threshold,))
        return cur.fetchall()




def add_sale(product_id, quantity, sale_price=None,
             customer_name=None, discount_percent=0.0):
    """Зареєструвати продаж із врахуванням знижки."""
    with get_connection() as conn:
        cur = conn.cursor()

        # Базова ціна
        if sale_price is None:
            cur.execute("SELECT base_price FROM products WHERE id = ?",
                        (product_id,))
            row = cur.fetchone()
            if row is None:
                raise ValueError("Товар з таким ID не знайдено.")
            base_price = row[0]
        else:
            base_price = sale_price

        # Перевірка залишку
        cur.execute("SELECT stock_qty, name FROM products WHERE id = ?",
                    (product_id,))
        row = cur.fetchone()
        if row is None:
            raise ValueError("Товар з таким ID не знайдено.")
        stock_qty, prod_name = row
        if stock_qty < quantity:
            raise ValueError(
                f"Недостатньо товару на складі. Доступно: {stock_qty}, потрібно: {quantity}"
            )

        # Розрахунок кінцевої ціни зі знижкою
        disc = float(discount_percent or 0)
        final_price = base_price * (1 - disc / 100)

        new_qty = stock_qty - quantity
        cur.execute("UPDATE products SET stock_qty = ? WHERE id = ?",
                    (new_qty, product_id))

        sale_date = datetime.date.today().isoformat()
        cur.execute("""
            INSERT INTO sales (product_id, quantity, sale_price,
                               discount_percent, sale_date, customer_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_id, quantity, final_price,
              disc, sale_date, customer_name))

        conn.commit()

    add_log(
        "add_sale",
        f"product_id={product_id}, name={prod_name}, qty={quantity}, "
        f"price={final_price:.2f}, discount={disc:.1f}%, customer={customer_name}"
    )


def list_sales(limit=None):
    with get_connection() as conn:
        cur = conn.cursor()
        sql = """
        SELECT s.id,
               s.sale_date,
               p.name,
               p.category,
               s.quantity,
               s.sale_price,
               s.discount_percent,
               (s.quantity * s.sale_price) AS total,
               s.customer_name
        FROM sales s
        JOIN products p ON p.id = s.product_id
        ORDER BY s.sale_date DESC, s.id DESC
        """
        if limit:
            sql += " LIMIT ?"
            cur.execute(sql, (limit,))
        else:
            cur.execute(sql)
        return cur.fetchall()


def list_sales_filtered(name_substr=None, date_from=None,
                        date_to=None, customer_substr=None, limit=None):
    """Продажі з фільтрами: назва товару, діапазон дат, покупець."""
    with get_connection() as conn:
        cur = conn.cursor()
        sql = """
        SELECT s.id,
               s.sale_date,
               p.name,
               p.category,
               s.quantity,
               s.sale_price,
               s.discount_percent,
               (s.quantity * s.sale_price) AS total,
               s.customer_name
        FROM sales s
        JOIN products p ON p.id = s.product_id
        WHERE 1=1
        """
        params = []

        if name_substr:
            sql += " AND p.name LIKE ?"
            params.append(f"%{name_substr}%")
        if customer_substr:
            sql += " AND s.customer_name LIKE ?"
            params.append(f"%{customer_substr}%")
        if date_from:
            sql += " AND s.sale_date >= ?"
            params.append(date_from)
        if date_to:
            sql += " AND s.sale_date <= ?"
            params.append(date_to)

        sql += " ORDER BY s.sale_date DESC, s.id DESC"
        if limit:
            sql += " LIMIT ?"
            params.append(limit)

        cur.execute(sql, params)
        return cur.fetchall()


def report_total_by_day():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
        SELECT sale_date,
               SUM(quantity * sale_price) AS total
        FROM sales
        GROUP BY sale_date
        ORDER BY sale_date DESC
        """)
        return cur.fetchall()
