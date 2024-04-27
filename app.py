import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Load the data
df = pd.read_csv('MedSchool.csv')

# Convert time columns from minutes to hours
time_columns = ['Sum', 'Anki', 'Volunteering', 'Research', 'Other', 'Self-Study']
df[time_columns] /= 60  # Convert minutes to hours

# Initialize the Dash app
app = dash.Dash(__name__)

# Get all unique year labels
all_year_labels = df['yearLabel'].unique()

# Add "All of med school" option to the list of year labels
all_year_labels = ['All of med school'] + list(all_year_labels)

# Define colors
colors = {
    'background': '#f9f9f9',
    'text': '#333333',
    'plot_background': '#ffffff'
}

# Define a color scale with more than 14 colors
color_scale = px.colors.qualitative.Bold

# Define the layout of the dashboard
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div([
        html.H1([html.A("Medical School Quantified", href="https://medium.com/p/c2f3b5c36504", style={'color': colors['text']})], style={'textAlign': 'center', 'color': colors['text']}),
        html.H3("Chris Hornung", style={'textAlign': 'center', 'color': colors['text']})    ], style={'textAlign': 'center', 'margin': '20px auto'}),

    # Dropdown to filter by yearLabel
    html.Div([
        html.Label("Select Year Label:"),
        dcc.Dropdown(
            id='year-label-dropdown',
            options=[{'label': label, 'value': label} for label in all_year_labels],
            value=all_year_labels[0],  # Default value
            multi=False,
            searchable=False,
            clearable=False,
            style={'width': '50%', 'margin': '10px auto', 'color': colors['text']}
        ),
    ], style={'textAlign': 'center'}),

    # Dropdown to further filter by Year, MS2Block, MS3Rotation, MS4Rotation, or yearLabel
    html.Div([
        html.Label("Select Additional Filter:"),
        dcc.Dropdown(
            id='additional-filter-dropdown',
            options=[
                {'label': 'Year Label', 'value': 'yearLabel'},
                {'label': 'MS2Block', 'value': 'MS2Block'},
                {'label': 'MS3Rotation', 'value': 'MS3Rotation'},
                {'label': 'MS4Rotation', 'value': 'MS4Rotation'}
            ],
            value='yearLabel',  # Default value
            multi=False,
            searchable=False,
            clearable=False,
            style={'width': '50%', 'margin': '10px auto', 'color': colors['text']}
        ),
    ], style={'textAlign': 'center'}),

    # Total sum of selected additional filter
    html.Div(id='total-sum', style={'textAlign': 'center', 'margin': '20px auto', 'color': colors['text']}),

    # Main graph to display the data
    dcc.Graph(id='time-graph', style={'height': '60vh'}),

    # Graphs for specific categories
    html.Div([
        dcc.Graph(id='anki-graph', config={'displayModeBar': False}),
        dcc.Graph(id='volunteering-graph', config={'displayModeBar': False}),
        dcc.Graph(id='research-graph', config={'displayModeBar': False}),
        dcc.Graph(id='other-graph', config={'displayModeBar': False}),
        dcc.Graph(id='self-study-graph', config={'displayModeBar': False})
    ], style={'display': 'grid', 'grid-template-columns': 'repeat(auto-fit, minmax(300px, 1fr))', 'gap': '20px'})
])

# Define callback to update the graphs based on dropdown selections
@app.callback(
    [Output('time-graph', 'figure'),
     Output('anki-graph', 'figure'),
     Output('volunteering-graph', 'figure'),
     Output('research-graph', 'figure'),
     Output('other-graph', 'figure'),
     Output('self-study-graph', 'figure'),
     Output('total-sum', 'children')],
    [Input('year-label-dropdown', 'value'),
     Input('additional-filter-dropdown', 'value')]
)
def update_graph(selected_year_label, additional_filter):
    if selected_year_label == "All of med school":
        filtered_df = df
        title_prefix = "All of Medical School"
    else:
        filtered_df = df[df['yearLabel'] == selected_year_label]
        title_prefix = f"{selected_year_label} of Medical School"

    # Calculate total sum of selected additional filter
    total_sum = filtered_df.groupby(additional_filter)['Sum'].sum().sum()

    # Main graph showing time spent by additional filter
    if additional_filter == 'yearLabel':
        time_graph = px.bar(filtered_df.groupby('yearLabel')['Sum'].sum().reset_index(), x='yearLabel', y='Sum', title=f'Time Spent by Year Label')
    else:
        time_graph = px.bar(filtered_df.groupby(additional_filter)['Sum'].sum().reset_index(), x=additional_filter, y='Sum', title=f'Time Spent by {additional_filter} in Hours')

    # Add text annotations to each bar in the main graph
    time_graph.update_traces(text=filtered_df.groupby(additional_filter)['Sum'].sum().reset_index()['Sum'].round(0).astype(int), textposition='inside')

    # Graphs for specific categories
    anki_graph = px.bar(filtered_df.groupby(additional_filter)['Anki'].sum().reset_index(), x=additional_filter, y='Anki', title=f'Time Spent on Anki in Hours')
    volunteering_graph = px.bar(filtered_df.groupby(additional_filter)['Volunteering'].sum().reset_index(), x=additional_filter, y='Volunteering', title=f'Time Spent on Volunteering in Hours')
    research_graph = px.bar(filtered_df.groupby(additional_filter)['Research'].sum().reset_index(), x=additional_filter, y='Research', title=f'Time Spent on Research in Hours')
    other_graph = px.bar(filtered_df.groupby(additional_filter)['Other'].sum().reset_index(), x=additional_filter, y='Other', title=f'Time Spent on Other Activities in Hours')
    self_study_graph = px.bar(filtered_df.groupby(additional_filter)['Self-Study'].sum().reset_index(), x=additional_filter, y='Self-Study', title=f'Time Spent on Self-Study in Hours')

    # Assign colors using a color scale
    for graph in [time_graph, anki_graph, volunteering_graph, research_graph, other_graph, self_study_graph]:
        graph.update_traces(marker_color=color_scale)

    # Add axis labels to graphs
    time_graph.update_layout(xaxis_title=additional_filter, yaxis_title='Time (Hours)')
    anki_graph.update_layout(xaxis_title=additional_filter, yaxis_title='Time (Hours)')
    volunteering_graph.update_layout(xaxis_title=additional_filter, yaxis_title='Time (Hours)')
    research_graph.update_layout(xaxis_title=additional_filter, yaxis_title='Time (Hours)')
    other_graph.update_layout(xaxis_title=additional_filter, yaxis_title='Time (Hours)')
    self_study_graph.update_layout(xaxis_title=additional_filter, yaxis_title='Time (Hours)')

    return time_graph, anki_graph, volunteering_graph, research_graph, other_graph, self_study_graph, f'Total Time: {total_sum:.2f} hours'

# Define server for Gunicorn compatibility
server = app.server
