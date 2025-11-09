"""
This module defines a `StorageUtilsSingleton` class for abstracting storage operations
across different environments (local and AWS S3). It provides a unified interface for
reading and writing images and JSON data. This allows the application to interact with
storage without worrying about the underlying details of the storage environment.

The StorageUtilsSingleton pattern ensures a single instance of `StorageUtilsSingleton`
is created throughout the application. This maintains a consistent state and
configuration for storage operations.

Functions:
- `get_instance()`: Returns the singleton instance of the `StorageUtilsSingleton` class.
- `use_local_environment()`: Configures the instance for local filesystem operations.
- `use_cloud_environment()`: Configures the instance for AWS S3 operations.
- `__init__(local_env)`: Initializes the singleton instance based on the environment.

Usage:

from StorageUtilsSingleton import StorageUtilsSingleton

# Get the singleton instance
storage_utils = StorageUtilsSingleton.get_instance()

# Configure for local environment
storage_utils.use_local_environment()

# Now you can use the storage_utils instance for your operations
# For example, to read an image:
image = storage_utils.read_image('path/to/your/image.jpg')

# Or to write JSON data:
data = {'key': 'value'}
storage_utils.write_json('path/to/your/file.json', data)

# If you want to switch to cloud environment (AWS S3)
storage_utils.use_cloud_environment()

# Now all your operations will be performed in the cloud
# For example, to read an image from S3:
image = storage_utils.read_image('s3://your-bucket/your-image.jpg')

# Or to write JSON data to S3:
data = {'key': 'value'}
storage_utils.write_json('s3://your-bucket/your-file.json', data)

Last Updated: 2024-04-26
"""

import json
import os
import boto3
import cv2
import numpy as np
from src.utils.log import logger

s3 = boto3.client("s3")


# pylint: disable=too-few-public-methods,unused-argument
class StorageUtilsSingleton:
    """."""

    __instance = None

    @staticmethod
    def get_instance():
        """
        This is a function docstring. This function returns
        the instance of the StorageUtilsSingleton class.

        """
        # pylint: disable=invalid-envvar-default
        if StorageUtilsSingleton.__instance is None:
            is_running_env_local = os.getenv("SANDBOX_ENV", default=False)
            logger.info(f"Local execution environment: {is_running_env_local}")
            StorageUtilsSingleton(is_running_env_local)
        return StorageUtilsSingleton.__instance

    # This function is use for reading data from local
    def use_local_environment(self):
        """."""
        self.env = "SANDBOX"
        self.read_image = self.__read_image_from_local
        self.write_image = self.__write_image_to_local
        self.read_json = self.__read_json_from_local
        self.write_json = self.__write_json_to_local
        self.list_objects_in_storage = self.__list_objects_in_local
        self.read_json_from_disc = self.__read_json_from_local

    # This function is use for reading data from Cloud
    def use_cloud_environment(self):
        """."""
        self.env = "AWS"
        self.read_image = self.__read_image_from_s3
        self.write_image = self.__write_image_to_s3
        self.read_json = self.__read_json_from_s3
        self.write_json = self.__write_json_to_s3
        self.list_objects_in_storage = self.__list_objects_in_storage
        self.read_json_from_disc = self.__read_json_from_local

    def __init__(self, local_env):
        """."""
        logger.info(f"Initiating StorageUtilsSingleton, local env = {local_env}")

        if StorageUtilsSingleton.__instance is not None:
            logger.info("Instance already exists.")
        else:
            if local_env is True:
                self.use_local_environment()
            else:
                self.use_cloud_environment()
        StorageUtilsSingleton.__instance = self

    @staticmethod
    def __list_objects_in_local(bucket, path):
        file_list = os.listdir(path)
        return file_list

    @staticmethod
    def __load_into_memory(bucket, path):
        obj = s3.get_object(Bucket=bucket, Key=path)
        data = obj["Body"].read()
        return data

    @staticmethod
    def __read_image_from_s3(image_path, bucket):  # download_image
        logger.info("Reading image from s3")
        image_data = StorageUtilsSingleton.__load_into_memory(
            bucket=bucket, path=image_path
        )
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)   # pylint: disable=no-member
        return image, image_data

    @staticmethod
    def __read_image_from_local(image_path, bucket=""):
        logger.info("Reading image from local")
        image = cv2.imread(image_path)  # pylint: disable=no-member
        _, encoded_image = cv2.imencode(".jpg", image)  # pylint: disable=no-member
        image_data = encoded_image.tobytes()
        return image, image_data

    @staticmethod
    def __write_image_to_s3(data, destination, bucket):  # upload_image_data
        img_data = cv2.imencode(".jpg", data)[1].tobytes()  # pylint: disable=no-member
        s3.put_object(Body=img_data, Bucket=bucket, Key=destination)

    @staticmethod
    def __write_image_to_local(data, destination, bucket=""):
        if not os.path.exists(os.path.dirname(destination)):
            os.mkdir(os.path.dirname(destination))
        cv2.imwrite(destination, data)  # pylint: disable=no-member

    @staticmethod
    def __list_objects_in_storage(bucket, path):
        s3_inner = boto3.resource("s3")
        my_bucket = s3_inner.Bucket(bucket)
        file_list = []
        for bucket_object in my_bucket.objects.filter(Prefix=path):
            file_list.append(bucket_object.key)

        return file_list[1:]

    @staticmethod
    def __read_json_from_s3(path, bucket):
        """
        This returns a python object: list/dictionary
        from the json file stored in s3.
        """
        data = StorageUtilsSingleton.__load_into_memory(bucket=bucket, path=path)
        data = json.loads(data.decode("utf-8"))
        return data

    @staticmethod
    def __read_json_from_local(path, bucket=""):
        # data = json.loads(open(path).read())
        with open(path, encoding="utf8") as fp:
            data = json.load(fp)
        return data

    @staticmethod
    def __write_json_to_s3(data, path, bucket):
        data_serial = json.dumps(data).encode("utf-8")
        s3.put_object(Body=data_serial, Bucket=bucket, Key=path)

    @staticmethod
    def __write_json_to_local(data, path, bucket=""):
        with open(path, "w", encoding='utf-8') as fp:
            json.dump(data, fp)
