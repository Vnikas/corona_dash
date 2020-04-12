import pandas as pd


def read_data():
    import glob
    path = './data/raw_data'
    all_files = glob.glob(path + "/*.csv")
    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        file_date = filename[-14:-4]
        df['date'] = file_date[-4:] + '-' + file_date[:2] + '-' + file_date[3:5]
        li.append(df)
    return pd.concat(li, axis=0, ignore_index=True, sort=False)


def fix_version_issues(data):
    import numpy as np
    country_regex_mappings = {
        '^.*Azerbaijan.*$': 'Azerbaijan',
        '^.*China.*$': 'China',
        '^.*Korea.*$': 'South Korea',
        '^.*Iran.*$': 'Iran',
        '^.*Hong Kong.*$': 'Hong Kong',
        '^.*Bahamas.*$': 'Bahamas',
        '^.*Czechia.*$': 'Czech Republic',
        '^.*Dominica.*$': 'Dominica',
        '^.*Gambia.*$': 'Gambia',
        '^.*Maca.*$': 'Macao',
        '^.*Ireland.*$': 'Ireland',
        '^.*Moldova.*$': 'Moldova',
        '^.*Congo.*$': 'Congo',
        '^.*Russia.*$': 'Russia',
        '^.*Taiwan.*$': 'Taiwan',
        '^.*United Kingdom.*$': 'UK',
        '^.*Viet Nam.*$': 'VietNam'
    }
    data['date'] = pd.to_datetime(data['date'])
    data['country'] = np.where(data.Country_Region.isna(),
                               data['Country/Region'],
                               data.Country_Region)
    data['deaths'] = data.Deaths.fillna(0).map(int)
    data['confirmed'] = data.Confirmed.fillna(0).map(int)
    data_ = data[['date', 'country', 'confirmed', 'deaths']] \
        .sort_values(['country', 'date']) \
        .reset_index(drop=True)
    data_ = data_.replace(regex=country_regex_mappings)
    return data_


def aggregate_data(data):
    data = data.groupby(['country', data.date]).sum().reset_index()
    world_data = data.groupby('date').sum().reset_index()
    world_data['country'] = 'World'
    data = pd.concat([data, world_data], axis=0).reset_index(drop=True)
    data['daily_deaths'] = data.groupby('country')\
        .deaths.apply(lambda x: x - x.shift(1))\
        .fillna(0)\
        .map(int)
    data['daily_confirmed'] = data.groupby('country') \
        .confirmed.apply(lambda x: x - x.shift(1)) \
        .fillna(0) \
        .map(int)
    return data


def enhance_data(data,
                 moving_period=7):
    populations_df = pd.read_csv('./data/populations_df.csv')
    populations_df = populations_df.append({'country': 'World',
                                            'population': populations_df.population.sum()},
                                           ignore_index=True)
    data = data.merge(populations_df, how='left', on='country')

    data['flat_ma'] = data.groupby('country').daily_deaths\
        .rolling(moving_period)\
        .mean()\
        .reset_index(0, drop=True)
    data['death_rate'] = data.deaths / data.population * 1000000
    return data


if __name__ == '__main__':
    raw_data = read_data()
    fixed_data = fix_version_issues(data=raw_data)
    agg_data = aggregate_data(data=fixed_data)
    data = enhance_data(data=agg_data)
    data.to_csv('./data/processed_data.csv', index=False)

