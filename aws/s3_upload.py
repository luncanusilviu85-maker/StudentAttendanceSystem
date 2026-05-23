"""
AWS S3 upload helper.
Uses IAM role credentials attached to the EC2 instance (no hard-coded keys).
Generates a pre-signed URL valid for 7 days after upload.
"""

import logging
import os
import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'attendance-reports-bucket')
AWS_REGION  = os.environ.get('AWS_REGION', 'eu-west-1')
PREFIX      = 'reports/'
EXPIRY      = 604800  # 7 days in seconds


def _get_client():
    """Return a boto3 S3 client; credentials come from the instance IAM role."""
    return boto3.client('s3', region_name=AWS_REGION)


def upload_report_to_s3(data: bytes, filename: str) -> str | None:
    """
    Upload `data` to S3 under the reports/ prefix.
    Returns a pre-signed download URL, or None on failure.

    Parameters
    ----------
    data     : raw bytes to upload (e.g. CSV content)
    filename : S3 object key suffix (without prefix)
    """
    key = f"{PREFIX}{filename}"
    try:
        client = _get_client()
        client.put_object(
            Bucket      = BUCKET_NAME,
            Key         = key,
            Body        = data,
            ContentType = 'text/csv',
            # Server-side encryption with AWS-managed keys
            ServerSideEncryption = 'AES256',
        )
        url = client.generate_presigned_url(
            'get_object',
            Params     = {'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn  = EXPIRY,
        )
        logger.info("Uploaded report to s3://%s/%s", BUCKET_NAME, key)
        return url

    except (BotoCoreError, ClientError) as exc:
        logger.error("S3 upload failed: %s", exc)
        return None


def list_reports() -> list[dict]:
    """List all objects under reports/ prefix; returns metadata dicts."""
    try:
        client   = _get_client()
        response = client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)
        return response.get('Contents', [])
    except (BotoCoreError, ClientError) as exc:
        logger.error("S3 list failed: %s", exc)
        return []
