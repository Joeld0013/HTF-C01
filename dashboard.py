import dash
from dash import dcc, html, Input, Output, State, callback
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime
import calendar
import random
import requests

# Sample data
df_employees = pd.DataFrame([{
    'employee_id': 'E001',
    'name': 'Anna Jensen',
    'department': 'Finance',
    'join_date': '2021-04-15',
    'months_employed': 36,
    'base_salary': 42000,
    'holiday_allowance': 5250,
    'annual_leave_balance': 15,
    'annual_leave_total': 25,
    'parental_leave_balance': 10,
    'parental_leave_total': 32,
    'paternity_leave_balance': 2,
    'paternity_leave_total': 2,
    'bereavement_leave_balance': 3,
    'bereavement_leave_total': 3,
    'sick_leave_taken': 2
}])

df_attendance = pd.DataFrame([
    {'employee_id': 'E001', 'date': '2024-04-05', 'check_in': '08:00', 'check_out': '16:30', 'overtime_hours': 0.5, 'status': 'Present'},
    {'employee_id': 'E001', 'date': '2024-04-04', 'check_in': '08:10', 'check_out': '17:00', 'overtime_hours': 1.0, 'status': 'Present'},
    {'employee_id': 'E001', 'date': '2024-04-03', 'check_in': '08:05', 'check_out': '16:40', 'overtime_hours': 0.7, 'status': 'Present'},
    {'employee_id': 'E001', 'date': '2024-04-02', 'check_in': '08:15', 'check_out': '16:30', 'overtime_hours': 0.0, 'status': 'Present'},
    {'employee_id': 'E001', 'date': '2024-04-01', 'check_in': '08:00', 'check_out': '16:45', 'overtime_hours': 0.8, 'status': 'Present'}
])

df_leaves = pd.DataFrame([
    {'employee_id': 'E001', 'leave_type': 'Annual Leave', 'start_date': '2024-03-15', 'end_date': '2024-03-18', 'duration': 3, 'status': 'Approved'},
    {'employee_id': 'E001', 'leave_type': 'Sick Leave', 'start_date': '2024-02-10', 'end_date': '2024-02-11', 'duration': 2, 'status': 'Approved'}
])


def get_weather_data(api_key, city_name, units='metric'):
    try:
        # Get current weather
        current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units={units}"
        current_response = requests.get(current_url)
        
        # Check if request was successful
        if current_response.status_code != 200:
            print(f"Error fetching current weather: {current_response.status_code}")
            print(current_response.json())
            return None
        
        current_data = current_response.json()
        
        # Get forecast (5-day)
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={api_key}&units={units}"
        forecast_response = requests.get(forecast_url)
        
        if forecast_response.status_code != 200:
            print(f"Error fetching forecast: {forecast_response.status_code}")
            print(forecast_response.json())
            return None
            
        forecast_data = forecast_response.json()
        
        # Process current weather with error checking
        if 'main' not in current_data:
            print("Unexpected current weather response format:")
            print(current_data)
            return None
            
        current_weather = {
            'temp': current_data['main'].get('temp', 'N/A'),
            'condition': current_data['weather'][0]['description'].title() if 'weather' in current_data else 'N/A',
            'humidity': current_data['main'].get('humidity', 'N/A'),
            'wind_speed': current_data['wind'].get('speed', 'N/A') if 'wind' in current_data else 'N/A',
            'icon': get_weather_icon(current_data['weather'][0]['icon']) if 'weather' in current_data else '☁️'
        }
        
        # Process forecast with error checking
        forecast = []
        today = datetime.datetime.now()
        
        for i in range(3):  # Get today + next 2 days
            try:
                if i == 0:
                    # Today's forecast (use first forecast entry)
                    day_data = forecast_data['list'][0]
                    day_name = 'Today'
                else:
                    # Find noon forecast for next days
                    target_date = today + datetime.timedelta(days=i)
                    target_date_str = target_date.strftime('%Y-%m-%d')
                    day_forecasts = [f for f in forecast_data['list'] if f['dt_txt'].startswith(target_date_str)]
                    day_data = day_forecasts[len(day_forecasts)//2] if day_forecasts else forecast_data['list'][i*8]
                    day_name = (today + datetime.timedelta(days=i)).strftime('%A')
                
                forecast_entry = {
                    'day': day_name,
                    'temp_high': day_data['main'].get('temp_max', 'N/A'),
                    'temp_low': day_data['main'].get('temp_min', 'N/A'),
                    'condition': day_data['weather'][0]['description'].title() if 'weather' in day_data else 'N/A',
                    'icon': get_weather_icon(day_data['weather'][0]['icon']) if 'weather' in day_data else '☁️'
                }
                
                # Add warnings if applicable
                warnings = []

# Heavy rain
                if 'rain' in day_data and day_data['rain'].get('3h', 0) > 10:
                    warnings.append('⚠️ Heavy Rain Warning')

# Strong winds
                if 'wind' in day_data and day_data['wind'].get('speed', 0) > 15:
                    warnings.append('🌬️ Strong Wind Advisory')

# Thunderstorms
                if 'weather' in day_data and 'storm' in day_data['weather'][0]['description'].lower():
                    warnings.append('⛈️ Thunderstorm Warning')

# If there are any warnings, add to forecast_entry
                if warnings:
                    forecast_entry['warnings'] = warnings
    
                    
                forecast.append(forecast_entry)
            except (KeyError, IndexError) as e:
                print(f"Error processing forecast day {i}: {str(e)}")
                continue
        
        return {
            'current': current_weather,
            'forecast': forecast
        }
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

def get_weather_icon(icon_code):
    icon_map = {
        '01d': '☀️', '01n': '🌙',
        '02d': '⛅', '02n': '⛅',
        '03d': '☁️', '03n': '☁️',
        '04d': '☁️', '04n': '☁️',
        '09d': '🌧️', '09n': '🌧️',
        '10d': '🌦️', '10n': '🌦️',
        '11d': '⛈️', '11n': '⛈️',
        '13d': '❄️', '13n': '❄️',
        '50d': '🌫️', '50n': '🌫️'
    }
    return icon_map.get(icon_code, '🌈')

# Usage with fallback to sample data
api_key = "adeb8ce5ba02e4a09b6befe21d7144a9"  # Replace with your actual API key
city_name = "Bangalore "

weather_data = get_weather_data(api_key, city_name)

if weather_data is None:
    print("Failed to fetch real weather data, using sample data instead")
    weather_data = {
        'current': {
            'temp': 18,
            'condition': 'Partly Cloudy',
            'humidity': 65,
            'wind_speed': 12,
            'icon': '⛅'
        },
        'forecast': [
            {'day': 'Today', 'temp_high': 18, 'temp_low': 10, 'condition': 'Partly Cloudy', 'icon': '⛅'},
            {'day': 'Tomorrow', 'temp_high': 22, 'temp_low': 12, 'condition': 'Sunny', 'icon': '☀️'},
            {'day': 'Wednesday', 'temp_high': 17, 'temp_low': 9, 'condition': 'Rain', 'icon': '🌧️', 'warning': 'Heavy Rain Warning'}
        ]
    }

#print(weather_data)

# AI task recommendations
ai_tasks = [
    {'priority': 'High', 'task': 'Complete Q2 financial report', 'deadline': '2024-04-15', 'status': 'Pending'},
    {'priority': 'Medium', 'task': 'Review department budget allocations', 'deadline': '2024-04-20', 'status': 'Pending'},
    {'priority': 'Low', 'task': 'Update expense tracking spreadsheet', 'deadline': '2024-04-25', 'status': 'Pending'}
]

# Monthly performance data for charts
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
performance_data = [84, 78, 82, 91, 85, 89]
attendance_data = [95, 92, 98, 100, 96, 98]
overtime_monthly = [12, 8, 10, 15, 16, 14]

# Generate leave balance data for pie chart
leave_types = ['Annual Leave', 'Parental Leave', 'Paternity Leave', 'Bereavement Leave']
leave_used = [10, 22, 0, 0]
leave_remaining = [15, 10, 2, 3]

# Create a color palette
colors = {
    'primary': '#1f77b4',
    'secondary': '#2ca02c',
    'accent': '#ff7f0e',
    'background': '#f9fafb',
    'card': '#ffffff',
    'text': '#2c3e50',
    'border': '#e1e4e8',
    'warning': '#e74c3c',
    'high': '#e74c3c',
    'medium': '#f39c12',
    'low': '#3498db'
}

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Employee Dashboard"

# Layout with tabs for better organization
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H2("Employee Dashboard", style={"margin-bottom": "10px"}),
            html.H3(f"Welcome, {df_employees['name'][0]} ({df_employees['employee_id'][0]})", 
                    style={"color": colors['text'], "font-weight": "normal"})
        ], style={"display": "flex", "flex-direction": "column", "align-items": "center"}),
        
        dcc.Tabs(id='dashboard-tabs', value='overview', children=[
            dcc.Tab(label='Overview', value='overview'),
            dcc.Tab(label='Attendance', value='attendance'),
            dcc.Tab(label='Leave Management', value='leave'),
            dcc.Tab(label='Performance', value='performance')
        ], style={"margin-top": "20px"})
    ]),
    
    html.Div(id='tab-content', className="tab-content")
], className="dashboard-container")

@callback(
    Output('tab-content', 'children'),
    Input('dashboard-tabs', 'value')
)
def render_tab_content(tab):
    if tab == 'overview':
        return html.Div([
            # Weather widget & AI Task recommendations row
            html.Div([
                # Weather Widget
                html.Div([
                    html.H4("Weather Report", className="card-title"),
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Span(weather_data['current']['icon'], className="weather-icon"),
                                html.Div([
                                    html.H3(f"{weather_data['current']['temp']}°C", className="temp"),
                                    html.P(weather_data['current']['condition'], className="condition")
                                ])
                            ], className="current-weather"),
                            html.Div([
                                html.P(f"Humidity: {weather_data['current']['humidity']}%"),
                                html.P(f"Wind: {weather_data['current']['wind_speed']} km/h")
                            ], className="weather-details")
                        ], className="weather-main"),
                        
                        html.Div([
                            html.Div([
                                html.H5(day['day']),
                                html.Span(day['icon'], className="forecast-icon"),
                                html.P(f"{day['temp_high']}°/{day['temp_low']}°"),
                                html.Div([
                                    html.P(day['warning'], className="weather-warning") 
                                    if 'warning' in day else None
                                ])
                            ], className="forecast-day") 
                            for day in weather_data['forecast']
                        ], className="weather-forecast")
                    ])
                ], className="card flex-1"),
                
                # AI Task Recommendations
                html.Div([
                    html.H4("AI Task Recommendations", className="card-title"),
                    html.Div([
                        html.Table([
                            html.Thead(html.Tr([html.Th(col) for col in ['Priority', 'Task', 'Deadline', 'Status']])),
                            html.Tbody([
                                html.Tr([
                                    html.Td(html.Span(task['priority'], className=f"priority-badge {task['priority'].lower()}")),
                                    html.Td(task['task']),
                                    html.Td(task['deadline']),
                                    html.Td(html.Span(task['status'], className="status-badge pending"))
                                ]) for task in ai_tasks
                            ])
                        ], className="data-table")
                    ], className="table-container"),
                    html.Div([
                        html.Button('Generate More Tasks', id='generate-tasks-btn', className="action-button")
                    ], className="action-container", style={"margin-top": "15px"})
                ], className="card flex-1")
            ], className="card-row"),
        
            # Personal info & AI insights row
            html.Div([
                html.Div([
                    html.H4("Personal Information", className="card-title"),
                    html.Div([
                        html.Div([
                            html.P("Department"),
                            html.H5(df_employees['department'][0])
                        ], className="info-item"),
                        html.Div([
                            html.P("Join Date"),
                            html.H5(df_employees['join_date'][0])
                        ], className="info-item"),
                        html.Div([
                            html.P("Months Employed"),
                            html.H5(df_employees['months_employed'][0])
                        ], className="info-item")
                    ], className="info-grid"),
                    html.Div([
                        html.Div([
                            html.P("Base Salary"),
                            html.H5(f"{df_employees['base_salary'][0]} DKK")
                        ], className="info-item"),
                        html.Div([
                            html.P("Holiday Allowance"),
                            html.H5(f"{df_employees['holiday_allowance'][0]} DKK")
                        ], className="info-item")
                    ], className="info-grid")
                ], className="card flex-1"),
                
                html.Div([
                    html.H4("AI Insights", className="card-title"),
                    html.Div([
                        html.Div([
                            html.P("Performance"),
                            html.H5("High", style={"color": "#27ae60"})
                        ], className="insight-item"),
                        html.Div([
                            html.P("Attendance"),
                            html.H5("98%", style={"color": "#27ae60"})
                        ], className="insight-item"),
                        html.Div([
                            html.P("Late Arrivals"),
                            html.H5("Low", style={"color": "#27ae60"})
                        ], className="insight-item"),
                        html.Div([
                            html.P("Overtime"),
                            html.H5("Moderate", style={"color": "#f39c12"})
                        ], className="insight-item")
                    ], className="insight-grid"),
                    html.Div([
                        html.P("Recommendation", className="recommendation-label"),
                        html.P("Keep up the good work!", className="recommendation")
                    ], className="recommendation-container")
                ], className="card flex-1", style={"backgroundColor": "#f8f9fa"})
            ], className="card-row"),
            
            html.Div([
                dcc.Graph(
                    id='performance-graph',
                    figure={
                        'data': [
                            go.Scatter(
                                x=months, 
                                y=performance_data,
                                mode='lines+markers',
                                name='Performance',
                                line=dict(color=colors['primary'], width=3),
                                marker=dict(size=8)
                            ),
                            go.Scatter(
                                x=months, 
                                y=attendance_data,
                                mode='lines+markers',
                                name='Attendance',
                                line=dict(color=colors['secondary'], width=3),
                                marker=dict(size=8)
                            )
                        ],
                        'layout': go.Layout(
                            title='Performance & Attendance Trends',
                            xaxis={'title': 'Month'},
                            yaxis={'title': 'Score', 'range': [60, 100]},
                            height=300,
                            margin={'l': 40, 'b': 40, 't': 50, 'r': 10},
                            hovermode='closest',
                            legend={'orientation': 'h', 'y': -0.2}
                        )
                    }
                )
            ], className="card")
        ])
        
    elif tab == 'attendance':
        return html.Div([
            html.Div([
                html.Div([
                    html.H4("Recent Attendance", className="card-title"),
                    html.Div([
                        html.Table([
                            html.Thead(html.Tr([html.Th(col) for col in ['Date', 'Check In', 'Check Out', 'Overtime', 'Status']])),
                            html.Tbody([
                                html.Tr([
                                    html.Td(row['date']),
                                    html.Td(row['check_in']),
                                    html.Td(row['check_out']),
                                    html.Td(f"{row['overtime_hours']} hrs" if row['overtime_hours'] else "-"),
                                    html.Td(html.Span(row['status'], className="status-badge present"))
                                ]) for _, row in df_attendance.iterrows()
                            ])
                        ], className="data-table")
                    ], className="table-container")
                ], className="card"),
                
                html.Div([
                    dcc.Graph(
                        id='overtime-graph',
                        figure={
                            'data': [
                                go.Bar(
                                    x=months,
                                    y=overtime_monthly,
                                    marker_color=colors['accent']
                                )
                            ],
                            'layout': go.Layout(
                                title='Monthly Overtime Hours',
                                xaxis={'title': 'Month'},
                                yaxis={'title': 'Hours'},
                                height=300,
                                margin={'l': 40, 'b': 40, 't': 50, 'r': 10}
                            )
                        }
                    )
                ], className="card")
            ])
        ])
        
    elif tab == 'leave':
        return html.Div([
            html.Div([
                html.Div([
                    html.H4("Leave Balance", className="card-title"),
                    dcc.Graph(
                        id='leave-balance-chart',
                        figure={
                            'data': [
                                go.Bar(
                                    x=leave_types,
                                    y=leave_remaining,
                                    name='Remaining',
                                    marker_color=colors['primary']
                                ),
                                go.Bar(
                                    x=leave_types,
                                    y=leave_used,
                                    name='Used',
                                    marker_color=colors['accent']
                                )
                            ],
                            'layout': go.Layout(
                                barmode='stack',
                                title='Leave Days Balance',
                                xaxis={'title': 'Leave Type'},
                                yaxis={'title': 'Days'},
                                height=300,
                                margin={'l': 40, 'b': 40, 't': 50, 'r': 10},
                                legend={'orientation': 'h', 'y': -0.2}
                            )
                        }
                    )
                ], className="card flex-1"),
                
                html.Div([
                    html.H4("Leave History", className="card-title"),
                    html.Div([
                        html.Table([
                            html.Thead(html.Tr([html.Th(col) for col in ['Type', 'Start Date', 'End Date', 'Duration', 'Status']])),
                            html.Tbody([
                                html.Tr([
                                    html.Td(row['leave_type']),
                                    html.Td(row['start_date']),
                                    html.Td(row['end_date']),
                                    html.Td(f"{row['duration']} days"),
                                    html.Td(html.Span(row['status'], className="status-badge approved"))
                                ]) for _, row in df_leaves.iterrows()
                            ])
                        ], className="data-table")
                    ], className="table-container"),
                    
                    html.Div([
                        html.Button('Request Leave', id='request-leave-btn', className="action-button")
                    ], className="action-container")
                ], className="card flex-1")
            ], className="card-row")
        ])
        
    elif tab == 'performance':
        return html.Div([
            html.Div([
                html.H4("Performance Overview", className="card-title"),
                dcc.Graph(
                    id='radar-chart',
                    figure={
                        'data': [
                            go.Scatterpolar(
                                r=[89, 95, 82, 78, 90],
                                theta=['Productivity', 'Attendance', 'Communication', 'Collaboration', 'Quality'],
                                fill='toself',
                                name='Current',
                                line_color=colors['primary']
                            ),
                            go.Scatterpolar(
                                r=[75, 75, 75, 75, 75],
                                theta=['Productivity', 'Attendance', 'Communication', 'Collaboration', 'Quality'],
                                fill='toself',
                                name='Target',
                                line_color=colors['accent'],
                                opacity=0.5
                            )
                        ],
                        'layout': go.Layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 100]
                                )
                            ),
                            showlegend=True,
                            height=400,
                            margin={'l': 40, 'b': 40, 't': 40, 'r': 40}
                        )
                    }
                )
            ], className="card")
        ])

# Generate task recommendations callback
@callback(
    Output('tab-content', 'children', allow_duplicate=True),
    Input('generate-tasks-btn', 'n_clicks'),
    State('dashboard-tabs', 'value'),
    prevent_initial_call=True
)
def generate_new_tasks(n_clicks, current_tab):
    if current_tab == 'overview':
        # Generate some new random tasks
        new_task = {
            'priority': random.choice(['High', 'Medium', 'Low']),
            'task': random.choice([
                'Prepare monthly expense report',
                'Schedule team meeting for budget review',
                'Update quarterly forecasts',
                'Create presentation for management meeting',
                'Review invoices for payment processing'
            ]),
            'deadline': f'2024-04-{random.randint(15, 30)}',
            'status': 'New'
        }
        ai_tasks.insert(0, new_task)
        if len(ai_tasks) > 5:
            ai_tasks.pop()
        
        # Return the updated overview tab
        return render_tab_content('overview')
    return render_tab_content(current_tab)

# CSS embedded
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <title>Employee Dashboard</title>
        {%metas%}
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: #f9fafb;
                color: #2c3e50;
            }
            .dashboard-container {
                max-width: 1200px;
                margin: auto;
                padding: 20px;
            }
            .card {
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                transition: all 0.3s ease;
            }
            .card:hover {
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .card-title {
                color: #2c3e50;
                margin-top: 0;
                margin-bottom: 20px;
                font-weight: 600;
                border-bottom: 1px solid #f0f0f0;
                padding-bottom: 10px;
            }
            .card-row {
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
            }
            .flex-1 {
                flex: 1;
                min-width: 300px;
            }
            .info-grid, .insight-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
                gap: 15px;
            }
            .info-item, .insight-item {
                padding: 10px;
            }
            .info-item p, .insight-item p {
                margin: 0;
                font-size: 0.85rem;
                color: #7f8c8d;
            }
            .info-item h5, .insight-item h5 {
                margin: 5px 0 0 0;
                font-size: 1.1rem;
                font-weight: 600;
            }
            .recommendation-container {
                margin-top: 15px;
                padding: 10px;
            }
            .recommendation-label {
                margin: 0;
                font-size: 0.85rem;
                color: #7f8c8d;
            }
            .recommendation {
                margin: 5px 0 0 0;
                font-size: 1rem;
                font-weight: 500;
            }
            table.data-table {
                width: 100%;
                border-collapse: collapse;
            }
            .data-table th, .data-table td {
                text-align: left;
                padding: 12px;
                border-bottom: 1px solid #eee;
            }
            .data-table th {
                background: #f6f8fa;
                font-weight: 600;
                color: #2c3e50;
            }
            .data-table tr:hover {
                background-color: #f9fafb;
            }
            .status-badge, .priority-badge {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: 500;
            }
            .present, .approved {
                background-color: #e3f8e5;
                color: #27ae60;
            }
            .pending, .new {
                background-color: #eaecee;
                color: #7f8c8d;
            }
            .high {
                background-color: #fce5e5;
                color: #e74c3c;
            }
            .medium {
                background-color: #fef5e7;
                color: #f39c12;
            }
            .low {
                background-color: #e8f4f8;
                color: #3498db;
            }
            .action-container {
                margin-top: 20px;
                display: flex;
                justify-content: flex-end;
            }
            .action-button {
                background-color: #1f77b4;
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 500;
                transition: background-color 0.3s;
            }
            .action-button:hover {
                background-color: #166aaa;
            }
            .tab-content {
                margin-top: 20px;
            }
            /* Weather Widget Styles */
            .weather-icon, .forecast-icon {
                font-size: 2.5rem;
                margin-right: 15px;
            }
            .forecast-icon {
                font-size: 1.5rem;
            }
            .current-weather {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
            }
            .temp {
                font-size: 1.8rem;
                margin: 0;
                font-weight: 600;
            }
            .condition {
                margin: 0;
                color: #7f8c8d;
            }
            .weather-details {
                margin-left: 20px;
            }
            .weather-details p {
                margin: 5px 0;
                color: #7f8c8d;
            }
            .weather-forecast {
                display: flex;
                justify-content: space-between;
                border-top: 1px solid #eee;
                padding-top: 15px;
            }
            .forecast-day {
                text-align: center;
                flex: 1;
            }
            .forecast-day h5 {
                margin: 0 0 10px;
                font-weight: 600;
            }
            .forecast-day p {
                margin: 5px 0;
            }
            .weather-warning {
                color: #e74c3c;
                font-weight: 600;
                font-size: 0.8rem;
                margin-top: 8px;
            }
            .weather-main {
                display: flex;
                justify-content: space-between;
                margin-bottom: 15px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)