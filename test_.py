from datetime import datetime
import time
import pytz


if __name__ == '__main__':
    while True:
        print('Running')
        print(datetime.now(pytz.timezone('Asia/Kolkata')))
        time.sleep(30)
