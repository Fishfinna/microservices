import connexion
import yaml
import json
from pykafka import KafkaClient
import logging
import logging.config
from flask_cors import CORS
import os
from connexion import NoContent


def load_configuration_files():
    """
    Load configuration files based on the environment.

    Returns:
        Tuple: A tuple containing app_config and events_config dictionaries.
    """
    if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
        print("In Test Environment")
        app_conf_file = "/config/app_conf.yml"
        log_conf_file = "/config/log_conf.yml"
    else:
        print("In Dev Environment")
        app_conf_file = "app_conf.yml"
        log_conf_file = "log_conf.yml"

    with open(app_conf_file, "r") as f:
        app_config = yaml.safe_load(f)
        events_config = app_config.get("events")

    return app_config, events_config


app_config, events_config = load_configuration_files()

with open(log_conf_file, "r") as f:
    log_config = yaml.safe_load(f)
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)


def get_event_at_index(index, event_type):
    """
    Retrieve an event of the specified type at a given index from Kafka.

    Args:
        index (int): The index of the event.
        event_type (str): The type of the event ("di" for direction, "sc" for scale).

    Returns:
        Tuple: A tuple containing the event and HTTP status code.
    """
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True, consumer_timeout_ms=1000
    )
    logger.info(f"Retrieving {event_type} at index {index}")

    try:
        event_messages = []
        for msg in consumer:
            msg_str = msg.value.decode("utf-8")
            msg = json.loads(msg_str)
            payload = msg["payload"]
            if msg["type"] == event_type:
                event_messages.append(payload)
        if event_messages[index]:
            logger.info(f"Located event {event_messages[index]} at index {index}")
            return event_messages[index], 200
    except Exception as e:
        logger.error(f"No messages found at requested index! Error: {type(e)}")

    logger.error(f"Could not find {event_type} at index {index}")
    return {"message": f"Event at index {index} Not Found"}, 404


def get_direction(index):
    """
    Retrieve a direction event at a given index from Kafka.

    Args:
        index (int): The index of the event.

    Returns:
        Tuple: A tuple containing the direction event and HTTP status code.
    """
    return get_event_at_index(index, "di")


def get_scale(index):
    """
    Retrieve a scale event at a given index from Kafka.

    Args:
        index (int): The index of the event.

    Returns:
        Tuple: A tuple containing the scale event and HTTP status code.
    """
    return get_event_at_index(index, "sc")


def health():
    """
    Endpoint for checking the health of the application.

    Returns:
        Tuple: A tuple indicating a successful health check with HTTP status code.
    """
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
