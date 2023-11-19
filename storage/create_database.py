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
c.execute(
    """
          CREATE TABLE direction
          (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
            trace_id VARCHAR(250) NOT NULL, 
            record_id VARCHAR(250) NOT NULL, 
            asteroid_id VARCHAR(250) NOT NULL,
            collision_risk BOOLEAN NOT NULL,
            direction INTEGER NOT NULL,
            km_per_hour INTEGER NOT NULL,
            moving_towards_earth BOOLEAN NOT NULL,
            timestamp VARCHAR(250) NOT NULL,
            date_created VARCHAR(100) NOT NULL)
          """
)

c.execute(
    """
        CREATE TABLE scale
        (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
            trace_id VARCHAR(250) NOT NULL, 
            record_id VARCHAR(250) NOT NULL, 
            asteroid_id VARCHAR(250) NOT NULL,
            depth_cm INTEGER NOT NULL,
            estimated_kg_weight INTEGER NOT NULL,
            height_cm INTEGER NOT NULL,
            material VARCHAR(100) NOT NULL,
            timestamp VARCHAR(100) NOT NULL,
            width_cm INTEGER NOT NULL,
            date_created VARCHAR(100) NOT NULL
            )
          """
)

connection.commit()
connection.close()
