from commons.config import Config
from boto3.s3.transfer import S3Transfer
import boto3

conf = Config()
access_key = conf.get_config('s3_bucket', 'access_key')
secret_key = conf.get_config('s3_bucket', 'secret_key')
bucket_name = conf.get_config('s3_bucket', 'bucket_name')
filepath = conf.get_config('s3_bucket', 'filepath')

def transfer_to_s3(folder_name):
    client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    transfer = S3Transfer(client)
    #transfer.upload_file(filepath, bucket_name, folder_name + "/" + filename)
    transfer.upload_file(filepath, bucket_name, folder_name + "/")

    return 'toto'