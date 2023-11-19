import sqlite3


def setup():
    conn = sqlite3.connect("health.sqlite")
    c = conn.cursor()

    c.execute(
        """
            CREATE TABLE IF NOT EXISTS health
            (id INTEGER PRIMARY KEY ASC, 
            receiver VARCHAR(100) NOT NULL,
            storage VARCHAR(100) NOT NULL,
            processing VARCHAR(100) NOT NULL,
            audit VARCHAR(100) NOT NULL,
            last_update VARCHAR(100) NOT NULL,
            date_created DateTime)
        """
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    setup()
