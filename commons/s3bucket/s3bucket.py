from commons.config import Config
from boto3.s3.transfer import S3Transfer
import boto3
import os
import utils
import logging

conf = Config()
access_key = conf.get_config('s3_bucket', 'access_key')
secret_key = conf.get_config('s3_bucket', 'secret_key')
bucket_name = conf.get_config('s3_bucket', 'bucket_name')

client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
transfer = S3Transfer(client)

def transfer_folder_content_to_s3(local_path, s3_path):
    logging.warning("transfer_folder_content_to_s3 - start")
    logging.warning('os.getcwd - ' + os.getcwd())
    logging.warning('local_path - ' + local_path)
    dir = utils.get_path_for_system_spe(os.getcwd(), local_path)
    os.chdir(dir)
    for root, dirs, files in os.walk(".", topdown=False):
        for local_filename in files:
            transfer_file_to_s3(local_filename, s3_path)
    logging.warning("transfer_folder_content_to_s3 - end")

def transfer_file_to_s3(local_filename, s3_path):
    transfer.upload_file(local_filename, bucket_name, s3_path + '/' + local_filename)