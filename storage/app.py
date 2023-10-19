import connexion
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from connexion import NoContent
from base import Base
from direction import Direction
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from datetime import datetime
from scale import Scale
import yaml
import json
import logging
import logging.config

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())
    data = app_config["datastore"]

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")

DB_ENGINE = create_engine(
    f'mysql+pymysql://{data["user"]}:{data["password"]}@{data["hostname"]}:{data["port"]}/{data["db"]}'
)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)
if DB_SESSION:
    logger.info(f"connected to DB. Hostname:{data['hostname']} Port:{data['port']}")


def get_asteroid_scale(timestamp):
    """Gets the asteroid scale readings from after the timestamp"""
    session = DB_SESSION()
    timestamp_datetime = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    readings = session.query(Scale).filter(Scale.date_created >= timestamp_datetime)

    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info(
        f"Query for Asteroid Scale reading after {timestamp} returns {len(results_list)}"
    )

    return results_list, 200


def get_asteroid_direction(timestamp):
    """Gets the asteroid direction readings from after the timestamp"""
    session = DB_SESSION()
    timestamp_datetime = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    readings = session.query(Direction).filter(
        Direction.date_created >= timestamp_datetime
    )

    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info(
        f"Query for Asteroid Direction reading after {timestamp} returns {len(results_list)}"
    )

    return results_list, 200


def process_messages():
    hostname = "%s:%d" % (
        app_config["events"]["hostname"],
        app_config["events"]["port"],
    )
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(
        consumer_group=b"event_group",
        reset_offset_on_start=False,
        auto_offset_reset=OffsetType.LATEST,
    )
    traced = []

    for msg in consumer:
        msg_str = msg.value.decode("utf-8")
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]
        if payload["trace_id"] not in traced:
            if msg["type"] == "di":
                session = DB_SESSION()

                direction = Direction(
                    payload["trace_id"],
                    payload["asteroid_id"],
                    payload["collision_risk"],
                    payload["direction"],
                    payload["km_per_hour"],
                    payload["moving_towards_earth"],
                    payload["record_id"],
                    payload["timestamp"],
                )
                logger.debug(
                    f"Stored event direction request with a trace id of {payload['trace_id']}"
                )

                session.add(direction)
                session.commit()
                session.close()
            if msg["type"] == "sc":
                session = DB_SESSION()

                scale = Scale(
                    payload["trace_id"],
                    payload["asteroid_id"],
                    payload["depth_cm"],
                    payload["estimated_kg_weight"],
                    payload["height_cm"],
                    payload["material"],
                    payload["record_id"],
                    payload["timestamp"],
                    payload["width_cm"],
                )
                logger.debug(
                    f"Stored event scale request with a trace id of {payload['trace_id']}"
                )

                session.add(scale)
                session.commit()
                session.close()
        traced.append(payload["trace_id"])
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
