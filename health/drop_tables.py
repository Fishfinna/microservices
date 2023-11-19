import sqlite3

conn = sqlite3.connect("health.sqlite")

c = conn.cursor()
c.execute(
    """
          DROP TABLE health
    """
)

conn.commit()
conn.close()
