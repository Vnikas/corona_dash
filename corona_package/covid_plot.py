def plot_metric_evolution_per_country(data, country, metric):
    if metric == 'confirmed':
        total_metric_text = 'Total Cases'
        new_metric_text = 'New Cases'
        title_text = 'Confirmed Cases'
    else:
        total_metric_text = 'Total Deaths'
        new_metric_text = 'New Deaths'
        title_text = 'Confirmed Deaths'
    metric_col = metric
    daily_metric_col = 'daily_' + metric

    df_ = data[data.country == country].reset_index(drop=True)
    df_['total_hovertexts'] = 'Country: ' + \
                              df_.country + \
                              '<br>' + \
                              'Date: ' + \
                              df_.date + \
                              '<br>' + \
                              total_metric_text + \
                              ': ' + \
                              df_[metric_col].map(str)
    df_['new_hovertexts'] = 'Country: ' + \
                            df_.country + \
                            '<br>' + \
                            'Date: ' + \
                            df_.date + \
                            '<br>' + \
                            new_metric_text + \
                            ': ' + \
                            df_[daily_metric_col].map(str)

    upper_range = int(df_[daily_metric_col].max() * 1.8)
    fig = {
        'data': [
            {
                'x': df_.date,
                'y': df_[metric_col],
                'mode': 'markers+lines',
                'name': total_metric_text,
                'marker': {'size': 8},
                'hoverinfo': 'text',
                'hovertext': df_['total_hovertexts']
            },
            {
                'x': df_.date,
                'y': df_[daily_metric_col],
                'name': new_metric_text,
                'type': 'bar',
                'yaxis': 'y2',
                'hoverinfo': 'text',
                'hovertext': df_['new_hovertexts'],
                'marker': {
                    'color': 'darkorange'
                }
            }
        ],
        'layout': {
            'title': '<b>' + title_text + ' in ' + country + '</b>',
            'barmode': 'overlay',
            'yaxis2': {
                'side': 'right',
                'overlaying': 'y',
                'showgrid': False,
                'range': [0, upper_range]
            },
            'legend': {
                'x': 1,
                'y': 1.1,
                'traceorder': 'normal',
                'font': {
                  'family': 'sans-serif',
                  'size': 12
                },
                'bgcolor': None,
                'bordercolor': '#FFFFFF',
                'borderwidth': 1
              } 
        }
    }
    return fig


def plot_metric_trajectory(data, country, metric, is_main_country):
    if metric == 'confirmed':
        total_metric_text = 'Total Confirmed Cases'
        weekly_metric_text = 'Weekly Confirmed Cases'
        title_text = 'confirmed cases'
    else:
        total_metric_text = 'Total Confirmed Deaths'
        weekly_metric_text = 'New Confirmed Deaths'
        title_text = 'confirmed deaths'
    metric_col = metric
    weekly_metric_col = 'weekly_' + metric
    daily_metric_col = 'daily_' + metric

    df_ = data[data.country == country].reset_index(drop=True).sort_values('date')

    df_[weekly_metric_col] = df_[daily_metric_col].rolling(7).sum()
    upper_range = int(df_[metric_col].max() * 2)
    df_['hovertexts'] = 'Country: ' + \
                         df_.country + \
                        '<br>' + \
                        'Date: ' + \
                         df_.date + \
                         '<br>' + \
                         total_metric_text + \
                         ': ' + \
                         df_[metric_col].map(str) + \
                         '<br>' + \
                         weekly_metric_text + \
                         ': ' + \
                         df_[weekly_metric_col].map(str)
    if is_main_country:
        marker_size = 6
        line_width = 3
        label_line_width = 3
        label_marker_size = 8
    else:
        marker_size = 4
        line_width = 1,
        label_line_width = 2
        label_marker_size = 6


    fig = {
        'data': [
            {
                'x': df_[metric_col],
                'y': df_[weekly_metric_col],
                'mode': 'lines+markers',
                'marker': {'size': marker_size},
                'line': {
                        'width': line_width
                        },
                'hoverinfo': 'text',
                'hovertext': df_['hovertexts']
            }
        ] + [
            {
                'x': df_[metric_col].tail(1),
                'y': df_[weekly_metric_col].tail(1),
                'text': country,
                'textposition': 'middle right',
                'mode': 'markers+text',
                'marker': {
                    'size': label_marker_size,
                    'line': {
                        'width': label_line_width,
                        'color': 'white',
                    },
                    'color': 'grey'
                },
                'hoverinfo': 'none'
            }
        ],
        'layout': {
            'title': '<b>Trajectory of ' + title_text,
            'yaxis': {
                'title': weekly_metric_text + ' (in Past Week)',
                'type': 'log'
            },
            'xaxis': {
                'title': total_metric_text,
                'type': 'log',
                #'range': [0, np.log10(upper_range)]
            },
            'showlegend': False

        }
    }
    return fig


def plot_flat_deaths(data,
                     ref_countries,
                     country,
                     num_deaths):
    rest_countries = list(set(data.country.unique().tolist()) - set(ref_countries + [country]))

    flat_data = data[data.deaths >= num_deaths].reset_index(0, drop=True)

    flat_data['days_since'] = flat_data.groupby('country').deaths\
        .cumcount()\
        .reset_index(0, drop=True)

    flat_data['flat_hovertexts'] = 'Country: ' + \
                                   flat_data.country + \
                                   '<br>Deaths: ' + \
                                   flat_data.flat_ma.round(2).map(str) + \
                                   '<br>Days: ' + \
                                   flat_data.days_since.map(str)

    country_flat_data = flat_data[flat_data.country == country].reset_index(drop=True)

    fig = {
        'data': [
                    {
                        'x': flat_data[flat_data.country == c].days_since,
                        'y': flat_data[flat_data.country == c].flat_ma,
                        'mode': 'lines',
                        'line': {
                            'shape': 'spline',
                            'smoothing': 1.3
                        },
                        'marker': {
                            'color': '#565656'
                        },
                        'hoverinfo': 'none'
                    } for c in rest_countries
                ] + [
                    {
                        'x': flat_data[flat_data.country == c].days_since,
                        'y': flat_data[flat_data.country == c].flat_ma,
                        'mode': 'lines',
                        'line': {
                            'shape': 'spline',
                            'smoothing': 1.3
                        },
                        'name': c,
                        'marker': {
                            # 'color': 'lightgrey'
                        },
                        'hoverinfo': 'text',
                        'hovertext': flat_data[flat_data.country == c]['flat_hovertexts'],
                    } for c in ref_countries
                ] + [
                    {
                        'x': flat_data[flat_data.country == c].days_since.tail(1),
                        'y': flat_data[flat_data.country == c].flat_ma.tail(1),
                        'text': c,
                        'textposition': 'middle right',
                        'mode': 'markers+text',
                        'marker': {
                            'size': 6,
                            'line': {
                                'width': 1,
                                'color': 'white',
                            },
                            'color': 'grey'
                        },
                        'hoverinfo': 'none'
                    } for c in ref_countries
                ] + [
                    {
                        'x': country_flat_data.days_since,
                        'y': country_flat_data.flat_ma,
                        'mode': 'lines',
                        'line': {
                            'shape': 'spline',
                            'smoothing': 1.3,
                            'width': 4
                        },
                        'name': 'Greece',
                        'marker': {
                            'color': 'white'
                        },
                        'hoverinfo': 'text',
                        'hovertext': country_flat_data['flat_hovertexts'],
                    },
                    {
                        'x': country_flat_data.days_since.tail(1),
                        'y': country_flat_data.flat_ma.tail(1),
                        'mode': 'markers+text',
                        'text': country,
                        'textposition': 'middle right',
                        'marker': {
                            'size': 8,
                            'line': {
                                'width': 2,
                                'color': 'white',
                            },
                            'color': 'grey'
                        },
                        'hoverinfo': 'none'
                    }],
        'layout': {
            'title': '<b>Daily deaths in ' + country + '</b>',
            'showlegend': False,
            'yaxis': {
                'title': 'Deaths (7-day moving average)',
                'type': 'log'
            },
            'xaxis': {
                'title': 'Number of days since ' + str(num_deaths) + ' daily deaths first recorded'
            },
            'hoverlabel': {
                'bgcolor': 'white',
                'font_size': 12,
            },
            'template': 'plotly_dark',
            'height': 600
        }
    }
    #iplot(fig)
    #plot(fig, filename='../docs/deaths_plot.html')
    return fig


def plot_rate_deaths(data,
                     country,
                     ref_countries,
                     death_rate):
    rest_countries = list(set(data.country.unique().tolist()) - set(ref_countries + [country]))

    rate_data = data[data.death_rate >= death_rate].reset_index(0, drop=True)

    rate_data['days_since'] = rate_data.groupby('country').deaths \
        .cumcount() \
        .reset_index(0, drop=True)

    rate_data['rate_hovertexts'] = 'Country: ' + \
                                   rate_data.country + \
                                   '<br>Death rate: ' + \
                                   rate_data.death_rate.round(2).map(str) + \
                                   '<br>Days: ' + \
                                   rate_data.days_since.map(str)
    country_rate_data = rate_data[rate_data.country == country].reset_index(drop=True)

    fig = {
        'data': [
                    {
                        'x': rate_data[rate_data.country == c].days_since,
                        'y': rate_data[rate_data.country == c].death_rate,
                        'mode': 'lines',
                        'line': {
                            'shape': 'spline',
                            'smoothing': 1.3
                        },
                        'marker': {
                            'color': '#565656'
                        },
                        'hoverinfo': 'none'
                    } for c in rest_countries
                ] + [
                    {
                        'x': rate_data[rate_data.country == c].days_since,
                        'y': rate_data[rate_data.country == c].death_rate,
                        'mode': 'lines',
                        'line': {
                            'shape': 'spline',
                            'smoothing': 1.3
                        },
                        'name': c,
                        'marker': {
                            # 'color': 'lightgrey'
                        },
                        'hoverinfo': 'text',
                        'hovertext': rate_data[rate_data.country == c]['rate_hovertexts'],
                    } for c in ref_countries
                ] + [
                    {
                        'x': rate_data[rate_data.country == c].days_since.tail(1),
                        'y': rate_data[rate_data.country == c].death_rate.tail(1),
                        'text': c,
                        'textposition': 'middle right',
                        'mode': 'markers+text',
                        'marker': {
                            'size': 6,
                            'line': {
                                'width': 1,
                                'color': 'white',
                            },
                            'color': 'grey'
                        },
                        'hoverinfo': 'none'
                    } for c in ref_countries
                ] + [
                    {
                        'x': country_rate_data.days_since,
                        'y': country_rate_data.death_rate,
                        'mode': 'lines',
                        'line': {
                            'shape': 'spline',
                            'smoothing': 1.3,
                            'width': 4
                        },
                        'name': country,
                        'marker': {
                            'color': 'white'
                        },
                        'hoverinfo': 'text',
                        'hovertext': country_rate_data['rate_hovertexts'],
                    },
                    {
                        'x': country_rate_data.days_since.tail(1),
                        'y': country_rate_data.death_rate.tail(1),
                        'mode': 'markers+text',
                        'text': country,
                        'textposition': 'middle right',
                        'marker': {
                            'size': 8,
                            'line': {
                                'width': 2,
                                'color': 'white',
                            },
                            'color': 'grey'
                        },
                        'hoverinfo': 'none'
                    }],
        'layout': {
            'title': '<b>Daily death rate in ' + country +'</b>',
            'showlegend': False,
            'yaxis': {
                'title': 'Death Rate (total deaths per million)',
                'type': 'log'
            },
            'xaxis': {
                'title': 'Days since total deaths reached ' + str(death_rate) + ' per million'
            },
            'hoverlabel': {
                'bgcolor': 'white',
                'font_size': 12,
            },
            'template': 'plotly_dark',
            'height': 600
        }
    }
    #iplot(fig)
    #plot(fig, filename='../docs/deaths_plot.html')
    return fig


if __name__ == '__main__':
    print('Done')
