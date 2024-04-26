from keep_alive import keep_alive
switch_flag='off'
keep_alive()
from datetime import *

if __name__ == '__main__':
  while True:
    day_number=datetime.now(pytz.timezone('Asia/Kolkata')).weekday()
    print('Loop Time ', datetime.now(pytz.timezone('Asia/Kolkata')))
    time.sleep(10)
