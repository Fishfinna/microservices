import os
import logging
import logging.config
import yaml
import json
from pykafka import KafkaClient
from flask_cors import CORS
from connexion import NoContent
import connexion

APP_CONF_FILE = (
    "/config/app_conf.yml" if os.environ.get("TARGET_ENV") == "test" else "app_conf.yml"
)
LOG_CONF_FILE = (
    "/config/log_conf.yml" if os.environ.get("TARGET_ENV") == "test" else "log_conf.yml"
)

with open(APP_CONF_FILE, "r", encoding="utf-8") as f:
    app_config = yaml.safe_load(f.read())
    events_config = app_config.get("events")

with open(LOG_CONF_FILE, "r", encoding="utf-8") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")

logger.info("App Conf File: %s", APP_CONF_FILE)
logger.info("Log Conf File: %s", LOG_CONF_FILE)


def get_direction(index):
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True, consumer_timeout_ms=1000
    )
    logger.info(f"Retrieving Direction at index {index}")

    try:
        direction_messages = [
            json.loads(msg.value.decode("utf-8")["payload"])
            for msg in consumer
            if json.loads(msg.value.decode("utf-8")["type"]) == "di"
        ]
        if direction_messages[index]:
            logger.info(f"Located event {direction_messages[index]} at index {index}")
            return direction_messages[index], 200
    except Exception as e:
        logger.error("No messages found at requested index! Error: %s", type(e))

    logger.error("Could not find direction at index %d", index)
    return {"message": f"Event at index {index} Not Found"}, 404


def get_scale(index):
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True, consumer_timeout_ms=1000
    )
    logger.info(f"Retrieving scale at index {index}")

    try:
        scale_messages = [
            json.loads(msg.value.decode("utf-8")["payload"])
            for msg in consumer
            if json.loads(msg.value.decode("utf-8")["type"]) == "sc"
        ]
        if scale_messages[index]:
            logger.info(f"Located event {scale_messages[index]} at index {index}")
            return scale_messages[index], 200
    except Exception as e:
        logger.error("No messages found at requested index! Error: %s", type(e))

    logger.error("Could not find direction at index %d", index)
    return {"message": f"Event at index {index} Not Found"}, 404


def health():
    return NoContent, 200


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api(
    "openapi.yml",
    base_path="/audit",
    strict_validation=True,
    validate_responses=True,
)

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config["CORS_HEADERS"] = "Content-Type"

if __name__ == "__main__":
    app.run(port=8110)
