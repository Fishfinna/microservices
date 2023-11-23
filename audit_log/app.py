import connexion
import yaml
import json
from pykafka import KafkaClient
import logging
import logging.config
from flask_cors import CORS
import os
from connexion import NoContent


if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"


with open(app_conf_file, "r") as f:
    app_config = yaml.safe_load(f.read())
    events_config = app_config.get("events")

with open(log_conf_file, "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)


def get_direction(index):
    hostname = "%s:%d" % (
        app_config["events"]["hostname"],
        app_config["events"]["port"],
    )
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True, consumer_timeout_ms=1000
    )
    logger.info("Retrieving Direction at index %d" % index)

    try:
        direction_messages = []
        for msg in consumer:
            msg_str = msg.value.decode("utf-8")
            msg = json.loads(msg_str)
            payload = msg["payload"]
            if msg["type"] == "di":
                direction_messages.append(payload)
        if direction_messages[index]:
            logger.info(f"located event {direction_messages[index]} at index {index}")
            return direction_messages[index], 200
    except Exception as e:
        logger.error("No messages found at requested index! error:", type(e))

    logger.error("could not find direction at index %d" % index)
    return {"message": f"Event at index {index} Not Found"}, 404


def get_scale(index):
    hostname = "%s:%d" % (
        app_config["events"]["hostname"],
        app_config["events"]["port"],
    )
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True, consumer_timeout_ms=1000
    )
    logger.info("Retrieving scale at index %d" % index)

    try:
        scale_messages = []
        for msg in consumer:
            msg_str = msg.value.decode("utf-8")
            msg = json.loads(msg_str)
            payload = msg["payload"]
            if msg["type"] == "sc":
                scale_messages.append(payload)
        if scale_messages[index]:
            logger.info(f"located event {scale_messages[index]} at index {index}")
            return scale_messages[index], 200
    except Exception as e:
        logger.error("No messages found at requested index! error:", type(e))

    logger.error("could not find direction at index %d" % index)
    return {"message": f"Event at index {index} Not Found"}, 404


def health():
    return NoContent, 200


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api(
    "openapi.yml",
    base_path="/audit_log",
    strict_validation=True,
    validate_responses=True,
)

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config["CORS_HEADERS"] = "Content-Type"

if __name__ == "__main__":
    app.run(port=8110)
