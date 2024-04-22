# %%
# importing dependencies
from dash import Dash, dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# %%
# read in and view dataframe
df = pd.read_csv("data.csv")
df.head()

# %%
# load the CSS stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# %%
# initialize the app
app = Dash(__name__, external_stylesheets=stylesheets)
server = app.server

# %%
# Creating layout
app.layout = html.Div(
    style={'backgroundColor': '#212529'},  # Setting background color 
    children=[  # Creating the layout with headings with appropriate styling/colors 
        html.Div(
            [
                html.H4("Carbon Dioxide (CO2) Emissions By Year", style={'color': '#FFFFFF', 'margin': '15px', 'padding-top': '15px'}),
                html.H5("Track carbon dioxide (CO2) emissions for the chosen year from 1990 to 2022 and its most significant contributors.", style={'color': '#FFFFFF', 'margin': '15px'})
            ]
        ),
        html.Div( #dropdown with styling
            [
                html.Label('Select Year', style={'color': '#FFFFFF', 'margin-right': '15px'}),
                dcc.Dropdown(  # Creating dropdown for the years with a preset value and taking unique value from data
                    options=[{'label': year, 'value': year} for year in df['year'].unique()],
                    id='year-dropdown',
                    value=1996,  # Preset year; not a multi-select dropdown
                    multi=False,
                    style={'width': '600px'}
                )
            ],
            style={'display': 'inline-block', 'margin-top': '15px', 'margin-bottom': '15px', 'padding-left': '15px', 'padding-right': '15px'}
        ),
        html.Div( #Creating a UI component for the world map graph with appropriate styling and colors while adjusting margins; users can pick which data type they would like to see
            [
                html.Label('Select Data Type for the World Map', style={'color': '#FFFFFF'}),
                dcc.RadioItems(
                    id='data-type-radio',
                    options=[ #The 2 options
                        {'label': 'Total', 'value': 'total'},
                        {'label': 'Per Capita', 'value': 'per_capita'}
                    ],
                    value='total',  # Preset to total
                    labelStyle={'color': '#FFFFFF'},
                    style={'margin-right': '80px'}
                ),
            ],
            style={'margin-top': '15px', 'margin-bottom': '30px', 'padding-left': '15px', 'padding-right': '15px'}
        ),
        html.Div(  # World map taking up half of the page width and colors
            dcc.Graph(id='world-map'),
            style={'width': '100%', 'height': '50%', 'display': 'inline-block', 'backgroundColor': '#212529'}
        ),
        html.Div(  #Graphs with appropriate styling and colors and setting them to half the page side by side
            [
                dcc.Graph(id='bar-chart'), # Grouped bar chart for CO2 emissions

                dcc.Graph(id='area-chart'), # Line area chart for CO2 emissions
            ],
            style={'width': '50%', 'height': '100%', 'display': 'flex', 'backgroundColor': '#212529', 'vertical-align': 'top'}
        ),
    ]
)
# Define callback for world map/update graph function
@app.callback(
    Output('world-map', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('data-type-radio', 'value')]
)
def update_world_map(selected_year, data_type):
    filtered_df = df[df['year'] == selected_year]

    if data_type == 'total':  # Creating an if/else statement that coincides for the radio button based on selected dataset for the colors based on the selected year
        color_column = 'total'
        title = f'Total CO2 Emissions by Country in {selected_year}'
        colorbar_title = 'CO2 Emissions (Metric Tons)'
    else:
        color_column = 'per_capita'
        title = f'CO2 Emissions Per Capita by Country in {selected_year}'
        colorbar_title = 'CO2 Emissions Per Capita'

    fig = px.choropleth(filtered_df,  # Making the graph using the country names to map to the country, what column maps to the color of the countries and the styling components
                        locations='country',
                        locationmode='country names',
                        color=color_column,
                        hover_name='country',
                        title=title,
                        color_continuous_scale='Viridis')
    fig.update_coloraxes(colorbar=dict(tickformat='.2f', title=colorbar_title))
    fig.update_layout(
        plot_bgcolor='#212529',
        paper_bgcolor='#212529',
        font=dict(color='#FFFFFF')
    )

    return fig  # Return figure

# Define callback for grouped bar chart/update graph function
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_grouped_bar_chart(selected_year):
    filtered_df = df[df['year'] == selected_year]

    top_10_countries = filtered_df.groupby('country')['total'].sum().nlargest(10).index  # Select top 10 emitting countries

    trace_data = []  # Making an empty list to store trace data

    emission_types = ['coal', 'oil', 'gas']  # Column names for each emission type

    for country in top_10_countries:  # Creating a for loop to iterate the values for the top 10
        country_data = filtered_df[filtered_df['country'] == country]
        emissions = [country_data[emission_type].values[0] for emission_type in emission_types]
        trace = go.Bar(  # Appending data for graph that has specifications
            x=emission_types,
            y=emissions,
            name=country,
            hoverinfo='y+name'
        )
        trace_data.append(trace)

    layout = go.Layout(  # Styling and formatting aspects such as color, title, legends
        title=f'CO2 Emissions by Fossil Fuels for Top 10 Countries in {selected_year}',
        barmode='group',
        xaxis=dict(title='Emission Type'),
        yaxis=dict(title='CO2 Emissions (Metric Tons)'),
        legend=dict(title='Country'),
        plot_bgcolor='#212529',
        paper_bgcolor='#212529',
        font=dict(color='#FFFFFF')
    )

    return {'data': trace_data, 'layout': layout}  # Return figure

@app.callback(  #Define callback for area chart/update graph function
    Output('area-chart', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_stacked_area_chart(selected_year):
    filtered_df = df[df['year'] <= selected_year]  # Filter the DataFrame to include data up to the selected year
    
    data = []  # Create an empty list to store the data for each emission type

    for emission_type in ['coal', 'oil', 'gas', 'cement', 'flaring']: # Group by year and sum the emissions for each type
        total_emissions_by_year = filtered_df.groupby('year')[emission_type].sum().reset_index()

        trace = go.Scatter(      #Create the stacked area chart data
            x=total_emissions_by_year['year'],
            y=total_emissions_by_year[emission_type],
            mode='lines',
            name=emission_type.title(),
            stackgroup='one'
        )
        data.append(trace)

    layout = go.Layout(   # Create the layout and figure to be returned
        title=f'Total CO2 Emissions Over Time until {selected_year}',
        xaxis=dict(title='Year'),
        yaxis=dict(title='CO2 Emissions (Metric Tons)', tickformat=',.0f'),  # Adjust tick format to display values in metric tons
        plot_bgcolor='#212529',
        paper_bgcolor='#212529',
        font=dict(color='#FFFFFF')
    )
    fig = go.Figure(data=data, layout=layout)

    return fig
# Run app
if __name__ == '__main__':
    app.run_server(debug=True)



