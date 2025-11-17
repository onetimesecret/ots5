"""Redis client for secret storage."""

import json
import logging
from typing import Optional
from datetime import datetime

import redis
from redis.connection import ConnectionPool

from onetimesecret.core.exceptions import StorageException, SecretNotFoundException
from onetimesecret.models.secret import SecretMetadata

logger = logging.getLogger(__name__)


class SecretStorage:
    """
    Redis-backed storage for secrets.

    Following v0.23+ pattern using database 0 for all models
    with improved connection pooling.
    """

    def __init__(self, redis_url: str, db: int = 0):
        """
        Initialize the storage client.

        Args:
            redis_url: Redis connection URL
            db: Redis database number (default: 0)
        """
        try:
            self.pool = ConnectionPool.from_url(redis_url, db=db, decode_responses=True)
            self.client = redis.Redis(connection_pool=self.pool)
            # Test connection
            self.client.ping()
        except redis.RedisError as e:
            raise StorageException(f"Failed to connect to Redis: {str(e)}")

    def store_secret(self, metadata: SecretMetadata) -> None:
        """
        Store a secret and its metadata in Redis.

        Args:
            metadata: Secret metadata including encrypted content

        Raises:
            StorageException: If storage operation fails
        """
        try:
            # Store the encrypted content with TTL
            secret_stored = self.client.setex(
                metadata.secret_key,
                metadata.ttl,
                metadata.encrypted_content
            )

            if not secret_stored:
                raise StorageException("Failed to store secret content")

            # Store salt if present
            if metadata.salt:
                self.client.setex(
                    f"{metadata.secret_key}:salt",
                    metadata.ttl,
                    metadata.salt
                )

            # Store metadata separately with same TTL
            metadata_key = f"{metadata.secret_key}:metadata"
            metadata_dict = {
                "secret_key": metadata.secret_key,
                "has_passphrase": metadata.has_passphrase,
                "created_at": metadata.created_at.isoformat(),
                "ttl": metadata.ttl,
                "viewed": metadata.viewed
            }

            self.client.setex(
                metadata_key,
                metadata.ttl,
                json.dumps(metadata_dict)
            )

        except redis.RedisError as e:
            raise StorageException(f"Failed to store secret: {str(e)}")

    def retrieve_secret(self, secret_key: str, destroy: bool = True) -> tuple[str, Optional[str]]:
        """
        Retrieve a secret's encrypted content and salt.

        Args:
            secret_key: Unique secret identifier
            destroy: Whether to delete secret after retrieval (default: True)

        Returns:
            Tuple of (encrypted_content, salt)

        Raises:
            SecretNotFoundException: If secret is not found
            StorageException: If retrieval operation fails
        """
        try:
            # Retrieve encrypted content
            encrypted_content = self.client.get(secret_key)
            if not encrypted_content:
                raise SecretNotFoundException()

            # Retrieve salt if it exists
            salt = self.client.get(f"{secret_key}:salt")

            if destroy:
                # Delete the secret and salt (one-time access)
                pipe = self.client.pipeline()
                pipe.delete(secret_key)
                if salt:
                    pipe.delete(f"{secret_key}:salt")
                pipe.execute()

                # Update metadata to mark as viewed
                metadata_key = f"{secret_key}:metadata"
                metadata_json = self.client.get(metadata_key)
                if metadata_json:
                    metadata_dict = json.loads(metadata_json)
                    metadata_dict["viewed"] = True
                    # Get remaining TTL for metadata
                    ttl = self.client.ttl(metadata_key)
                    if ttl > 0:
                        self.client.setex(metadata_key, ttl, json.dumps(metadata_dict))

            return encrypted_content, salt

        except SecretNotFoundException:
            raise
        except redis.RedisError as e:
            raise StorageException(f"Failed to retrieve secret: {str(e)}")

    def get_metadata(self, secret_key: str) -> Optional[dict]:
        """
        Retrieve secret metadata without destroying the secret.

        Args:
            secret_key: Unique secret identifier

        Returns:
            Metadata dictionary or None if not found

        Raises:
            StorageException: If retrieval operation fails
        """
        try:
            metadata_key = f"{secret_key}:metadata"
            metadata_json = self.client.get(metadata_key)

            if not metadata_json:
                return None

            metadata_dict = json.loads(metadata_json)
            # Parse datetime
            metadata_dict["created_at"] = datetime.fromisoformat(metadata_dict["created_at"])

            return metadata_dict

        except redis.RedisError as e:
            raise StorageException(f"Failed to retrieve metadata: {str(e)}")

    def secret_exists(self, secret_key: str) -> bool:
        """
        Check if a secret exists in storage.

        Args:
            secret_key: Unique secret identifier

        Returns:
            True if secret exists, False otherwise
        """
        try:
            return self.client.exists(secret_key) > 0
        except redis.RedisError as e:
            raise StorageException(f"Failed to check secret existence: {str(e)}")

    def delete_secret(self, secret_key: str) -> bool:
        """
        Manually delete a secret and its associated data.

        Args:
            secret_key: Unique secret identifier

        Returns:
            True if secret was deleted, False if it didn't exist
        """
        try:
            pipe = self.client.pipeline()
            pipe.delete(secret_key)
            pipe.delete(f"{secret_key}:salt")
            pipe.delete(f"{secret_key}:metadata")
            results = pipe.execute()
            return any(results)
        except redis.RedisError as e:
            raise StorageException(f"Failed to delete secret: {str(e)}")

    def get_ttl(self, secret_key: str) -> int:
        """
        Get the remaining TTL for a secret.

        Args:
            secret_key: Unique secret identifier

        Returns:
            Remaining TTL in seconds, -1 if no expiration, -2 if doesn't exist
        """
        try:
            return self.client.ttl(secret_key)
        except redis.RedisError as e:
            raise StorageException(f"Failed to get TTL: {str(e)}")

    def close(self) -> None:
        """Close the Redis connection."""
        try:
            self.client.close()
            logger.info("Redis connection closed successfully")
        except redis.RedisError as e:
            logger.warning(f"Error closing Redis connection: {str(e)}")
