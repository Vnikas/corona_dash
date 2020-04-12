import pandas as pd
from datetime import date, timedelta

prefix = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'

first_date = date(2020,1,22)
last_date = date.today()
num_days = (last_date - first_date).days
dates = [(first_date + timedelta(days=d)).strftime(format='%m-%d-%Y') for d in range(num_days)]
urls = [prefix + date + '.csv' for date in dates]

for date in dates:
	url = prefix + date + '.csv'
	try:
		pd.read_csv(url).to_csv('./data/raw_data/' + date + '.csv', index=False)
	except:
		continue

