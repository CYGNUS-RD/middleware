#! /usr/bin/env python3
def get_s3_client(client_id, client_secret, endpoint_url, session_token):
    # Specify the session token, access key, and secret key received from the STS
    import boto3
    sts_client = boto3.client('sts',
            endpoint_url = endpoint_url,
            region_name  = ''
            )

    response_sts = sts_client.assume_role_with_web_identity(
            RoleArn          = "arn:aws:iam:::role/S3AccessIAM200",
            RoleSessionName  = 'cygno',
            DurationSeconds  = 3600,
            WebIdentityToken = session_token # qua ci va il token IAM
            )

    s3 = boto3.client('s3',
            aws_access_key_id     = response_sts['Credentials']['AccessKeyId'],
            aws_secret_access_key = response_sts['Credentials']['SecretAccessKey'],
            aws_session_token     = response_sts['Credentials']['SessionToken'],
            endpoint_url          = endpoint_url,
            region_name           = '')
    return s3
def main():
    import boto3
    from boto3sts import credentials as creds
    import os
    client_id     = os.environ['IAM_CLIENT_ID']
    client_secret = os.environ['IAM_CLIENT_SECRET']
    endpoint_url  = os.environ['ENDPOINT_URL']
    # read with sts
    # aws_session = creds.assumed_session("infncloud-wlcg")
    # s3 = aws_session.client('s3', endpoint_url="https://minio.cloud.infn.it/",
    #                         config=boto3.session.Config(signature_version='s3v4'),verify=True)
    # rear with HTML token
    with open('/tmp/token') as file:
        s3_token = file.readline().strip('\n')
        
    s3 = get_s3_client(client_id, client_secret, endpoint_url, s3_token)
    filedata='run39297.mid.gz'
    bucket = 'cygno-data'
    key = "LNGS/"
    
    # LIST
    response = s3.list_objects(Bucket='cygno-data')['Contents']
    for i, file in enumerate(response):
        print(file['Key'], file['LastModified'])
    
    # SIZE OBJECT
    response = s3.head_object(Bucket=bucket,Key=key+filedata)['ContentLength']
    print(response)
    # DOWNLOAD
    # response = s3.download_file(Bucket=bucket, Key=key+filedata, Filename="/tmp/prova.dat")
    # print(response)
    
main()