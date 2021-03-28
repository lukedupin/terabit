from django.conf import settings

from botocore.client import Config
from botocore.exceptions import NoCredentialsError

from website.helpers import util
import os, boto3


def url( url ):
    return "https://%s.%s.%s/%s" % (settings.S3_ACCESS['BUCKET'],
                                    settings.S3_ACCESS['REGION'],
                                    settings.S3_ACCESS['HOST'],
                                    url)


def put_data(data, s3_file, bucket=None):
    # Default bucket
    if bucket is None:
        bucket = settings.S3_ACCESS['BUCKET']

    # Dev code
    if 'MODE' in settings.S3_ACCESS and settings.S3_ACCESS['MODE'] == 'DEV':
        endpoint = "https://%s.%s" % (settings.S3_ACCESS['REGION'], settings.S3_ACCESS['HOST'])

        # Initialize a session using DigitalOcean Spaces.
        session = boto3.session.Session()
        client = session.client('s3',
                                region_name=settings.S3_ACCESS['REGION'],
                                endpoint_url=endpoint,
                                aws_access_key_id=settings.S3_ACCESS['ACCESS_KEY'],
                                aws_secret_access_key=settings.S3_ACCESS['SECRET_KEY'])

    # Production
    else:
        client = boto3.client("s3")

    try:
        args = { "Bucket": bucket, "Key": s3_file, "Body": data }
        if 'EXTRA_ARGS' in settings.S3_ACCESS and util.xstr(settings.S3_ACCESS['EXTRA_ARGS']) != "":
            args["ACL"] = settings.S3_ACCESS['EXTRA_ARGS']
        client.put_object( **args )

    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

    return True


def upload_file(local_file, s3_file, bucket=None):
    raise Exception("Deprecated Function")
    # # Default bucket
    # if bucket is None:
    #     bucket = settings.S3_ACCESS['BUCKET']

    # # Server endpoint
    # endpoint = "https://%s.%s" % (settings.S3_ACCESS['REGION'], settings.S3_ACCESS['HOST'])

    # # Initialize a session using DigitalOcean Spaces.
    # session = boto3.session.Session()
    # client = session.client('s3',
    #                         region_name=settings.S3_ACCESS['REGION'],
    #                         endpoint_url=endpoint,
    #                         aws_access_key_id=settings.S3_ACCESS['ACCESS_KEY'],
    #                         aws_secret_access_key=settings.S3_ACCESS['SECRET_KEY'])

    # try:
    #     client.upload_file(local_file, bucket, s3_file,
    #                        settings.S3_ACCESS['EXTRA_ARGS'] )

    # except FileNotFoundError:
    #     print("The file was not found")
    #     return False
    # except NoCredentialsError:
    #     print("Credentials not available")
    #     return False

    # return True
    

def read_permissions(bucket=None):
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.S3_ACCESS['ACCESS_KEY'],
                      aws_secret_access_key=settings.S3_ACCESS['SECRET_KEY'],
                      )

    # Default bucket
    if bucket is None:
        bucket = settings.S3_ACCESS['BUCKET']

    try:
        return s3.get_bucket_acl(Bucket=bucket)

    except NoCredentialsError:
        print("Credentials not available")
        return None
