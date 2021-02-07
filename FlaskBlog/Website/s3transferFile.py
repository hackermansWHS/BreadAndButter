import boto3

path = 'C:/Users/HP/Desktop/'
s3 = boto3.client('s3')
s3.download_file('breaddyandbuttery1','test.png',path + 'client_test.png')