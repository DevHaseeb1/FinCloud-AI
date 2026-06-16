"""
AWS credential encryption/decryption and client creation.
"""

import os
import base64
import logging
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.settings import get_settings

logger = logging.getLogger(__name__)


def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def _get_fernet() -> Fernet:
    settings = get_settings()
    key = settings.aws_credential_encryption_key
    if not key:
        key = os.getenv("AWS_CREDENTIAL_ENCRYPTION_KEY", "")
    if not key:
        key = "fincloud-default-dev-key-change-in-production"
    salt = b"fincloud-aws-salt"
    return Fernet(_derive_key(key, salt))


def encrypt_credential(value: str) -> str:
    f = _get_fernet()
    return f.encrypt(value.encode()).decode()


def decrypt_credential(encrypted: str) -> str:
    f = _get_fernet()
    return f.decrypt(encrypted.encode()).decode()


def create_aws_client(
    service_name: str,
    region: str = "us-east-1",
    role_arn: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    external_id: Optional[str] = None,
):
    """
    Create a boto3 client using either IAM role or access keys.
    Falls back to default credential chain if neither is provided.
    """
    import boto3
    from botocore.config import Config

    config = Config(
        retries={"max_attempts": 3, "mode": "adaptive"},
        connect_timeout=30,
        read_timeout=60,
    )

    if access_key and secret_key:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )
    else:
        session = boto3.Session(region_name=region)

    client = session.client(service_name, config=config)

    if role_arn:
        sts = session.client("sts")
        assume_role_kwargs = {
            "RoleArn": role_arn,
            "RoleSessionName": "FinCloudAISession",
        }
        if external_id:
            assume_role_kwargs["ExternalId"] = external_id
        response = sts.assume_role(**assume_role_kwargs)
        creds = response["Credentials"]
        client = boto3.Session(
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
            region_name=region,
        ).client(service_name, config=config)

    return client
