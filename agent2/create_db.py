import sqlite3

DB_PATH = "weather_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            humidity INTEGER,
            wind_speed REAL,
            pressure REAL,
            storm_risk BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
