import mysql.connector
import yaml

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())
    data = app_config["datastore"]

connection = mysql.connector.connect(
    host=data["hostname"],
    user=data["user"],
    password=data["password"],
    database=data["db"],
)
c = connection.cursor()
c.execute("""DROP TABLE direction, scale""")

connection.commit()
connection.close()
