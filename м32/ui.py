import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv

from db import (
    list_products,
    list_products_filtered,
    list_sales,
    list_sales_filtered,
    report_total_by_day,
    add_product,
    add_sale,
    update_product,
    delete_product,
    list_logs,
)
from seed_data import seed_test_data

class FurnitureApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Автоматизована система обліку продажу меблів")
        self.geometry("1200x650")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.products_frame = ttk.Frame(self.notebook)
        self.sales_frame = ttk.Frame(self.notebook)
        self.reports_frame = ttk.Frame(self.notebook)
        self.logs_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.products_frame, text="Товари")
        self.notebook.add(self.sales_frame, text="Продажі")
        self.notebook.add(self.reports_frame, text="Звіти")
        self.notebook.add(self.logs_frame, text="Журнал")

        self.selected_product_id = None

        self.create_products_tab()
        self.create_sales_tab()
        self.create_reports_tab()
        self.create_logs_tab()

        self.refresh_products()
        self.refresh_sales()
        self.refresh_reports()
        self.refresh_logs()


    def create_products_tab(self):
        form_frame = ttk.LabelFrame(self.products_frame, text="Додати / редагувати меблевий товар")
        form_frame.pack(side="top", fill="x", padx=10, pady=10)

        labels = [
            "Назва", "Категорія", "Матеріал", "Колір",
            "Ширина (см)", "Висота (см)", "Глибина (см)",
            "Базова ціна (грн)", "Кількість на складі"
        ]
        self.product_entries = {}

        for i, label in enumerate(labels):
            ttk.Label(form_frame, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=2)
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=2)
            self.product_entries[label] = entry

        add_btn = ttk.Button(form_frame, text="Додати як новий", command=self.on_add_product)
        add_btn.grid(row=len(labels), column=0, pady=10, padx=5, sticky="ew")

        update_btn = ttk.Button(form_frame, text="Оновити вибраний", command=self.on_update_product)
        update_btn.grid(row=len(labels), column=1, pady=10, padx=5, sticky="ew")

        delete_btn = ttk.Button(form_frame, text="Видалити вибраний", command=self.on_delete_product)
        delete_btn.grid(row=len(labels) + 1, column=0, columnspan=2, pady=2, padx=5, sticky="ew")

        seed_btn = ttk.Button(form_frame, text="Заповнити тестовими даними (50 товарів)", command=self.on_seed_data)
        seed_btn.grid(row=len(labels) + 2, column=0, columnspan=2, pady=2, padx=5, sticky="ew")

        # Панель фільтрів
        filter_frame = ttk.LabelFrame(self.products_frame, text="Фільтр товарів")
        filter_frame.pack(side="top", fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Назва містить:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.filter_name_entry = ttk.Entry(filter_frame, width=20)
        self.filter_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(filter_frame, text="Категорія містить:").grid(row=0, column=2, padx=5, pady=2, sticky="e")
        self.filter_category_entry = ttk.Entry(filter_frame, width=20)
        self.filter_category_entry.grid(row=0, column=3, padx=5, pady=2, sticky="w")

        ttk.Label(filter_frame, text="Ціна від:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.filter_price_min_entry = ttk.Entry(filter_frame, width=10)
        self.filter_price_min_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(filter_frame, text="до:").grid(row=1, column=2, padx=5, pady=2, sticky="e")
        self.filter_price_max_entry = ttk.Entry(filter_frame, width=10)
        self.filter_price_max_entry.grid(row=1, column=3, padx=5, pady=2, sticky="w")

        filter_btn = ttk.Button(filter_frame, text="Застосувати фільтр", command=self.refresh_products)
        filter_btn.grid(row=0, column=4, padx=5, pady=2)

        reset_btn = ttk.Button(filter_frame, text="Скинути", command=self.reset_product_filters)
        reset_btn.grid(row=1, column=4, padx=5, pady=2)

        # Таблиця товарів
        list_frame = ttk.LabelFrame(self.products_frame, text="Каталог меблів")
        list_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "name", "category", "material", "color",
                   "size", "price", "stock")

        self.products_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=10
        )
        self.products_tree.pack(side="left", fill="both", expand=True)

        headings = {
            "id": "ID",
            "name": "Назва",
            "category": "Категорія",
            "material": "Матеріал",
            "color": "Колір",
            "size": "Розміри (ШxВxГ)",
            "price": "Ціна, грн",
            "stock": "Залишок"
        }
        for col, text in headings.items():
            self.products_tree.heading(col, text=text)
            self.products_tree.column(col, width=110 if col != "name" else 180, anchor="center")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.products_tree.bind("<<TreeviewSelect>>", self.on_product_select)

    def on_seed_data(self):
        seed_test_data()
        messagebox.showinfo("Готово", "Базу заповнено тестовими меблями (якщо вона була порожня).")
        self.refresh_products()
        self.refresh_sales()
        self.refresh_reports()
        self.refresh_logs()

    def reset_product_filters(self):
        self.filter_name_entry.delete(0, tk.END)
        self.filter_category_entry.delete(0, tk.END)
        self.filter_price_min_entry.delete(0, tk.END)
        self.filter_price_max_entry.delete(0, tk.END)
        self.refresh_products()

    def on_product_select(self, event):
        sel = self.products_tree.selection()
        if not sel:
            self.selected_product_id = None
            return
        item = self.products_tree.item(sel[0])
        pid, name, category, material, color, size_str, price_str, stock = item["values"]
        self.selected_product_id = int(pid)

        self.product_entries["Назва"].delete(0, tk.END)
        self.product_entries["Назва"].insert(0, name)

        self.product_entries["Категорія"].delete(0, tk.END)
        self.product_entries["Категорія"].insert(0, category)

        self.product_entries["Матеріал"].delete(0, tk.END)
        if material != "-":
            self.product_entries["Матеріал"].insert(0, material)

        self.product_entries["Колір"].delete(0, tk.END)
        if color != "-":
            self.product_entries["Колір"].insert(0, color)

        width = height = depth = ""
        if size_str:
            try:
                parts = size_str.split("x")
                if len(parts) == 3:
                    width, height, depth = parts
            except Exception:
                pass

        self.product_entries["Ширина (см)"].delete(0, tk.END)
        self.product_entries["Ширина (см)"].insert(0, str(width).strip())

        self.product_entries["Висота (см)"].delete(0, tk.END)
        self.product_entries["Висота (см)"].insert(0, str(height).strip())

        self.product_entries["Глибина (см)"].delete(0, tk.END)
        self.product_entries["Глибина (см)"].insert(0, str(depth).strip())

        self.product_entries["Базова ціна (грн)"].delete(0, tk.END)
        self.product_entries["Базова ціна (грн)"].insert(0, price_str)

        self.product_entries["Кількість на складі"].delete(0, tk.END)
        self.product_entries["Кількість на складі"].insert(0, str(stock))

    def _read_product_form(self):
        name = self.product_entries["Назва"].get().strip()
        category = self.product_entries["Категорія"].get().strip()
        material = self.product_entries["Матеріал"].get().strip() or None
        color = self.product_entries["Колір"].get().strip() or None

        def parse_float(field_name):
            raw = self.product_entries[field_name].get().strip()
            if not raw:
                return None
            return float(raw.replace(",", "."))

        width = parse_float("Ширина (см)")
        height = parse_float("Висота (см)")
        depth = parse_float("Глибина (см)")

        base_price_raw = self.product_entries["Базова ціна (грн)"].get().strip()
        stock_raw = self.product_entries["Кількість на складі"].get().strip()

        if not name or not category:
            raise ValueError("Назва та категорія обов'язкові.")
        if not base_price_raw:
            raise ValueError("Базова ціна обов'язкова.")

        base_price = float(base_price_raw.replace(",", "."))
        stock_qty = int(stock_raw) if stock_raw else 0

        return name, category, material, color, width, height, depth, base_price, stock_qty

    def on_add_product(self):
        try:
            data = self._read_product_form()
            add_product(*data)
            messagebox.showinfo("Успіх", "Новий товар додано.")
            self.refresh_products()
            self.refresh_logs()
        except ValueError as e:
            messagebox.showerror("Помилка", f"Невірні дані: {e}")

    def on_update_product(self):
        if self.selected_product_id is None:
            messagebox.showerror("Помилка", "Спочатку оберіть товар у таблиці.")
            return
        try:
            data = self._read_product_form()
            update_product(self.selected_product_id, *data)
            messagebox.showinfo("Успіх", "Дані товару оновлено.")
            self.refresh_products()
            self.refresh_logs()
        except ValueError as e:
            messagebox.showerror("Помилка", f"Невірні дані: {e}")

    def on_delete_product(self):
        if self.selected_product_id is None:
            messagebox.showerror("Помилка", "Спочатку оберіть товар у таблиці.")
            return
        if not messagebox.askyesno("Підтвердження", "Видалити вибраний товар?"):
            return
        try:
            delete_product(self.selected_product_id)
            messagebox.showinfo("Успіх", "Товар видалено.")
            self.selected_product_id = None
            self.refresh_products()
            self.refresh_logs()
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))

    def refresh_products(self):
        # читаємо фільтри
        name = self.filter_name_entry.get().strip()
        cat = self.filter_category_entry.get().strip()
        pmin_raw = self.filter_price_min_entry.get().strip()
        pmax_raw = self.filter_price_max_entry.get().strip()

        pmin = float(pmin_raw.replace(",", ".")) if pmin_raw else None
        pmax = float(pmax_raw.replace(",", ".")) if pmax_raw else None

        for row in self.products_tree.get_children():
            self.products_tree.delete(row)

        products = list_products_filtered(
            name_substr=name or None,
            category=cat or None,
            price_min=pmin,
            price_max=pmax,
        )
        for (pid, name, category, material, color,
             width, height, depth, price, stock) in products:
            size_str = ""
            if width and height and depth:
                size_str = f"{width:.0f}x{height:.0f}x{depth:.0f}"
            self.products_tree.insert(
                "", "end",
                values=(pid, name, category, material or "-", color or "-",
                        size_str, f"{price:.2f}", stock)
            )

        self.refresh_product_choices()



    def create_sales_tab(self):
        form_frame = ttk.LabelFrame(self.sales_frame, text="Оформлення продажу")
        form_frame.pack(side="top", fill="x", padx=10, pady=10)

        ttk.Label(form_frame, text="Товар:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(form_frame, textvariable=self.product_var, width=40, state="readonly")
        self.product_combo.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(form_frame, text="Кількість:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.sale_qty_entry = ttk.Entry(form_frame, width=10)
        self.sale_qty_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(form_frame, text="Ціна за одиницю (грн, опц.):").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.sale_price_entry = ttk.Entry(form_frame, width=10)
        self.sale_price_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(form_frame, text="Знижка, % (опц.):").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.discount_entry = ttk.Entry(form_frame, width=10)
        self.discount_entry.grid(row=3, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(form_frame, text="Ім'я покупця (опц.):").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.customer_entry = ttk.Entry(form_frame, width=25)
        self.customer_entry.grid(row=4, column=1, sticky="w", padx=5, pady=2)

        add_sale_btn = ttk.Button(form_frame, text="Зареєструвати продаж", command=self.on_add_sale)
        add_sale_btn.grid(row=5, column=0, columnspan=2, pady=10)

        # Фільтр продажів
        filter_frame = ttk.LabelFrame(self.sales_frame, text="Фільтр продажів")
        filter_frame.pack(side="top", fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Назва товару містить:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.sales_filter_name = ttk.Entry(filter_frame, width=20)
        self.sales_filter_name.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(filter_frame, text="Покупець містить:").grid(row=0, column=2, padx=5, pady=2, sticky="e")
        self.sales_filter_customer = ttk.Entry(filter_frame, width=20)
        self.sales_filter_customer.grid(row=0, column=3, padx=5, pady=2, sticky="w")

        ttk.Label(filter_frame, text="Дата від (РРРР-ММ-ДД):").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.sales_filter_from = ttk.Entry(filter_frame, width=12)
        self.sales_filter_from.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(filter_frame, text="до:").grid(row=1, column=2, padx=5, pady=2, sticky="e")
        self.sales_filter_to = ttk.Entry(filter_frame, width=12)
        self.sales_filter_to.grid(row=1, column=3, padx=5, pady=2, sticky="w")

        filter_btn = ttk.Button(filter_frame, text="Застосувати фільтр", command=self.refresh_sales)
        filter_btn.grid(row=0, column=4, padx=5, pady=2)

        reset_btn = ttk.Button(filter_frame, text="Скинути", command=self.reset_sales_filters)
        reset_btn.grid(row=1, column=4, padx=5, pady=2)

        # Таблиця продажів
        list_frame = ttk.LabelFrame(self.sales_frame, text="Останні продажі")
        list_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "date", "name", "category", "qty",
                   "price", "discount", "total", "customer")
        self.sales_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.sales_tree.pack(side="left", fill="both", expand=True)

        headings = {
            "id": "ID",
            "date": "Дата",
            "name": "Товар",
            "category": "Категорія",
            "qty": "К-сть",
            "price": "Ціна",
            "discount": "Знижка, %",
            "total": "Сума",
            "customer": "Покупець"
        }
        for col, text in headings.items():
            self.sales_tree.heading(col, text=text)
            self.sales_tree.column(col, width=100 if col != "name" else 160, anchor="center")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def reset_sales_filters(self):
        self.sales_filter_name.delete(0, tk.END)
        self.sales_filter_customer.delete(0, tk.END)
        self.sales_filter_from.delete(0, tk.END)
        self.sales_filter_to.delete(0, tk.END)
        self.refresh_sales()

    def refresh_product_choices(self):
        products = list_products()
        self.products_for_combo = {
            f"{pid}: {name} ({category})": pid
            for (pid, name, category, *_rest) in products
        }
        self.product_combo["values"] = list(self.products_for_combo.keys())

    def on_add_sale(self):
        try:
            product_label = self.product_var.get()
            if not product_label:
                messagebox.showerror("Помилка", "Оберіть товар.")
                return
            product_id = self.products_for_combo.get(product_label)
            if not product_id:
                messagebox.showerror("Помилка", "Невірний вибір товару.")
                return

            qty = int(self.sale_qty_entry.get())
            price_raw = self.sale_price_entry.get().strip()
            sale_price = float(price_raw.replace(",", ".")) if price_raw else None

            disc_raw = self.discount_entry.get().strip()
            discount_percent = float(disc_raw.replace(",", ".")) if disc_raw else 0.0

            customer_name = self.customer_entry.get().strip() or None

            add_sale(product_id, qty, sale_price, customer_name, discount_percent)
            messagebox.showinfo("Успіх", "Продаж зареєстровано.")
            self.refresh_products()
            self.refresh_sales()
            self.refresh_reports()
            self.refresh_logs()
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))

    def refresh_sales(self):
        name = self.sales_filter_name.get().strip()
        customer = self.sales_filter_customer.get().strip()
        d_from = self.sales_filter_from.get().strip()
        d_to = self.sales_filter_to.get().strip()

        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)

        sales = list_sales_filtered(
            name_substr=name or None,
            date_from=d_from or None,
            date_to=d_to or None,
            customer_substr=customer or None,
            limit=200,
        )
        for (sid, date, name, category, qty, price,
             discount, total, customer) in sales:
            self.sales_tree.insert(
                "", "end",
                values=(sid, date, name, category, qty,
                        f"{price:.2f}", f"{discount:.1f}", f"{total:.2f}", customer or "-")
            )



    def create_reports_tab(self):
        top_frame = ttk.Frame(self.reports_frame)
        top_frame.pack(side="top", fill="x", padx=10, pady=10)

        ttk.Button(top_frame, text="Оновити звіти", command=self.refresh_reports)\
            .pack(side="left", padx=5)

        ttk.Button(top_frame, text="Експорт виручки у CSV", command=self.export_revenue_csv)\
            .pack(side="left", padx=5)

        ttk.Button(top_frame, text="Експорт залишків у CSV", command=self.export_stock_csv)\
            .pack(side="left", padx=5)

        revenue_frame = ttk.LabelFrame(self.reports_frame, text="Виручка за днями")
        revenue_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.revenue_tree = ttk.Treeview(
            revenue_frame, columns=("date", "total"), show="headings", height=15
        )
        self.revenue_tree.heading("date", text="Дата")
        self.revenue_tree.heading("total", text="Виручка, грн")
        self.revenue_tree.column("date", width=100, anchor="center")
        self.revenue_tree.column("total", width=120, anchor="center")
        self.revenue_tree.pack(side="left", fill="both", expand=True)

        rev_scroll = ttk.Scrollbar(revenue_frame, orient="vertical",
                                   command=self.revenue_tree.yview)
        self.revenue_tree.configure(yscrollcommand=rev_scroll.set)
        rev_scroll.pack(side="right", fill="y")

        stock_frame = ttk.LabelFrame(self.reports_frame, text="Залишки на складі")
        stock_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.stock_tree = ttk.Treeview(
            stock_frame, columns=("id", "name", "category", "stock"),
            show="headings", height=15
        )
        self.stock_tree.heading("id", text="ID")
        self.stock_tree.heading("name", text="Назва")
        self.stock_tree.heading("category", text="Категорія")
        self.stock_tree.heading("stock", text="Залишок")
        for col in ("id", "name", "category", "stock"):
            self.stock_tree.column(col, width=120 if col == "name" else 100, anchor="center")

        self.stock_tree.pack(side="left", fill="both", expand=True)

        stock_scroll = ttk.Scrollbar(stock_frame, orient="vertical",
                                     command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=stock_scroll.set)
        stock_scroll.pack(side="right", fill="y")

    def refresh_reports(self):
        for row in self.revenue_tree.get_children():
            self.revenue_tree.delete(row)

        for date, total in report_total_by_day():
            self.revenue_tree.insert("", "end",
                                     values=(date, f"{total:.2f}"))

        for row in self.stock_tree.get_children():
            self.stock_tree.delete(row)

        products = list_products()
        for (pid, name, category, material, color,
             width, height, depth, price, stock) in products:
            self.stock_tree.insert("", "end",
                                   values=(pid, name, category, stock))

    def export_revenue_csv(self):
        filename = filedialog.asksaveasfilename(
            title="Зберегти звіт по виручці",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filename:
            return
        rows = report_total_by_day()
        try:
            with open(filename, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Дата", "Виручка, грн"])
                for date, total in rows:
                    writer.writerow([date, f"{total:.2f}"])
            messagebox.showinfo("Експорт", "Звіт по виручці збережено.")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти файл: {e}")

    def export_stock_csv(self):
        filename = filedialog.asksaveasfilename(
            title="Зберегти звіт по залишках",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filename:
            return
        rows = list_products()
        try:
            with open(filename, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "ID", "Назва", "Категорія", "Матеріал", "Колір",
                    "Ширина", "Висота", "Глибина", "Ціна, грн", "Залишок"
                ])
                for (pid, name, category, material, color,
                     width, height, depth, price, stock) in rows:
                    writer.writerow([
                        pid, name, category, material or "", color or "",
                        width or "", height or "", depth or "",
                        f"{price:.2f}", stock
                    ])
            messagebox.showinfo("Експорт", "Звіт по залишках збережено.")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти файл: {e}")


    def create_logs_tab(self):
        top_frame = ttk.Frame(self.logs_frame)
        top_frame.pack(side="top", fill="x", padx=10, pady=10)

        ttk.Button(top_frame, text="Оновити журнал", command=self.refresh_logs)\
            .pack(side="left", padx=5)

        list_frame = ttk.LabelFrame(self.logs_frame, text="Журнал дій системи")
        list_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        columns = ("ts", "user", "action", "details")
        self.logs_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        self.logs_tree.pack(side="left", fill="both", expand=True)

        headings = {
            "ts": "Час",
            "user": "Користувач",
            "action": "Дія",
            "details": "Деталі"
        }
        for col, text in headings.items():
            self.logs_tree.heading(col, text=text)
            width = 120 if col in ("ts", "user") else 300
            self.logs_tree.column(col, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.logs_tree.yview)
        self.logs_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def refresh_logs(self):
        for row in self.logs_tree.get_children():
            self.logs_tree.delete(row)

        logs = list_logs(limit=200)
        for ts, user, action, details in logs:
            self.logs_tree.insert("", "end",
                                  values=(ts, user or "-", action, details or ""))
