import connexion
from datetime import datetime
import requests
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
import os
import create_tables
from health import Health
from sqlalchemy import create_engine, desc
from base import Base
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS

create_tables.setup()
DB_ENGINE = create_engine("sqlite:///health.sqlite")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)
SERVICE_LIST = ["receiver", "storage", "processing", "audit"]


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
    logger.info("Health status requested")
    session = DB_SESSION()
    latest_reading = session.query(Health).order_by(desc(Health.date_created)).first()
    session.close()
    if latest_reading is None:
        return {"error": "No health readings available"}, 404

    # extract the desired data
    results = {}
    for service in SERVICE_LIST:
        results[service] = latest_reading.to_dict()[service]
    results["last_update"] = latest_reading.to_dict()["last_update"]
    print(results)
    return results, 200


def request_application_health(application_name):
    status = "Down"
    try:
        response = requests.get(
            f"http://{app_config['requests']['host']}{app_config['requests'][application_name]}",
            timeout=int(app_config["requests"]["timeout_sec"]),
        )
        if response.status_code == 200:
            status = "Running"
    except:
        pass
    return status


def retrieve_health():
    logger.info("Starting periodic health checks...")

    results = {}
    for service in SERVICE_LIST:
        status = request_application_health(service)
        logger.info(f"{service} is found to be {status}")
        results[service] = status
    results["last_update"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    health_results = Health(**results)
    session = DB_SESSION()
    session.add(health_results)
    session.commit()
    session.close()
    logger.info("Results stored to database")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(
        retrieve_health, "interval", seconds=app_config["scheduler"]["period_sec"]
    )
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api(
    "openapi.yml",
    base_path="/health",
    strict_validation=True,
    validate_responses=True,
)

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config["CORS_HEADERS"] = "Content-Type"

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120, use_reloader=False)
