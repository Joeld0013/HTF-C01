import dash
from dash import dcc, html, Input, Output, State, callback
import plotly.graph_objects as go
import plotly.express as px
import mysql.connector
import pandas as pd
import datetime
import requests

# Define color palette
colors = {
    'primary': '#1f77b4',
    'secondary': '#2ca02c',
    'accent': '#ff7f0e',
    'background': '#f9fafb',
    'text': '#2c3e50',
    'high': '#e74c3c',
    'medium': '#f39c12',
    'low': '#3498db'
}

# Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="workforce"
    )
    return conn

# Data fetching functions
def get_employee_data(employee_id="E001"):  # Default ID for testing
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM employee_dash WHERE employee_id = %s", (employee_id,))
    emp_data = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return emp_data

def get_attendance_data(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT date, check_in, check_out, overtime_hours, status 
        FROM attendance_dash 
        WHERE employee_id = %s 
        ORDER BY date DESC 
        LIMIT 5
    """, (employee_id,))
    
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(data) if data else pd.DataFrame()

def get_leave_data(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get leave history
    cursor.execute("""
        SELECT leave_type, start_date, end_date, duration, status 
        FROM leave_dash 
        WHERE employee_id = %s 
        ORDER BY start_date DESC
    """, (employee_id,))
    leave_history = cursor.fetchall()
    
    # Get leave balances
    cursor.execute("""
        SELECT annual_leave_balance, annual_leave_total,
               parental_leave_balance, parental_leave_total,
               paternity_leave_balance, paternity_leave_total,
               bereavement_leave_balance, bereavement_leave_total,
               sick_leave_taken
        FROM employee_dash 
        WHERE employee_id = %s
    """, (employee_id,))
    leave_balance = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return leave_history, leave_balance

def get_performance_data(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get monthly performance data
    cursor.execute("""
        SELECT month, performance_score, attendance_score, overtime_hours
        FROM performance_dash
        WHERE employee_id = %s
        ORDER BY year, month_num
        LIMIT 6
    """, (employee_id,))
    monthly_data = cursor.fetchall()
    
    # Get radar chart data
    cursor.execute("""
        SELECT productivity, attendance, communication, collaboration, quality
        FROM performance_dash
        WHERE employee_id = %s
        ORDER BY year DESC, month_num DESC
        LIMIT 1
    """, (employee_id,))
    radar_data = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return monthly_data, radar_data

def get_task_recommendations(employee_id, role):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT priority, task, deadline, status
        FROM task_dash
        WHERE role = %s
        ORDER BY priority_order, deadline
        LIMIT 3
    """, (role,))
    
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return tasks

def get_weather_data(city="Bangalore"):
    api_key = "adeb8ce5ba02e4a09b6befe21d7144a9"  # Replace with actual API key
    try:
        current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        
        current_response = requests.get(current_url)
        forecast_response = requests.get(forecast_url)
        
        if current_response.status_code != 200 or forecast_response.status_code != 200:
            return None
            
        current_data = current_response.json()
        forecast_data = forecast_response.json()
        
        weather = {
            'current': {
                'temp': current_data['main']['temp'],
                'condition': current_data['weather'][0]['description'].title(),
                'humidity': current_data['main']['humidity'],
                'wind_speed': current_data['wind']['speed'],
                'icon': get_weather_icon(current_data['weather'][0]['icon'])
            },
            'forecast': []
        }
        
        today = datetime.datetime.now()
        for i in range(3):
            day_name = 'Today' if i == 0 else (today + datetime.timedelta(days=i)).strftime('%A')
            day_data = forecast_data['list'][i*8]
            
            forecast_entry = {
                'day': day_name,
                'temp_high': day_data['main']['temp_max'],
                'temp_low': day_data['main']['temp_min'],
                'condition': day_data['weather'][0]['description'].title(),
                'icon': get_weather_icon(day_data['weather'][0]['icon'])
            }
            
            weather['forecast'].append(forecast_entry)
        
        return weather
    except:
        # Return sample data if API call fails
        return {
            'current': {
                'temp': 28,
                'condition': 'Partly Cloudy',
                'humidity': 65,
                'wind_speed': 12,
                'icon': '⛅'
            },
            'forecast': [
                {'day': 'Today', 'temp_high': 29, 'temp_low': 22, 'condition': 'Partly Cloudy', 'icon': '⛅'},
                {'day': 'Tomorrow', 'temp_high': 30, 'temp_low': 23, 'condition': 'Sunny', 'icon': '☀️'},
                {'day': 'Wednesday', 'temp_high': 27, 'temp_low': 21, 'condition': 'Rain', 'icon': '🌧️'}
            ]
        }

def get_weather_icon(icon_code):
    icon_map = {
        '01d': '☀️', '01n': '🌙', '02d': '⛅', '02n': '⛅',
        '03d': '☁️', '03n': '☁️', '04d': '☁️', '04n': '☁️',
        '09d': '🌧️', '09n': '🌧️', '10d': '🌦️', '10n': '🌦️',
        '11d': '⛈️', '11n': '⛈️', '13d': '❄️', '13n': '❄️',
        '50d': '🌫️', '50n': '🌫️'
    }
    return icon_map.get(icon_code, '🌈')

# Initialize app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Employee Dashboard"

# Define the layout
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H2("Employee Dashboard", style={"margin-bottom": "10px"}),
            html.Div(id="employee-header")
        ], style={"display": "flex", "flex-direction": "column", "align-items": "center"}),
        
        # Employee selector (simplified for testing)
        html.Div([
            dcc.Input(id="employee-id-input", type="text", placeholder="Enter Employee ID", 
                     value="E001", style={"margin-right": "10px"}),
            html.Button("Load Dashboard", id="load-dashboard-btn")
        ], style={"margin": "10px auto", "text-align": "center"}),
        
        dcc.Tabs(id='dashboard-tabs', value='overview', children=[
            dcc.Tab(label='Overview', value='overview'),
            dcc.Tab(label='Attendance', value='attendance'),
            dcc.Tab(label='Leave Management', value='leave'),
            dcc.Tab(label='Performance', value='performance')
        ], style={"margin-top": "20px"})
    ]),
    
    html.Div(id='tab-content', className="tab-content")
], className="dashboard-container")

# Employee header callback
@app.callback(
    Output('employee-header', 'children'),
    [Input('load-dashboard-btn', 'n_clicks')],
    [State('employee-id-input', 'value')]
)
def update_employee_header(n_clicks, employee_id):
    if not employee_id:
        return html.H3("Please enter an Employee ID", style={"color": colors['text']})
    
    emp_data = get_employee_data(employee_id)
    if not emp_data:
        return html.H3(f"Employee {employee_id} not found", style={"color": colors['high']})
    
    return html.H3(f"Welcome, {emp_data['name']} ({emp_data['employee_id']}) - {emp_data['role']}", 
                  style={"color": colors['text'], "font-weight": "normal"})

# Tab content callback
@app.callback(
    Output('tab-content', 'children'),
    [Input('dashboard-tabs', 'value'),
     Input('load-dashboard-btn', 'n_clicks')],
    [State('employee-id-input', 'value')]
)
def render_tab_content(tab, n_clicks, employee_id):
    if not employee_id:
        return html.Div("Please enter an Employee ID and click Load Dashboard")
    
    emp_data = get_employee_data(employee_id)
    if not emp_data:
        return html.Div(f"Employee {employee_id} not found")
    
    if tab == 'overview':
        weather_data = get_weather_data()
        tasks = get_task_recommendations(employee_id, emp_data['role'])
        monthly_data, _ = get_performance_data(employee_id)
        
        return html.Div([
            # First row: Weather & Tasks
            html.Div([
                # Weather Widget
                html.Div([
                    html.H4("Weather Report", className="card-title"),
                    create_weather_widget(weather_data)
                ], className="card flex-1"),
                
                # Task Recommendations
                html.Div([
                    html.H4("Task Recommendations", className="card-title"),
                    create_tasks_table(tasks)
                ], className="card flex-1")
            ], className="card-row"),
            
            # Second row: Employee Info & Performance Insights
            html.Div([
                html.Div([
                    html.H4("Personal Information", className="card-title"),
                    create_employee_info(emp_data)
                ], className="card flex-1"),
                
                html.Div([
                    html.H4("Performance Insights", className="card-title"),
                    create_performance_insights(monthly_data)
                ], className="card flex-1")
            ], className="card-row"),
            
            # Performance chart
            html.Div([
                dcc.Graph(figure=create_performance_chart(monthly_data))
            ], className="card")
        ])
        
    elif tab == 'attendance':
        attendance_data = get_attendance_data(employee_id)
        monthly_data, _ = get_performance_data(employee_id)
        
        return html.Div([
            html.Div([
                html.H4("Recent Attendance", className="card-title"),
                create_attendance_table(attendance_data)
            ], className="card"),
            
            html.Div([
                dcc.Graph(figure=create_overtime_chart(monthly_data))
            ], className="card")
        ])
        
    elif tab == 'leave':
        leave_history, leave_balance = get_leave_data(employee_id)
        
        return html.Div([
            html.Div([
                html.Div([
                    html.H4("Leave Balance", className="card-title"),
                    dcc.Graph(figure=create_leave_balance_chart(leave_balance))
                ], className="card flex-1"),
                
                html.Div([
                    html.H4("Leave History", className="card-title"),
                    create_leave_history_table(leave_history)
                ], className="card flex-1")
            ], className="card-row")
        ])
        
    elif tab == 'performance':
        _, radar_data = get_performance_data(employee_id)
        
        return html.Div([
            html.Div([
                html.H4("Performance Overview", className="card-title"),
                dcc.Graph(figure=create_radar_chart(radar_data))
            ], className="card")
        ])

# Helper functions for UI components
def create_weather_widget(weather_data):
    if not weather_data:
        return html.Div("Weather data unavailable")
    
    return html.Div([
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
                html.P(f"{day['temp_high']}°/{day['temp_low']}°")
            ], className="forecast-day") 
            for day in weather_data['forecast']
        ], className="weather-forecast")
    ])

def create_tasks_table(tasks):
    if not tasks:
        return html.Div("No tasks available")
    
    return html.Div([
        html.Table([
            html.Thead(html.Tr([html.Th(col) for col in ['Priority', 'Task', 'Deadline', 'Status']])),
            html.Tbody([
                html.Tr([
                    html.Td(html.Span(task['priority'], className=f"priority-badge {task['priority'].lower()}")),
                    html.Td(task['task']),
                    html.Td(task['deadline']),
                    html.Td(html.Span(task['status'], className="status-badge"))
                ]) for task in tasks
            ])
        ], className="data-table")
    ], className="table-container")

def create_employee_info(emp_data):
    return html.Div([
        html.Div([
            html.Div([
                html.P("Department"),
                html.H5(emp_data.get('department', 'N/A'))
            ], className="info-item"),
            html.Div([
                html.P("Join Date"),
                html.H5(emp_data.get('join_date', 'N/A'))
            ], className="info-item"),
            html.Div([
                html.P("Months Employed"),
                html.H5(emp_data.get('months_employed', 'N/A'))
            ], className="info-item")
        ], className="info-grid"),
        html.Div([
            html.Div([
                html.P("Base Salary"),
                html.H5(f"{emp_data.get('base_salary', 'N/A')} DKK")
            ], className="info-item")
        ], className="info-grid")
    ])

def create_performance_insights(monthly_data):
    if not monthly_data:
        return html.Div("Performance data unavailable")
    
    # Calculate averages from monthly data
    perf_scores = [m.get('performance_score', 0) for m in monthly_data]
    att_scores = [m.get('attendance_score', 0) for m in monthly_data]
    overtime_hrs = [m.get('overtime_hours', 0) for m in monthly_data]
    
    avg_perf = sum(perf_scores) / len(perf_scores) if perf_scores else 0
    avg_att = sum(att_scores) / len(att_scores) if att_scores else 0
    avg_overtime = sum(overtime_hrs) / len(overtime_hrs) if overtime_hrs else 0
    
    # Ratings and colors
    perf_rating = "High" if avg_perf > 85 else "Medium" if avg_perf > 70 else "Low"
    perf_color = "#27ae60" if perf_rating == "High" else "#f39c12" if perf_rating == "Medium" else "#e74c3c"
    
    return html.Div([
        html.Div([
            html.Div([
                html.P("Performance"),
                html.H5(perf_rating, style={"color": perf_color})
            ], className="insight-item"),
            html.Div([
                html.P("Attendance"),
                html.H5(f"{avg_att:.0f}%", style={"color": "#27ae60" if avg_att > 90 else "#f39c12"})
            ], className="insight-item"),
            html.Div([
                html.P("Overtime"),
                html.H5(f"{avg_overtime:.1f} hrs", style={"color": "#3498db"})
            ], className="insight-item")
        ], className="insight-grid")
    ])

def create_performance_chart(monthly_data):
    if not monthly_data:
        return {}
    
    months = [m.get('month', '') for m in monthly_data]
    performance = [m.get('performance_score', 0) for m in monthly_data]
    attendance = [m.get('attendance_score', 0) for m in monthly_data]
    
    return {
        'data': [
            go.Scatter(
                x=months, 
                y=performance,
                mode='lines+markers',
                name='Performance',
                line=dict(color=colors['primary'], width=3),
                marker=dict(size=8)
            ),
            go.Scatter(
                x=months, 
                y=attendance,
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

def create_attendance_table(attendance_data):
    if attendance_data.empty:
        return html.Div("No attendance data available")
    
    return html.Div([
        html.Table([
            html.Thead(html.Tr([html.Th(col) for col in ['Date', 'Check In', 'Check Out', 'Overtime', 'Status']])),
            html.Tbody([
                html.Tr([
                    html.Td(row['date']),
                    html.Td(row['check_in']),
                    html.Td(row['check_out']),
                    html.Td(f"{row['overtime_hours']} hrs" if row['overtime_hours'] else "-"),
                    html.Td(html.Span(row['status'], className="status-badge present"))
                ]) for _, row in attendance_data.iterrows()
            ])
        ], className="data-table")
    ], className="table-container")

def create_overtime_chart(monthly_data):
    if not monthly_data:
        return {}
    
    months = [m.get('month', '') for m in monthly_data]
    overtime = [m.get('overtime_hours', 0) for m in monthly_data]
    
    return {
        'data': [go.Bar(x=months, y=overtime, marker_color=colors['accent'])],
        'layout': go.Layout(
            title='Monthly Overtime Hours',
            xaxis={'title': 'Month'},
            yaxis={'title': 'Hours'},
            height=300,
            margin={'l': 40, 'b': 40, 't': 50, 'r': 10}
        )
    }

def create_leave_balance_chart(leave_balance):
    if not leave_balance:
        return {}
    
    leave_types = ['Annual', 'Parental', 'Paternity', 'Bereavement']
    leave_remaining = [
        leave_balance.get('annual_leave_balance', 0),
        leave_balance.get('parental_leave_balance', 0),
        leave_balance.get('paternity_leave_balance', 0),
        leave_balance.get('bereavement_leave_balance', 0)
    ]
    leave_total = [
        leave_balance.get('annual_leave_total', 0),
        leave_balance.get('parental_leave_total', 0),
        leave_balance.get('paternity_leave_total', 0),
        leave_balance.get('bereavement_leave_total', 0)
    ]
    leave_used = [t - r for t, r in zip(leave_total, leave_remaining)]
    
    return {
        'data': [
            go.Bar(x=leave_types, y=leave_remaining, name='Remaining', marker_color=colors['primary']),
            go.Bar(x=leave_types, y=leave_used, name='Used', marker_color=colors['accent'])
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

def create_leave_history_table(leave_history):
    if not leave_history:
        return html.Div("No leave history available")
    
    return html.Div([
        html.Table([
            html.Thead(html.Tr([html.Th(col) for col in ['Type', 'Start Date', 'End Date', 'Duration', 'Status']])),
            html.Tbody([
                html.Tr([
                    html.Td(row['leave_type']),
                    html.Td(row['start_date']),
                    html.Td(row['end_date']),
                    html.Td(f"{row['duration']} days"),
                    html.Td(html.Span(row['status'], className="status-badge approved"))
                ]) for row in leave_history
            ])
        ], className="data-table")
    ], className="table-container")

def create_radar_chart(radar_data):
    if not radar_data:
        return {}
    
    categories = ['Productivity', 'Attendance', 'Communication', 'Collaboration', 'Quality']
    values = [
        radar_data.get('productivity', 0),
        radar_data.get('attendance', 0),
        radar_data.get('communication', 0),
        radar_data.get('collaboration', 0),
        radar_data.get('quality', 0)
    ]
    
    return {
        'data': [
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Current',
                line_color=colors['primary']
            ),
            go.Scatterpolar(
                r=[75, 75, 75, 75, 75],
                theta=categories,
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

# Add CSS styling for the dashboard
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

# Run the app
if __name__ == '__main__':
    app.run(debug=True , port="8051")