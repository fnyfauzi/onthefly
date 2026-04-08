from datetime import datetime
import calendar, pytz, time

def shanghai_time():
	tz = pytz.timezone('Asia/Shanghai')
	return datetime.now(tz)

def get_date():
	t = shanghai_time()
	year = str(t.year)
	mon = str(t.month).zfill(2)
	day = str(t.day).zfill(2)
	hour = str(t.hour).zfill(2)
	minute = str(t.minute).zfill(2)
	sec = str(t.second).zfill(2)
	msec = str(t.microsecond)
	return t, year, mon, day, hour, minute, sec, msec
	# 2020 12 21 21 13 37 10 716745

def to_timestamp(t):
	# t = shanghai_time()
	# ts = int( to_timestamp(t) )
	return round(calendar.timegm(t.timetuple()))

def time_to_string(t):
    return t.strftime('%Y%m%d_%H%M%S')

def extract_time(t):
	""" t = shanghai_time() """
	year = str(t.year)
	mon = str(t.month).zfill(2)
	day = str(t.day).zfill(2)
	hour = str(t.hour).zfill(2)
	minute = str(t.minute).zfill(2)
	sec = str(t.second).zfill(2)
	msec = str(t.microsecond)
	return year, mon, day, hour, minute, sec, msec



if __name__ == '__main__':

	# ---------------------------
	# t = shanghai_time()
	# print(t.year, t.month, t.day, t.day, t.hour, t.minute, t.second, t.microsecond)

	# ---------------------------

	t = shanghai_time()
	ts = int( to_timestamp(t) )
	print(ts)

	time.sleep(2)

	t = shanghai_time()
	ts_now = int( to_timestamp(t) )
	print(ts_now)
	print('diff: {}'.format(ts_now-ts))

	t = shanghai_time()
	print(time_to_string(t))
