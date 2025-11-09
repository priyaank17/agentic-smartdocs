"""Global Logger Module."""

import os
import logging
import watchtower
import coloredlogs
from dotenv import load_dotenv

load_dotenv()


HANDLER = None
if "SANDBOX_ENV" in os.environ or "DO_NOT_USE_BOTO3_LOGS" in os.environ:
    print(
        "Environmental Variable SANDBOX_ENV/DO_NOT_USE_BOTO3_LOGS found. "
        + "Skipping the Boto3-Create_Log_Group."
    )
else:
    print(
        "Enabling Boto3 Cloudwatch Logs. This would require your AWS "
        + "credentials to be configured in your environment. "
        + "If you are using your sandbox environment, "
        + "Provide environment variable SANDBOX_ENV=true or "
        + "DO_NOT_USE_BOTO3_LOGS=true to not to "
        + "use CloudWatchLogs."
    )
    HANDLER = watchtower.CloudWatchLogHandler()
    # logging.getLogger("werkzeug").addHandler(handler)


LOG_FORMAT = None

if "LOG_FORMAT" in os.environ:
    LOG_FORMAT = os.environ["LOG_FORMAT"]
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)
coloredlogs.install(level="INFO", logger=logger, fmt=LOG_FORMAT)
print("Logger Configured.......")
prompt_logger = logging.getLogger("prompt_info")
prompt_logger.setLevel(logging.INFO)
