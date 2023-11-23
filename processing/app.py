import connexion
from connexion import NoContent
from datetime import datetime
import requests
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
from flask_cors import CORS, cross_origin

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
    data_file = app_config["datastore"]["filename"]

with open(log_conf_file, "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)


def get_stats():
    logger.info("Get stats request started.")

    if os.path.isfile(data_file):
        # Read in the data
        with open(data_file, "r") as f:
            json_data = json.load(f)

        logger.debug(f"Statistics message content: {json_data}")
        logger.info("Get stats request complete.")

        return json_data, 200
    else:
        logger.error("File does not exist")
        return "Statistics do not exist", 404


def populate_stats():
    """Periodically update stats"""
    if os.path.isfile(data_file):
        with open(data_file, "r") as f:
            json_data = json.load(f)
    else:
        json_data = {
            "num_direction_readings": 0,
            "max_direction_readings": 0,
            "num_scale_readings": 0,
            "max_scale_readings": 0,
            "last_updated": "2021-02-05T12:39:16.005Z",
        }
    logger.info("Starting periodic processing...")

    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    last_update_time = json_data["last_updated"]

    direction_response = requests.get(
        f"{ENDPOINT}/direction?start_timestamp={last_update_time}&end_timestamp={current_time}"
    )
    direction_data = direction_response.json()
    direction_count = len(direction_data)

    scale_response = requests.get(
        f"{ENDPOINT}/scale?start_timestamp={last_update_time}&end_timestamp={current_time}"
    )
    scale_data = scale_response.json()
    scale_count = len(scale_data)

    if scale_response.status_code != 200:
        logger.error(
            f"Error with request! scale status code: {scale_response.status_code}"
        )
        return NoContent, scale_response.status_code

    if direction_response.status_code != 200:
        logger.error(
            f"Error with request! direction status code: {direction_response.status_code}"
        )
        return NoContent, direction_response.status_code

    logger.info(
        f"Number of events received: scale {scale_count}, direction {direction_count}"
    )

    if direction_count:
        max_direction = max(
            [
                json_data["max_direction_readings"],
                max([float(i["direction"]) for i in direction_data]),
            ]
        )
    else:
        max_direction = json_data["max_direction_readings"]

    if scale_count:
        max_scale = max(
            [
                json_data["max_scale_readings"],
                max([float(i["estimated_kg_weight"]) for i in scale_data]),
            ]
        )
    else:
        max_scale = json_data["max_scale_readings"]

    updated_content = {
        "num_direction_readings": json_data["num_direction_readings"] + direction_count,
        "max_direction_readings": max_direction,
        "num_scale_readings": json_data["num_scale_readings"] + scale_count,
        "max_scale_readings": max_scale,
        "last_updated": current_time,
    }

    with open(data_file, "w") as f:
        json.dump(updated_content, f)

    logger.debug(f"stored updated data: {updated_content}")
    logger.info("Periodic processing has ended.")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(
        populate_stats, "interval", seconds=app_config["scheduler"]["period_sec"]
    )
    sched.start()


def health():
    return NoContent, 200


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api(
    "openapi.yml",
    base_path="/processing",
    strict_validation=True,
    validate_responses=True,
)

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config["CORS_HEADERS"] = "Content-Type"

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
