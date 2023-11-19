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
from flask_cors import CORS

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

with open(log_conf_file, "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)


def health():
    return {}, 200


def request_application_health(application_name):
    status = "Down"

    try:
        response = requests.get(
            f"http://localhost{app_config['requests'][application_name]}",
            timeout=int(app_config["requests"]["timeout_sec"]),
        )
        if response.status_code == 200:
            status = "Running"
    except:
        pass

    return status


def retrieve_health():
    logger.info("Starting periodic health checks...")
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    logger.info(f"time {current_time}")
    receiver = request_application_health("receiver")
    logger.info(receiver)


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(
        retrieve_health, "interval", seconds=app_config["scheduler"]["period_sec"]
    )
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config["CORS_HEADERS"] = "Content-Type"


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120, use_reloader=False)
