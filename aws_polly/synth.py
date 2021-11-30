import json
import os
import urllib.parse
import boto3

print('Loading function')

s3 = boto3.client('s3')
polly = boto3.client('polly')


def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    # parameters for the polly call
    textType = 'text'
    if key.split('.')[1] == 'xml':
        textType = 'ssml'

    try:
        text_event = s3.get_object(Bucket=bucket, Key=key)
        text = text_event['Body'].read().decode('utf-8')

        response = polly.start_speech_synthesis_task(VoiceId=os.environ['VOICE_ID'],
                                                     Engine='neural',
                                                     OutputS3BucketName=os.environ['TARGET_BUCKET'],
                                                     SnsTopicArn=os.environ['TARGET_TOPIC'],
                                                     OutputFormat='mp3',
                                                     TextType=textType,
                                                     Text=text)

        taskId = response['SynthesisTask']['TaskId']
        # print(taskId)

        #task_status = polly.get_speech_synthesis_task(TaskId=taskId)
        # print(task_status)

        return taskId

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
