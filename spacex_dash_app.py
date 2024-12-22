Python 3.10.4 (v3.10.4:9d38120e33, Mar 23 2022, 17:29:05) [Clang 13.0.0 (clang-1300.0.29.30)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the spacex data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # Task 1: Dropdown for selecting launch sites
                                html.Div([
                                    dcc.Dropdown(
                                        id='site-dropdown',  # Unique identifier for this component
                                        options=[
                                            {'label': 'All Sites', 'value': 'ALL'},  # Default option to select all sites
                                            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'}
                                        ],  # List of options (launch sites)
                                        value='ALL',  # Default value when the page loads, meaning all sites are selected
                                        placeholder='Select a Launch Site here',  # Placeholder text for the dropdown input
                                        searchable=True  # Allow searching for launch sites in the dropdown
                                    )
                                ]),
                                html.Br(),

                                # Task 2: Pie chart to show success/failure rate based on selected site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                # Task 3: Payload range slider to filter payload by mass
                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=min_payload,
                                    max=max_payload,
                                    step=1000,
                                    marks={i: str(i) for i in range(int(min_payload), int(max_payload) + 1, 1000)},
                                    value=[min_payload, max_payload]
                                ),
                                html.Br(),

                                # Task 4: Scatter plot for correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart'))
                            ])

# Task 2: Callback function to render success-pie-chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    # Initialize filtered dataframe to the entire dataframe initially
    filtered_df = spacex_df

    # Check if "ALL" sites are selected
    if entered_site == 'ALL':
        grouped_df = spacex_df.groupby('Launch Site')['class'].count().reset_index()
        grouped_df.rename(columns={'class': 'Total Launches'}, inplace=True)
        fig = px.pie(
            filtered_df, 
            names='Launch Site',  # class column (0 for failed, 1 for successful)
            title='Total Launch Success By Site',
            labels={'Launch Site': 'Site'},
            hole=0.3  # Creates a donut chart for better visibility
        )
    else:
        # If a specific site is selected, filter the dataframe for that site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]        
        fig = px.pie(
            filtered_df, 
            names='class',  # class column (0 for failed, 1 for successful)
            title=f"Launch Success vs Failure for {entered_site}",
            labels={'class': 'Launch Outcome'},
            hole=0.3  # Creates a donut chart for better visibility
        )

    return fig

# Task 4: Callback function for payload range slider and site-dropdown
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_plot(entered_site, payload_range):
    # Initialize filtered dataframe to the entire dataframe initially
    filtered_df = spacex_df

    # Filter data based on payload range
    filtered_df = filtered_df[
        (filtered_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (filtered_df['Payload Mass (kg)'] <= payload_range[1])
    ]

    # Check if "ALL" sites are selected
    if entered_site != 'ALL':
        # If a specific site is selected, filter the dataframe for that site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

    # Create scatter plot for Payload vs Launch Outcome
    fig = px.scatter(
        filtered_df, 
        x='Payload Mass (kg)', 
        y='class', 
        color='Booster Version Category',  # Color points based on Booster Version
        title=f"Payload vs Launch Outcome for {entered_site if entered_site != 'ALL' else 'All Sites'}",
        labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'}
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
