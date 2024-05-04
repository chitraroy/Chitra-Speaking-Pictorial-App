import boto3


class StorageService:
    def __init__(self, storage_location):
        self.client = boto3.client('s3')
        self.bucket_name = storage_location

    def get_storage_location(self):
        return self.bucket_name


    def upload_file(self, file_bytes, file_name):
        self.client.put_object(Bucket = self.bucket_name,
                               Body = file_bytes,
                               Key = file_name,
                            #    ACL = 'public-read'
                               )

        return {'fileId': file_name,
                'fileUrl': "http://" + self.bucket_name + ".s3.amazonaws.com/" + file_name}
        
    def upload_mp3(self, local_path, file_name):
        self.client.upload_file(local_path, self.bucket_name, file_name)

        return {'fileId': file_name,
                'fileUrl': "http://" + self.bucket_name + ".s3.amazonaws.com/" + file_name}

    def list_files(self):
        response = self.client.list_objects_v2(Bucket = self.bucket_name)

        files = []
        for content in response['Contents']:
            files.append({
                'location': self.bucket_name,
                'file_name': content['Key'],
                'url': "http://" + self.bucket_name + ".s3.amazonaws.com/"
                       + content['Key']
            })
        return files
