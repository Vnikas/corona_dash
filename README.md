# COVID-19 Dashboard

## Data 
Data are taken from [here](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports)

## Data preparation
* Download data per date.
* Concatenate data.
* Fix issues with country names.
* Aggregate data per country and date.
* Add additional columns like population per country, world data, moving averages etc.

## Plots
Ideas for plots came from [here](https://www.ft.com/coronavirus-latest) and [here](https://aatishb.com/covidtrends/)

## Tutorials (for MacOS)
1. Git clone.
```bash
$ mkdir ~/corona_dash
$ cd ~/corona_dash
$ git clone https://github.com/Vnikas/corona_dash.git
```
2. Create a virtual environment and install all packages needed.
```bash
$ python3 -m venv corona-env
$ source corona-env/bin/activate
$ pip install -r requirements.txt
```
3. Download and prepare data.
```bash
$ python3 corona_package/download_data.py
$ python3 corona_package/prepare_data.py
```
4. Run the app locally.
```bash
$ python3 app.py
```

You can also visit my deployed app [here](https://vnikas-corona-dash.herokuapp.com/)

