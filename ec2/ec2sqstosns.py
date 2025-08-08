import boto3
import json
import time

SQS_QUEUE_URL = 'https://sqs.ap-southeast2.amazonaws.com/008673239246/tbsm-pizza'
SNS_TOPIC_ARN = 'arn:aws:sns:ap-southeast-2:008673239246:testtbsm'

sqs = boto3.client('sqs', region_name='ap-southeast-2')
sns = boto3.client('sns', region_name='ap-southeast-2')


def poll_and_forward():
    while True:
        print("Polling messages from SQS...")
        response = sqs.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=10, 
        )
        
        messages = response.get('Messages', [])
        if not messages:
            print("No messages in queue. Waiting...")
            time.sleep(5)
            continue
        
        for message in messages:
            try:
                body = json.loads(message['Body'])
                print("Received message:", body)
                
   
                sns_response = sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject='SQS to SNS Alert',
                    Message=json.dumps(body, indent=2)
                )
                print("Published to SNS. MessageId:", sns_response['MessageId'])
                
                
                sqs.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=message['ReceiptHandle']
                )
                print("Deleted message from SQS.")
                
            except Exception as e:
                print("Error processing message:", e)
        
        time.sleep(2)


if __name__ == '__main__':
    poll_and_forward()
