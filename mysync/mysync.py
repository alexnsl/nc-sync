import os
import shutil
import logging

from .owncloud import *
from datetime import datetime
from datetime import timedelta
from typing import List


class MySync:
    url: str = "https://cloud.un-uni.com/"
    directory: str = ""
    cloud_base_path: str = "/Library/"
    client = None
    days_threshold = timedelta(days=14)
    now = datetime.now()
    exclude_items = []
    remove_locally = False

    def __init__(self, url: str = None,
                 days_threshold: int = None,
                 remove_locally: bool = None,
                 log_file: str = None) -> None:
        if url:
            self.url = url
        if days_threshold:
            self.days_threshold = timedelta(days=days_threshold)
        if remove_locally:
            self.remove_locally = remove_locally
        if log_file:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", filename=log_file)
        else:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

        logging.info("Sync initialized with parameters:\n "
                     "cloud_url=%s, \n"
                     "days_threshold=%s, \n"
                     "remove_locally=%s \n",
                     self.url, self.days_threshold, self.remove_locally)

    def connect(self, login=None, password=None):
        try:
            user = login if login else os.environ["NC_LOGIN"]
            passwd = password if password else os.environ["NC_PASS"]
        except KeyError as e:
            logging.exception("Cloud username or password were not provided")
            return
        try:
            client = owncloud.Client(self.url)
            client.login(user, passwd)
            logging.info("Connected to the cloud as \"%s\"", user)
        except Exception as e:
            logging.exception("Cannot connect to NC server: \"%s\"", self.url)
        else:
            self.client = client

    def is_exist_in_cloud(self, name):
        if self.client is None:
            raise Exception("Client does not connected to the cloud")

        try:
            info = self.client.file_info(name)
        except:
            return False
        else:   
            return True

    def sync(self, local_dir: str, remote_dir: str = None, exclude_items: list = None) -> None:
        if self.client is None:
            raise Exception("Client does not connected to the cloud")
        if exclude_items:
            self.exclude_items = exclude_items

        self.directory = local_dir
        remote = self.cloud_base_path if not remote_dir else remote_dir

        for item in self.items_for_upload:
            if self.is_exist_in_cloud(remote + item.name):
                logging.info("Object \"%s\" already exists in the cloud, marking to remove locally", item.name)
                if item.is_file():
                    os.remove(item.path)
                else:
                    shutil.rmtree(item.path)
            else:
                logging.info("Starting upload of \"%s\"...", item.name)
                if item.is_file():
                    self.client.put_file(remote, item.path)
                else:
                    self.client.put_directory(remote, item.path)
                logging.info("Finished upload of \"%s\"", item.name)

    def is_match(self, item):
        if item.name[0] == '.':  # skip hidden objects
            return False

        c_time = datetime.fromtimestamp(item.stat().st_ctime)
        date_threshold = self.now - self.days_threshold

        if date_threshold > c_time:
            if item.name not in self.exclude_items:
                logging.info("To be synced: \"%s\".", item.name)
                return True
            else:
                logging.info("Skipping: \"%s\", object is in exclusion list.", item.name)
                return False
        else:
            logging.info("Skipping: \"%s\", days threshold not exceeded.", item.name)
            return False

    @property
    def items_for_upload(self) -> List:
        if not os.path.isdir(self.directory):
            err = format("Directory '%s' doesn't exist", self.directory)
            raise Exception(err)

        items_for_upload = []

        with os.scandir(self.directory) as items:
            for item in items:
                if self.is_match(item):
                    items_for_upload.append(item)

        return items_for_upload
