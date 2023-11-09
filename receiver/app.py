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

MAX_EVENTS = 10
EVENT_FILE = "events.json"
ENDPOINT = "http://localhost:8090"

with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())
    events_config = app_config.get("events")

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")


def report_asteroid_direction(body):
    event_name = "save-direction"
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id
    logger.info(f"Received {event_name} request with a trace id of {trace_id}) ")

    client = KafkaClient(
        hosts=f'{events_config.get("hostname")}:{events_config.get("port")}'
    )
    topic = client.topics[str.encode(events_config["topic"])]
    producer = topic.get_sync_producer()
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

    client = KafkaClient(
        hosts=f'{events_config.get("hostname")}:{events_config.get("port")}'
    )
    topic = client.topics[str.encode(events_config["topic"])]
    producer = topic.get_sync_producer()
    msg = {
        "type": "sc",
        "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body,
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode("utf-8"))

    logger.info(f"event {event_name} response (id: {trace_id}) with status {201}")

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
