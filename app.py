import pandas as pd
import dash
import dash_core_components as dcc
import dash_table
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from corona_package import covid_plot
from plotly.io import templates
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol

data = pd.read_csv('./data/processed_data.csv')
data.population = data.population.fillna(0).map(int)
last_update = data.date.max()
summary_df = pd.DataFrame(columns=['Country',
                                   'Population',
                                   'Date of first case',
                                   'Date of first death',
                                   'Total cases',
                                   'Total deaths',
                                   'Deaths per million',
                                   'Deaths to cases']).set_index('Country')

summary_df['Population'] = data.groupby('country').population.max()
summary_df['Date of first case'] = data.groupby('country').date.min()
summary_df['Date of first death'] = data[data.deaths > 0].groupby('country').date.min()
summary_df['Total cases'] = data.groupby('country').confirmed.max()
summary_df['Total deaths'] = data.groupby('country').deaths.max()
summary_df['Deaths per million'] = summary_df['Total deaths'] / summary_df['Population'] * 1000000
summary_df['Deaths to cases'] = summary_df['Total deaths'] / summary_df['Total cases']

summary_df = summary_df.sort_values('Total cases', ascending=False).reset_index()
summary_df = summary_df.rename(columns={'country': 'Country'})

ref_countries = [
    'US',
    'UK',
    'Sweden',
    'Turkey',
    'Italy',
    'Spain',
    'France',
    'Germany',
    'China'
]

fig1 = covid_plot.plot_flat_deaths(data=data,
                                   country='Greece',
                                   ref_countries=ref_countries,
                                   num_deaths=3)
fig2 = covid_plot.plot_rate_deaths(data=data,
                                   country='Greece',
                                   ref_countries=ref_countries,
                                   death_rate=0.1)
fig3 = covid_plot.plot_metric_evolution_per_country(data, 'Greece', 'confirmed')
fig4 = covid_plot.plot_metric_evolution_per_country(data, 'Greece', 'deaths')
fig5 = covid_plot.plot_metric_trajectory(data, 'Greece', 'confirmed')
fig6 = covid_plot.plot_metric_trajectory(data, 'Greece', 'deaths')


dark_theme = templates['plotly_dark']._compound_props

fig1['layout']['template'] = dark_theme
fig2['layout']['template'] = dark_theme
fig3['layout']['template'] = dark_theme
fig4['layout']['template'] = dark_theme
fig5['layout']['template'] = dark_theme
fig6['layout']['template'] = dark_theme
country_options = []
for c in data.country.unique().tolist():
    country_options.append(
        {
            'label': c,
            'value': c
        })


def build_table(table_data):
    d_table = dash_table.DataTable(
        id='summary_table',
        data=table_data.to_dict('records'),
        columns=[
            {'name': 'Country', 'id': 'Country', 'type': 'text'},
            {'name': 'Population', 'id': 'Population', 'type': 'numeric',
             'format': Format(group=',')},
            {'name': 'Date of first case', 'id': 'Date of first case', 'type': 'datetime'},
            {'name': 'Date of first death', 'id': 'Date of first death', 'type': 'datetime'},
            {'name': 'Total cases', 'id': 'Total cases', 'type': 'numeric',
             'format': Format(group=',')},
            {'name': 'Total deaths', 'id': 'Total deaths', 'type': 'numeric',
             'format': Format(group=',')},
            {'name': 'Deaths per million', 'id': 'Deaths per million', 'type': 'numeric',
             'format': Format(precision=2, scheme=Scheme.fixed)},
            {'name': 'Deaths to cases', 'id': 'Deaths to cases', 'type': 'numeric',
             'format': FormatTemplate.percentage(1)}
            ],
        sort_action='native',
        style_header={
            'backgroundColor': 'rgb(50, 50, 50)',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        fixed_rows={'headers': True, 'data': 0},
        style_cell={
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white',
            'font_size': '18px',
            'minWidth': '0px',
            'whiteSpace': 'normal',
            'maxWidth': '80px',
            'textAlign': 'center'
        },
        style_table={'overflowX': 'scroll', 'margin-left': '0px',
                     'maxHeight': '300px',
                     'overflowY': 'scroll',
                     'border': '2px lightgrey solid'
                     },
        style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(35, 35, 35)'
                }
        ])
    return d_table


app = dash.Dash('Example', external_stylesheets=[dbc.themes.DARKLY])
app.css.config.serve_locally = False
server = app.server
# Boostrap CSS.
app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})


app.layout = html.Div([
    html.Div([
        html.H1('COVID-19 Dashboard',
                className='twelve columns',
                style={
                    'margin-left': 0,
                    'color': 'white',
                    'textAlign': 'center',
                    'font-size': '55'
                }
                )], className='row'),
    html.Div([
        html.H3('Last Update: ' + last_update,
                className='twelve columns',
                style={
                    'margin-left': 0,
                    'color': 'white',
                    'textAlign': 'center',
                    'font-size': '55'
                }
                )], className='row'),
    html.Div([
        html.Div(
            id='drop_single', children=[
                dcc.Dropdown(
                    id='country_dropdown',
                    options=country_options,
                    placeholder='Select Country...',
                    searchable=True,
                    style={'background-color': '#303030',
                           'height': '50px',
                           'width': '100%',
                           'color': 'white',
                           'font-size': '150%',
                           'font-color': 'white',
                           'margin': '0 auto'})
            ],
            className='six columns',
            style={'margin-bottom': '10px',
                   'margin-left': 'auto',
                   'margin-right': 'auto',
                   'margin-top': '10px'}
        )],
        className='row'),
    html.Div([
        html.Div(
            id='drop_multi', children=[
                dcc.Dropdown(
                    id='reference_dropdown',
                    options=country_options,
                    placeholder='Select Reference Countries...',
                    multi=True,
                    searchable=True,
                    style={'background-color': '#303030',
                           'height': '50px',
                           'width': '100%',
                           'color': 'white',
                           'font-size': '150%',
                           'font-color': 'white',
                           'margin': '0 auto'})
                ],
            className='six columns',
            style={'margin-bottom': '10px',
                   'margin-left': 'auto',
                   'margin-right': 'auto',
                   'margin-top': '10px'}
        )],
        className='row'),
    html.Div([
        html.Div([
            build_table(summary_df)
            ],
            className='12 columns', style={'width': 1600, 'margin': '0 auto'})],
        className='row'),
    html.Div([
        html.Div([
            dcc.Graph(
                id='cases_evolution',
                figure=fig3
            )
            ],
            className='six columns',
            style={
                'margin-left': 0,
                'margin-bottom': 20
            }
        ),
        html.Div([
            dcc.Graph(
                id='deaths_evolution',
            )
            ],
            className='six columns',
            style={
                'margin-left': 0,
                'margin-bottom': 20
            }
        )
        ], className='row'),
    html.Div([
        html.Div([
            dcc.Graph(
                id='trajectory_cases',
                figure=fig5
            )
            ],
            className='six columns',
            style={
                'margin-left': 0,
                'margin-bottom': 20
            }
        ),
        html.Div([
            dcc.Graph(
                id='trajectory_deaths',
                figure=fig6
            )
            ],
            className='six columns',
            style={
                'margin-left': 0,
                'margin-bottom': 20
            }
        )
        ], className='row'),
    html.Div([
        html.Div([
            dcc.Graph(
                id='deaths_growth',
                figure=fig1
            )
            ],
            className='six columns',
            style={
                'margin-left': 0,
                'margin-bottom': 20
            }
        ),
        html.Div([
            dcc.Graph(
                id='deaths_rate',
                figure=fig2
            )
            ],
            className='six columns',
            style={
                'margin-left': 0,
                'margin-bottom': 20
            }
        )
        ], className='row')
    ])

# Updates
# Update Table


@app.callback(
    Output(component_id='summary_table', component_property='data'),
    [Input(component_id='country_dropdown', component_property='value'),
     Input(component_id='reference_dropdown', component_property='value')]
)
def update_table(country_value, reference_values):
    if (country_value is None or len(country_value) < 1) and \
            (reference_values is None or len(reference_values) < 1):
        summary_data = summary_df
    elif reference_values is None:
        summary_data = summary_df[summary_df.Country == country_value].reset_index(drop=True)
    elif country_value is None:
        summary_data = summary_df[summary_df.Country.isin(reference_values)].reset_index(drop=True)
    else:
        summary_countries = [country_value] + reference_values
        summary_data = summary_df[summary_df.Country.isin(summary_countries)].reset_index(drop=True)
    return summary_data.to_dict('records')

# Update Plots


@app.callback(
    Output(component_id='cases_evolution', component_property='figure'),
    [Input(component_id='country_dropdown', component_property='value')]
)
def update_graph(value):
    if value is None:
        value = 'World'
    new_fig = covid_plot.plot_metric_evolution_per_country(data, value, 'confirmed')
    new_fig['layout']['template'] = dark_theme
    return new_fig


@app.callback(
    Output(component_id='deaths_evolution', component_property='figure'),
    [Input(component_id='country_dropdown', component_property='value')]
)
def update_graph(value):
    if value is None:
        value = 'World'
    new_fig = covid_plot.plot_metric_evolution_per_country(data, value, 'deaths')
    new_fig['layout']['template'] = dark_theme
    return new_fig


@app.callback(
    Output(component_id='trajectory_cases', component_property='figure'),
    [Input(component_id='country_dropdown', component_property='value'),
     Input(component_id='reference_dropdown', component_property='value')]
)
def update_graph(country_value, reference_values):
        if country_value is None:
            country_value = 'World'
        new_fig = covid_plot.plot_metric_trajectory(data, country_value, 'confirmed')
        new_fig['layout']['template'] = dark_theme
        if reference_values is None:
            return new_fig
        for ref_country in reference_values:
            ref_fig = covid_plot.plot_metric_trajectory(data, ref_country, 'confirmed')
            new_fig['data'] = new_fig['data'] + ref_fig['data']
        return new_fig


@app.callback(
    Output(component_id='trajectory_deaths', component_property='figure'),
    [Input(component_id='country_dropdown', component_property='value'),
     Input(component_id='reference_dropdown', component_property='value')]
)
def update_graph(country_value, reference_values):
    if country_value is None:
        country_value = 'World'
    new_fig = covid_plot.plot_metric_trajectory(data, country_value, 'deaths')
    new_fig['layout']['template'] = dark_theme
    if reference_values is None:
        return new_fig
    for ref_country in reference_values:
        ref_fig = covid_plot.plot_metric_trajectory(data, ref_country, 'deaths')
        new_fig['data'] = new_fig['data'] + ref_fig['data']
    return new_fig

@app.callback(
    Output(component_id='deaths_growth', component_property='figure'),
    [Input(component_id='country_dropdown', component_property='value'),
     Input(component_id='reference_dropdown', component_property='value')]
)
def update_graph(country_value, reference_values):
    if country_value is None:
        country_value = 'World'
    new_fig = covid_plot.plot_flat_deaths(data=data,
                                          country=country_value,
                                          ref_countries=ref_countries,
                                          num_deaths=3)
    new_fig['layout']['template'] = dark_theme
    if reference_values is None:
        return new_fig
    new_fig = covid_plot.plot_flat_deaths(data=data,
                                          country=country_value,
                                          ref_countries=reference_values,
                                          num_deaths=3)
    new_fig['layout']['template'] = dark_theme
    return new_fig

@app.callback(
    Output(component_id='deaths_rate', component_property='figure'),
    [Input(component_id='country_dropdown', component_property='value'),
     Input(component_id='reference_dropdown', component_property='value')]
)
def update_graph(country_value, reference_values):
    if country_value is None:
        country_value = 'World'
    new_fig = covid_plot.plot_rate_deaths(data=data,
                                          country=country_value,
                                          ref_countries=ref_countries,
                                          death_rate=0.1)
    new_fig['layout']['template'] = dark_theme
    if reference_values is None:
        return new_fig
    new_fig = covid_plot.plot_rate_deaths(data=data,
                                          country=country_value,
                                          ref_countries=reference_values,
                                          death_rate=0.1)
    new_fig['layout']['template'] = dark_theme
    return new_fig


if __name__ == '__main__':
    app.run_server(debug=True)
