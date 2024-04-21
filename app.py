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
    style={'backgroundColor': '#212529'},  #setting background color 
    children=[ #creating the layout with headings with approprite styling/colors 
        html.H4("Carbon Dioxide (CO2) Emissions By Year", style={'color': '#FFFFFF'}),
        html.H5("Track carbon dioxide (CO2) emissions for the chosen year from 1990 to 2022 and its most significant contributors.", style={'color': '#FFFFFF'}),
        html.Label('Select Year', style={'color': '#FFFFFF'}),
        dcc.Dropdown( #creating dropdown for the years with a preset value
            options=[{'label': year, 'value': year} for year in df['year'].unique()],
            id='year-dropdown',
            value=2020, #preset year; not a multi-select dropdown
            multi=False,
        ),
       html.Div( #creating a UI component for the world map graph with appropriate styling and colors while adjusting margins; users can pick which data type they would like to see
            [
                html.Label('Select Data Type for the World Map', style={'color': '#FFFFFF'}),
                dcc.RadioItems(
                    id='data-type-radio',
                    options=[
                        {'label': 'Total', 'value': 'total'},
                        {'label': 'Per Capita', 'value': 'per_capita'}
                    ],
                    value='total',  #preset to total
                    labelStyle={'display': 'inline-block', 'color': '#FFFFFF'}
                ),
            ],
            style={'margin-top': '30px'}  
        ),
        html.Div( #world map taking up half of the page width and colors
            dcc.Graph(id='world-map'),
            style={'width': '100%', 'height': '50%', 'display': 'inline-block', 'backgroundColor': '#212529'}
        ),
        html.Div( #graphs with appropriate styling and colors and setting them to half the page side by side
            [
                #grouped bar chart for CO2 emissions
                dcc.Graph(id='bar-chart'),
                #line area chart for CO2 emissions
                dcc.Graph(id='area-chart'),
            ],
            style={'width': '50%', 'height': '100%', 'display': 'flex', 'flex-direction': 'row', 'backgroundColor': '#212529'}
        ),
    ]
)
#define callback for world map/update graph function
@app.callback(
    Output('world-map', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('data-type-radio', 'value')]
)
def update_world_map(selected_year, data_type):
    filtered_df = df[df['year'] == selected_year]
    
    if data_type == 'total': #creating an if/else statement that coincides for the radio button based on selected dataset for the colors based on the selected year
        color_column = 'total'
        title = f'Total CO2 Emissions by Country in {selected_year}'
        colorbar_title = 'CO2 Emissions (Metric Tons)'
    else:
        color_column = 'per_capita'
        title = f'CO2 Emissions Per Capita by Country in {selected_year}'
        colorbar_title = 'CO2 Emissions Per Capita'
    
    fig = px.choropleth(filtered_df, #making the graph using the country names to map to the country, what column maps to the color of the countries and the styling components
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
    
    return fig #return figure

#define callback for grouped bar chart/update graph function
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_grouped_bar_chart(selected_year):
    filtered_df = df[df['year'] == selected_year]
    
    top_10_countries = filtered_df.groupby('country')['total'].sum().nlargest(10).index #select top 10 emitting countries
    
    trace_data = [] #making an empty list to store trace data
    
    emission_types = ['coal', 'oil', 'gas', 'cement', 'flaring'] #column names for each emission type
    
    for country in top_10_countries: #creating a for loop to iterate the values for the top 10 
        country_data = filtered_df[filtered_df['country'] == country]
        emissions = [country_data[emission_type].values[0] for emission_type in emission_types]
        trace = go.Bar(  #appending data for graph that has specifications 
            x=emission_types,
            y=emissions,
            name=country,
            hoverinfo='y+name'
        )
        trace_data.append(trace) 
    
    layout = go.Layout( #styling and formatting aspects such as color, title, legends
        title=f'CO2 Emissions by Type for Top 10 Emitting Countries in {selected_year}',
        barmode='group',
        xaxis=dict(title='Emission Type'),
        yaxis=dict(title='CO2 Emissions (Metric Tons)'),
        legend=dict(title='Country'),
        plot_bgcolor='#212529',  
        paper_bgcolor='#212529',  
        font=dict(color='#FFFFFF')  
    )
    
    return {'data': trace_data, 'layout': layout} #return figure

@app.callback( #define callback for areac hart/update graph function
    Output('area-chart', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_stacked_area_chart(selected_year): #filter the DataFrame to include data from the first year up to the selected year
    filtered_df = df[df['year'] <= selected_year]

    top_10_countries = filtered_df.groupby('country')['total'].sum().nlargest(10).index  #getting the top 10 countries based on total emissions for the selected year

    filtered_df = filtered_df[filtered_df['country'].isin(top_10_countries)]  #filter for the top 10 countries

    x_column = 'year' # setting x and y variables
    y_column = 'total'  
    color_column = 'country'  

    # Create the stacked area chart with proper formatting, colors, labels
    fig = px.area(filtered_df, x=x_column, y=y_column, color=color_column, 
                   title='CO2 Emissions by Type for Top 10 Emitting Countries Overtime',
                   labels={x_column: 'Year', y_column: 'CO2 Emissions (Metric Tons)', color_column: 'Country'})
    fig.update_yaxes(tickformat=',.0f')
    fig.update_layout(
        plot_bgcolor='#212529',  # DARKLY theme background color
        paper_bgcolor='#212529',  # DARKLY theme paper background color
        font=dict(color='#FFFFFF')  # White font color
    )
    return fig #returns figure


# Run app
if __name__ == '__main__':
    app.run_server(debug=True)



