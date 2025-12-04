from db import init_db, seed_test_data
from ui import FurnitureApp


if __name__ == "__main__":
    init_db()
    seed_test_data()

    app = FurnitureApp()
    app.mainloop()
