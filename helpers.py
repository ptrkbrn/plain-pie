import os
import boto3
from botocore.exceptions import NoCredentialsError

ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')


def upload_to_aws(imageString, bucket, fileName):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.put_object(Bucket=bucket, Key=fileName, Body=imageString, ContentDisposition='inline', ContentType='image/jpeg')
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def to_msec(timestamp):
    return ((timestamp.hour * 60 + timestamp.minute) * 60 + timestamp.second) * 1000

