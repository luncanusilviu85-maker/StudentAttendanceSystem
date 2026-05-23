"""
AWS CloudWatch Logs integration.
Sends application logs to a CloudWatch log group using watchtower.
Attach this handler to the root logger in your WSGI entry point.
"""

import logging
import os
import boto3
import watchtower

LOG_GROUP  = os.environ.get('CLOUDWATCH_LOG_GROUP', '/attendance-system/app')
LOG_STREAM = os.environ.get('CLOUDWATCH_LOG_STREAM', 'flask-app')
AWS_REGION = os.environ.get('AWS_REGION', 'eu-west-1')


def configure_cloudwatch_logging(app_logger: logging.Logger = None):
    """
    Add a CloudWatch Logs handler to `app_logger` (defaults to root logger).
    Safe to call multiple times (idempotent via handler type check).
    """
    target = app_logger or logging.getLogger()

    # Avoid duplicate handlers on reload
    if any(isinstance(h, watchtower.CloudWatchLogHandler) for h in target.handlers):
        return

    try:
        cw_client = boto3.client('logs', region_name=AWS_REGION)
        handler   = watchtower.CloudWatchLogHandler(
            boto3_client       = cw_client,
            log_group_name     = LOG_GROUP,
            log_stream_name    = LOG_STREAM,
            send_interval      = 60,      # flush every 60 s
            create_log_group   = True,
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s  %(levelname)-8s  %(name)s  %(message)s'
        ))
        target.addHandler(handler)
        target.setLevel(logging.INFO)
        target.info("CloudWatch logging configured (group=%s, stream=%s)",
                    LOG_GROUP, LOG_STREAM)
    except Exception as exc:
        # Never crash the app if CloudWatch is unavailable
        logging.warning("CloudWatch handler setup failed: %s", exc)
