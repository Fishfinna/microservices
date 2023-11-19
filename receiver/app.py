import connexion
from connexion import NoContent
from datetime import datetime
import yaml
import json
from pykafka import KafkaClient
import logging
import logging.config
import uuid
import time
import os

MAX_EVENTS = 10
EVENT_FILE = "events.json"
ENDPOINT = "http://localhost:8090"

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

max_retries = int(app_config["max_retries"])
current_retry_count = 0
while current_retry_count < max_retries:
    try:
        logger.info(
            f"Attempting connection to Kafka (attempt {current_retry_count} of {max_retries})"
        )
        client = KafkaClient(
            hosts=f'{events_config.get("hostname")}:{events_config.get("port")}'
        )
        topic = client.topics[str.encode(events_config["topic"])]
        global producer
        producer = topic.get_sync_producer()
        logger.info(f"Successfully connected to kafka")
        break
    except Exception as e:
        logger.error(f"attempt {current_retry_count} failed to connect to kafka")
        time.sleep(app_config["sleep_time"])
        current_retry_count += 1
    if current_retry_count == max_retries:
        logger.error("Failed to connect to kafka")


def report_asteroid_direction(body):
    event_name = "save-direction"
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id
    logger.info(f"Received {event_name} request with a trace id of {trace_id}) ")
    msg = {
        "type": "di",
        "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body,
    }
    msg_str = json.dumps(msg)

    producer.produce(msg_str.encode("utf-8"))

    logger.info(f"event {event_name} response (id: {trace_id}) with status {201}")

    return NoContent, 201


def report_asteroid_scale(body):
    event_name = "save-scale"
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id
    logger.info(f"Received {event_name} request with a trace id of {trace_id}) ")
    msg = {
        "type": "sc",
        "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body,
    }
    msg_str = json.dumps(msg)

    producer.produce(msg_str.encode("utf-8"))

    logger.info(f"event {event_name} response (id: {trace_id}) with status {201}")

    return NoContent, 201


def health():
    return NoContent, 200


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
