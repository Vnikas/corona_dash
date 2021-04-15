import pandas as pd
from datetime import date, timedelta
import pathlib

# Create the directory needed to save the raw data, if not already there.
pathlib.Path('./data/raw_data/').mkdir(exist_ok=True)

prefix = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'

last_date = date.today()
first_date = last_date - timedelta(days=30) # the actual first date of data is 2020-01-22 but we only udtate the 30 last days

num_days = (last_date - first_date).days
dates = [(first_date + timedelta(days=d)).strftime(format='%m-%d-%Y') for d in range(num_days)]
urls = [prefix + date + '.csv' for date in dates]
max_date = date(1900,1,1)

for date in dates:
	url = prefix + date + '.csv'
	try:
		pd.read_csv(url).to_csv('./data/raw_data/' + date + '.csv', index=False)
		max_date = date
	except:
		continue	

print('Downloaded data until: ', max_date)

