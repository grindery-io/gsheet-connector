from crontab import CronTab
from datetime import datetime


# def write_date_time():
print('----crated---cron---job----')
# myFile = open('append.txt', 'a')
# myFile.write('\nAccessed on ' + str(datetime.now()))

with open('append.txt', 'a') as outFile:
    outFile.write('\nAccessed' + str(datetime.now()))
