import json
import os
import boto3


def fetch_credentials(filename, mode='local',
                      bucket=None, credentials=None, remote_keys=None):

    if mode not in ['s3', 'local']:
        raise Exception('Unknown mode')

    if mode == 'local':

        credentials_folder = os.environ['CREDENTIALS_HOME']
        f = open('{}/{}'.format(credentials_folder, filename), 'r')
        filedata = f.read()
        f.close()

        filetype = filename.split('.')[-1]
        if filetype == 'json':
            return json.loads(filedata)

    else:

        if not bucket:
            raise Exception('Bucket name required for remote access')

        if remote_keys:

            ACCESS_KEY = remote_keys['AWS_ACCESS_KEY_ID']
            SECRET_KEY = remote_keys['AWS_SECRET_ACCESS_KEY']

            s3 = boto3.resource('s3',
                                aws_access_key_id=ACCESS_KEY,
                                aws_secret_access_key=SECRET_KEY)
        else:

            s3 = boto3.resource('s3')

        obj = s3.Object(bucket, filename)
        body = obj.get()['Body'].read()

        filetype = filename.split('.')[-1]
        if filetype == 'json':
            return json.loads(body)
