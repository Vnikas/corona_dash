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

# Read and data and create a summary dataframe to be used in dash table
data = pd.read_csv('./data/processed_data.csv')
data.population = data.population.fillna(0).map(int)
last_update = data.date.max()
summary_df = pd.DataFrame(columns=['Country / Continent',
                                   'Continent',
                                   'Population',
                                   'Date of first case',
                                   'Date of first death',
                                   'Total cases',
                                   'Total deaths',
                                   'Deaths per million',
                                   'Deaths to cases'])\
    .set_index([
        'Country / Continent', 
        'Continent'])

summary_df['Population'] = data.groupby(['country', 'continent'])\
    .population.max()
summary_df['Date of first case'] = data.groupby(['country', 'continent'])\
    .date.min()
summary_df['Date of first death'] = data[data.deaths > 0].groupby(['country', 'continent'])\
    .date.min()
summary_df['Total cases'] = data.groupby(['country', 'continent']).confirmed.max()
summary_df['Total deaths'] = data.groupby(['country', 'continent']).deaths.max()
summary_df['Deaths per million'] = summary_df['Total deaths'] / summary_df['Population'] * 1000000
summary_df['Deaths to cases'] = summary_df['Total deaths'] / summary_df['Total cases']

summary_df = summary_df.sort_values('Total cases', ascending=False).reset_index()
summary_df = summary_df.rename(columns={'country': 'Country / Continent',
                                        'continent': 'Continent'})

ref_countries = [
    'United States',
    'United Kingdom',
    'Sweden',
    'Turkey',
    'Italy',
    'Spain',
    'Germany',
]

# Setting options for dropdowns
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
            {'name': 'Country / Continent', 'id': 'Country / Continent', 'type': 'text'},
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
            'font_size': '15px',
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

dark_theme = templates['plotly_dark']._compound_props

# Create the app
app = dash.Dash('Example', external_stylesheets=[dbc.themes.DARKLY])
app.css.config.serve_locally = False
server = app.server

# Append Boostrap CSS
# app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})


app.layout = html.Div([
    html.Div([
        html.H1('COVID-19 Dashboard',
                className='twelve columns',
                style={
                    'margin': 'auto',
                    'color': 'white',
                    'textAlign': 'center',
                    # 'font-size': '55'
                }
                )], className='row'),
    html.Div([
        html.H4('Last Update: ' + last_update,
                className='twelve columns',
                style={
                    'margin': 'auto',
                    'color': 'white',
                    'textAlign': 'center',
                }
                )], className='row'),
    html.Div([
        dcc.Markdown(
            """
            The unprocessed data for this dashboard were taken from [here](https://github.com/CSSEGISandData/COVID-19).\n
            The code for the data preparation and the app can be found [here](https://github.com/Vnikas/corona_dash).
            """,
            className='twelve columns',
            style={
                'margin': 'auto',
                'margin-bottom': 0,
                'color': 'lightgrey',
                'textAlign': 'center'
                }
            )], className='row'),
    html.Div([
        html.Div(
            id='drop_single', children=[
                dcc.Dropdown(
                    id='country_dropdown',
                    options=country_options,
                    placeholder='Select Country / Continent...',
                    searchable=True,
                    style={'background-color': '#303030',
                           # 'height': '50px',
                           'width': '100%',
                           'color': 'white',
                           # 'font-size': '150%',
                           'font-color': 'white',
                           'margin': '0 auto'})
            ],
            className='six columns',
            style={'margin-bottom': '10px',
                   'margin-left': 'auto',
                   'margin-right': 'auto',
                   'margin-top': '10px',
                   'width': 800}
        )],
        className='row'),
    html.Div([
        html.Div(
            id='drop_multi', children=[
                dcc.Dropdown(
                    id='reference_dropdown',
                    options=country_options,
                    placeholder='Select Reference Countries / Continents...',
                    multi=True,
                    searchable=True,
                    style={'background-color': '#303030',
                           # 'height': '50px',
                           'width': '100%',
                           'color': 'white',
                           # 'font-size': '150%',
                           'font-color': 'white',
                           'margin': '0 auto'})
                ],
            className='six columns',
            style={'margin-bottom': '10px',
                   'margin-left': 'auto',
                   'margin-right': 'auto',
                   'margin-top': '10px',
                   'width': 800}
        )],
        className='row'),
    html.Div([
        html.Div([
            html.Br(),
            build_table(summary_df),
            html.Br()
            ],
            className='12 columns', style={'width': 1600, 'margin': '0 auto'})],
        className='row'),
    html.Div([
        html.Div(
            children=[
            dbc.Label('Filter table\'s countries based on population or continent',
                style={'margin-left': 10}),
            dcc.RangeSlider(
                id='slider',
                min=0,
                max=1,
                value=[0, 1],
                step=.25,
                marks={
                    0: {'label': '0'},
                    .25: {'label': '1,4M (Q1)'},
                    .50: {'label': '8M (Median)'},
                    .75: {'label': '28M (Q3)'},
                    1: {'label': '1,5B'}
                }
            ),
            dbc.Checklist(
                id='checkbox',
                options=[
                    {'label': 'Africa', 'value': 'Africa'},
                    {'label': 'Asia', 'value': 'Asia'},
                    {'label': 'Europe', 'value': 'Europe'},
                    {'label': 'North America', 'value': 'North America'},
                    {'label': 'Oceania', 'value': 'Oceania'},
                    {'label': 'South America', 'value': 'South America'}
                    ],
                value=['Africa', 'Asia', 'Europe', 'North America',
                    'Oceania', 'South America'],
                inline=True,
                style={
                    'text-align': 'center'
                    },
                switch=True,
                )  
            ],
            className='12 columns', style={
                'width': 800, 
                'margin': '0 auto', 
                'border': '1px lightgrey solid',
                'margin-bottom': 20}
                ),
         ],
        className='row'),
    html.Div([
        html.Div([
            dcc.Graph(
                id='cases_evolution'
            )
            ],
            className='six columns',
            style={
                'margin': '0 auto',
                'margin-bottom': 20,
                'width': '48%',
                'border': '1px lightgrey solid'
            }
        ),
        html.Div([
            dcc.Graph(
                id='deaths_evolution',
            )
            ],
            className='six columns',
            style={
                'margin': '0 auto',
                'margin-bottom': 20,
                'width': '48%',
                'border': '1px lightgrey solid'
            }
        )
        ], className='row'),
    html.Div([
        html.Div([
            dcc.Graph(
                id='trajectory_cases'
            )
            ],
            className='six columns',
            style={
                'margin': 'auto',
                'margin-bottom': 20,
                'width': '48%',
                'border': '1px lightgrey solid'
            }
        ),
        html.Div([
            dcc.Graph(
                id='trajectory_deaths'
            )
            ],
            className='six columns',
            style={
                'margin': 'auto',
                'margin-bottom': 20,
                'width': '48%',
                'border': '1px lightgrey solid'
            }
        )
        ], className='row'),
    html.Div([
        html.Div([
            dcc.Graph(
                id='deaths_growth'
            )
            ],
            className='six columns',
            style={
                'margin': 'auto',
                'margin-bottom': 20,
                'width': '48%',
                'border': '1px lightgrey solid'
            }
        ),
        html.Div([
            dcc.Graph(
                id='deaths_rate'
            )
            ],
            className='six columns',
            style={
                'margin': 'auto',
                'margin-bottom': 20,
                'width': '48%',
                'border': '1px lightgrey solid'
            },

        )
        ], className='row')
    ])

# Updates
# Update Table


@app.callback(
    Output(component_id='summary_table', component_property='data'),
    [Input(component_id='country_dropdown', component_property='value'),
     Input(component_id='reference_dropdown', component_property='value'),
     Input(component_id='slider', component_property='value'),
     Input(component_id='checkbox', component_property='value')]
)
def update_table(
        country_value, 
        reference_values, 
        slider_values,
        checkbox_values):
    # apply population filer
    world_info = summary_df[summary_df['Country / Continent'] == 'World']
    continents = data.continent.unique().tolist()
    from_q = summary_df[(~ summary_df['Country / Continent'].isin(continents)) & 
        (summary_df.Population > 0)].Population\
        .quantile(slider_values[0])
    to_q = summary_df[(summary_df['Country / Continent'] != 'World') & 
        (summary_df.Population > 0)].Population\
        .quantile(slider_values[1])
    summary_df_ = summary_df[(summary_df.Population >= from_q) & 
        (summary_df.Population <= to_q)]
    summary_df_ = summary_df_.append(world_info, ignore_index=True)\
        .sort_values('Total cases', ascending=False).reset_index(drop=True)

    if (country_value is None or len(country_value) < 1) and \
            (reference_values is None or len(reference_values) < 1):
        summary_data = summary_df_
    elif reference_values is None:
        summary_data = summary_df_[summary_df_['Country / Continent'] == country_value].reset_index(drop=True)
    elif country_value is None:
        summary_data = summary_df_[summary_df_['Country / Continent'].isin(reference_values)].reset_index(drop=True)
    else:
        summary_countries = [country_value] + reference_values
        summary_data = summary_df_[summary_df_['Country / Continent'].isin(summary_countries)].reset_index(drop=True) 
    summary_data = summary_data[summary_data['Continent'].isin(checkbox_values + ['World'])]    
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
        new_fig = covid_plot.plot_metric_trajectory(
            data=data, 
            country=country_value, 
            metric='confirmed',
            is_main_country=True)
        new_fig['layout']['template'] = dark_theme
        if reference_values is None:
            return new_fig
        for ref_country in reference_values:
            ref_fig = covid_plot.plot_metric_trajectory(
                data=data, 
                country=ref_country, 
                metric='confirmed',
                is_main_country=False)
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
    new_fig = covid_plot.plot_metric_trajectory(
        data=data, 
        country=country_value, 
        metric='deaths', 
        is_main_country=True)
    new_fig['layout']['template'] = dark_theme
    if reference_values is None:
        return new_fig
    for ref_country in reference_values:
        ref_fig = covid_plot.plot_metric_trajectory(
            data=data, 
            country=ref_country, 
            metric='deaths',
            is_main_country=False)
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
