import boto3
from .tools import fetch_credentials


class S3Aux():

    def __init__(self, bucket, mode='local'):

        if mode == 's3':
            self.s3 = boto3.resource('s3')

        elif mode == 'local':
            keys = fetch_credentials('aws_mat.json')
            ACCESS_KEY = keys['AWS_ACCESS_KEY_ID']
            SECRET_KEY = keys['AWS_SECRET_ACCESS_KEY']
            self.s3 = boto3.resource('s3',
                                     aws_access_key_id=ACCESS_KEY,
                                     aws_secret_access_key=SECRET_KEY)

        else:
            keys = fetch_credentials('credentials/aws_mat.json', mode=mode)
            ACCESS_KEY = keys['AWS_ACCESS_KEY_ID']
            SECRET_KEY = keys['AWS_SECRET_ACCESS_KEY']
            self.s3 = boto3.resource('s3',
                                     aws_access_key_id=ACCESS_KEY,
                                     aws_secret_access_key=SECRET_KEY)

        self.bucket = bucket
        self.working_folder = ''

    def upload(self, local_file, remote_file=None,public=False):

        if not remote_file:

            remote_file = local_file.split('/')[-1]

        remote_file = self.working_folder + remote_file

        self.s3.Object(self.bucket, remote_file).put(
            Body=open(local_file, 'rb'))

        if public:

            self.make_public(remote_file)

    def download(self, remote_file, local_file=None):

        if not local_file:

            local_file = remote_file.split('/')[-1]

        remote_file = self.working_folder + remote_file

        obj = self.s3.Object(self.bucket, remote_file)
        body = obj.get()['Body'].read()
        f = open(local_file, 'wb')
        f.write(body)
        f.close()

    def make_public(self,remote_file):
        object_acl = self.s3.ObjectAcl(self.bucket,remote_file)
        response = object_acl.put(ACL='public-read')

    def set_working_folder(self, folder):

        if not folder.endswith('/'):

            folder += '/'

        self.working_folder = folder

    def list_files(self, path=None):

        bucket = self.s3.Bucket(self.bucket)

        results = []

        for s3_file in bucket.objects.filter(Prefix=self.working_folder):
            results.append(s3_file.key)

        return results

    def get_modified_date(self, remote_file):
        remote_file = self.working_folder + remote_file
        obj = self.s3.Object(self.bucket, remote_file)
        return obj.last_modified

    def get_file_size(self, remote_file):
        remote_file = self.working_folder + remote_file
        obj = self.s3.Object(self.bucket, remote_file)
        return obj.content_length

    def get_list_objects(self):
        folder_objs = []
        mybucket = self.s3.Bucket(self.bucket)
        for obj in mybucket.objects.filter(Prefix = self.working_folder):
            if obj.key == self.working_folder:
                continue
            else:
                folder_objs.append(obj.key)
        return folder_objs

    def delete_folder(self,folder_path):
        mybucket = self.s3.Bucket(self.bucket)
        if folder_path == '/':
            pass
        else:
            for key in mybucket.objects.filter(Prefix = folder_path):
                key.delete()