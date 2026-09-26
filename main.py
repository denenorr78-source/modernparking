from database import Database
from ui import ParkingApp


def main():
    db = Database()
    db.initialize()

    app = ParkingApp(db)
    app.run()


if __name__ == "__main__":
    main()
