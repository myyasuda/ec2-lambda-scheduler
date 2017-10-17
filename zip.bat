@echo off

pip install crontab pytz -t src
powershell "Get-ChildItem -Path .\src | Compress-Archive -DestinationPath ec2-lambda-scheduler.zip"