from pytz import timezone
from datetime import datetime, timedelta
import math

import boto3
from crontab import CronTab

PREFIX_START_TAG = 'scheduler:ec2-start'
PREFIX_STOP_TAG = 'scheduler:ec2-stop'
PREFIX_DELETE_TAG = 'scheduler:ec2-terminate'
DEFAULT_OFFSET_MINUTES = 30


def test(crontab, now):
    cron = CronTab(crontab)
    prevSeconds = math.ceil(cron.previous(now=now))
    nextSeconds = math.ceil(cron.next(now=now))
    from_datetime = now + timedelta(seconds=prevSeconds)
    to_datetime = now + timedelta(seconds=prevSeconds, minutes=DEFAULT_OFFSET_MINUTES)
    return from_datetime < now and now < to_datetime

def lambda_handler(event, context):
    ec2 = boto3.client('ec2', 'ap-northeast-1')
    resp = ec2.describe_instances()
    now = datetime.now(timezone('Asia/Tokyo'))

    start_instances = []
    stop_instances = []
    terminate_instances = []

    for reservation in resp['Reservations']:
        for instance in reservation['Instances']:
            if 'Tags' in instance:
                instance_id = instance['InstanceId']
                for tag in instance['Tags']:
                    if tag['Key'].startswith(PREFIX_START_TAG) and instance_id not in start_instances and test(tag['Value'], now):
                        start_instances.append(instance['InstanceId'])
                    elif tag['Key'].startswith(PREFIX_STOP_TAG) and instance_id not in stop_instances and test(tag['Value'], now):
                        stop_instances.append(instance['InstanceId'])
                    elif tag['Key'].startswith(PREFIX_DELETE_TAG) and instance_id not in terminate_instances and test(tag['Value'], now):
                        terminate_instances.append(instance['InstanceId'])

    if len(start_instances) > 0:
        ec2.start_instances(InstanceIds=start_instances)
        print('Started Instances:' + str(start_instances))
    if len(stop_instances) > 0:
        ec2.stop_instances(InstanceIds=stop_instances)
        print('Stopped Instances:' + str(stop_instances))
    if len(terminate_instances) > 0:
        ec2.terminate_instances(InstanceIds=terminate_instances)
        print('Terminated Instances:' + str(terminate_instances))
