from datetime import datetime, timedelta
import math
import logging

from pytz import timezone
import boto3
from crontab import CronTab

PREFIX_START_TAG = 'scheduler:ec2-start'
PREFIX_STOP_TAG = 'scheduler:ec2-stop'
PREFIX_DELETE_TAG = 'scheduler:ec2-terminate'
DEFAULT_OFFSET_MINUTES = 30
DEFAULT_TIMEZONE = 'Asia/Tokyo'

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def is_target(crontab, now):
    cron = CronTab(crontab)
    prev_seconds = math.ceil(cron.previous(now=now))
    from_datetime = now + timedelta(seconds=prev_seconds)
    to_datetime = now + timedelta(seconds=prev_seconds, minutes=DEFAULT_OFFSET_MINUTES)
    return from_datetime < now and now < to_datetime

def lambda_handler(event, context):

    ec2 = boto3.client('ec2', 'ap-northeast-1')
    resp = ec2.describe_instances()

    start_instances = []
    stop_instances = []
    terminate_instances = []

    now = datetime.now(timezone(DEFAULT_TIMEZONE))

    for reservation in resp['Reservations']:
        for instance in reservation['Instances']:
            if 'Tags' in instance:
                instance_id = instance['InstanceId']
                for tag in instance['Tags']:
                    try:
                        key = tag['Key']
                        value = tag['Value']
                        if key.startswith(PREFIX_START_TAG) and instance_id not in start_instances and is_target(value, now):
                            start_instances.append(instance_id)
                        elif key.startswith(PREFIX_STOP_TAG) and instance_id not in stop_instances and is_target(value, now):
                            stop_instances.append(instance_id)
                        elif key.startswith(PREFIX_DELETE_TAG) and instance_id not in terminate_instances and is_target(value, now):
                            terminate_instances.append(instance_id)
                    except ValueError as err:
                        LOGGER.error('ValueError: {}, instance_id={}'.format(err, instance_id))

    if len(start_instances) > 0:
        ec2.start_instances(InstanceIds=start_instances)
        LOGGER.info('Started Instances:' + str(start_instances))
    else:
        LOGGER.info('Started Instances: None')

    if len(stop_instances) > 0:
        ec2.stop_instances(InstanceIds=stop_instances)
        LOGGER.info('Stopped Instances:' + str(stop_instances))
    else:
        LOGGER.info('Stopped Instances: None')

    if len(terminate_instances) > 0:
        ec2.terminate_instances(InstanceIds=terminate_instances)
        LOGGER.info('Terminated Instances:' + str(terminate_instances))
    else:
        LOGGER.info('Terminated Instances: None')
