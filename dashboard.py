import dash
from dash import dcc, html, Input, Output, State, callback
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime
import calendar
import requests
from db_connection import create_db_connection, execute_read_query, execute_query, DB_HOST, DB_USER, DB_PASS, DB_NAME

# Create database connection
connection = create_db_connection(DB_HOST, DB_USER, DB_PASS, DB_NAME)

# Function to fetch employee data
def fetch_employee_data(employee_id):
    query = """
    SELECT * FROM userss 
    WHERE employee_id = %s
    """
    params = (employee_id,)
    result = execute_read_query(connection, query, params)
    
    if result:
        return pd.DataFrame(result)
    return None

# Function to fetch attendance data
def fetch_attendance_data(employee_id, limit=5):
    query = """
    SELECT date, check_in, check_out, overtime_hours, status
    FROM attendances 
    WHERE employee_id = %s
    ORDER BY date DESC
    LIMIT %s
    """
    params = (employee_id, limit)
    result = execute_read_query(connection, query, params)
    
    if result:
        return pd.DataFrame(result)
    return None

# Function to fetch leave data
def fetch_leave_data(employee_id):
    query = """
    SELECT leave_type, start_date, end_date, duration, status
    FROM leaves 
    WHERE employee_id = %s
    ORDER BY start_date DESC
    """
    params = (employee_id,)
    result = execute_read_query(connection, query, params)
    
    if result:
        return pd.DataFrame(result)
    return None

# Function to fetch performance data
def fetch_performance_data(employee_id, months=6):
    query = """
    SELECT month, year, performance_score, attendance_score, overtime_hours,
           productivity_score, communication_score, collaboration_score, quality_score
    FROM performance 
    WHERE employee_id = %s
    ORDER BY year DESC, FIELD(month, 'Dec', 'Nov', 'Oct', 'Sep', 'Aug', 'Jul', 'Jun', 'May', 'Apr', 'Mar', 'Feb', 'Jan')
    LIMIT %s
    """
    params = (employee_id, months)
    result = execute_read_query(connection, query, params)
    
    if result:
        return pd.DataFrame(result)
    return None

# Function to fetch AI task recommendations
def fetch_ai_tasks(employee_id):
    query = """
    SELECT priority, task, deadline, status
    FROM ai_tasks 
    WHERE employee_id = %s
    ORDER BY 
        CASE 
            WHEN priority = 'High' THEN 1
            WHEN priority = 'Medium' THEN 2
            WHEN priority = 'Low' THEN 3
            ELSE 4
        END,
        deadline ASC
    """
    params = (employee_id,)
    result = execute_read_query(connection, query, params)
    
    if result:
        return result
    return []

# Function to create a new AI task
def create_ai_task(employee_id, priority, task, deadline, status):
    query = """
    INSERT INTO ai_tasks (employee_id, priority, task, deadline, status)
    VALUES (%s, %s, %s, %s, %s)
    """
    params = (employee_id, priority, task, deadline, status)
    return execute_query(connection, query, params)

# Helper function to calculate months employed
def calculate_months_employed(join_date):
    today = datetime.date.today()
    join_date = datetime.datetime.strptime(join_date, '%Y-%m-%d').date()
    months = (today.year - join_date.year) * 12 + (today.month - join_date.month)
    return months

# Use weather API function from original code
def get_weather_data(api_key, city_name, units='metric'):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units={units}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_info = {
            'current': {
                'temp': data['main']['temp'],
                'condition': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'icon': get_weather_icon(data['weather'][0]['icon'])
            }
        }
        return weather_info
    else:
        return None

def get_weather_icon(icon_code):
    mapping = {
        "01d": "☀️", "01n": "🌙", "02d": "⛅", "02n": "☁️",
        "03d": "☁️", "03n": "☁️", "04d": "☁️", "04n": "☁️",
        "09d": "🌧️", "09n": "🌧️", "10d": "🌦️", "10n": "🌧️",
        "11d": "⛈️", "11n": "⛈️", "13d": "❄️", "13n": "❄️",
        "50d": "🌫️", "50n": "🌫️"
    }
    return mapping.get(icon_code, "☁️")
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Employee Dashboard"

# Layout with tabs for better organization (keep from original code but with dynamic data)
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H2("Employee Dashboard", style={"margin-bottom": "10px"}),
            html.H3(f"Welcome, {df_employees['name'][0]} ({df_employees['employee_id'][0]})", 
                    style={"color": colors['text'], "font-weight": "normal"})
        ], style={"display": "flex", "flex-direction": "column", "align-items": "center"}),
        
        dcc.Tabs(id='dashboard-tabs', value='overview', children=[
            dcc.Tab(label='Overview', value='overview'),
            dcc.Tab(label='Attendances', value='attendances'),
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
                            html.H5(df_employees['months_employed'])
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
                            html.P("Attendances"),
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
                                name='Attendances',
                                line=dict(color=colors['secondary'], width=3),
                                marker=dict(size=8)
                            )
                        ],
                        'layout': go.Layout(
                            title='Performance & Attendances Trends',
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
    
    elif tab == 'attendances':
        return html.Div([
            html.Div([
                html.Div([
                    html.H4("Recent Attendances", className="card-title"),
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
                                ]) for _, row in df_attendances.iterrows()
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
                                r=radar_data,
                                theta=['Productivity', 'Attendances', 'Communication', 'Collaboration', 'Quality'],
                                fill='toself',
                                name='Current',
                                line_color=colors['primary']
                            ),
                            go.Scatterpolar(
                                r=[75, 75, 75, 75, 75],
                                theta=['Productivity', 'Attendances', 'Communication', 'Collaboration', 'Quality'],
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
            ], className="card"),
            
            # Add monthly performance trend
            html.Div([
                html.H4("Monthly Performance Detail", className="card-title"),
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='performance-detail-graph',
                            figure={
                                'data': [
                                    go.Bar(
                                        x=months,
                                        y=performance_data,
                                        name='Performance',
                                        marker_color=colors['primary']
                                    )
                                ],
                                'layout': go.Layout(
                                    title='Monthly Performance Score',
                                    xaxis={'title': 'Month'},
                                    yaxis={'title': 'Score', 'range': [60, 100]},
                                    height=300,
                                    margin={'l': 40, 'b': 40, 't': 50, 'r': 10}
                                )
                            }
                        )
                    ], className="flex-1"),
                    
                    html.Div([
                        dcc.Graph(
                            id='productivity-comparison-graph',
                            figure={
                                'data': [
                                    go.Bar(
                                        x=months,
                                        y=[88, 82, 85, 93, 91, 89],
                                        name='You',
                                        marker_color=colors['primary']
                                    ),
                                    go.Bar(
                                        x=months,
                                        y=[79, 80, 81, 82, 83, 81],
                                        name='Department Average',
                                        marker_color=colors['accent'],
                                        opacity=0.7
                                    )
                                ],
                                'layout': go.Layout(
                                    title='You vs. Department Average',
                                    xaxis={'title': 'Month'},
                                    yaxis={'title': 'Score', 'range': [60, 100]},
                                    barmode='group',
                                    height=300,
                                    margin={'l': 40, 'b': 40, 't': 50, 'r': 10},
                                    legend={'orientation': 'h', 'y': -0.2}
                                )
                            }
                        )
                    ], className="flex-1")
                ], className="card-row"),
            ], className="card"),
            
            # Performance feedback and improvement suggestions
            html.Div([
                html.H4("AI Performance Insights", className="card-title"),
                html.Div([
                    html.Div([
                        html.H5("Strengths", style={"color": colors['secondary'], "margin-bottom": "10px"}),
                        html.Ul([
                            html.Li("Excellent attendances record with 98% consistency"),
                            html.Li("Strong attention to detail in financial reporting"),
                            html.Li("Effective time management during high-pressure periods")
                        ], style={"padding-left": "20px"})
                    ], className="flex-1"),
                    
                    html.Div([
                        html.H5("Growth Areas", style={"color": colors['accent'], "margin-bottom": "10px"}),
                        html.Ul([
                            html.Li("Consider reducing overtime hours for better work-life balance"),
                            html.Li("Opportunity to improve cross-departmental collaboration"),
                            html.Li("Potential to take more initiative in team meetings")
                        ], style={"padding-left": "20px"})
                    ], className="flex-1")
                ], className="card-row"),
                
                html.Div([
                    html.H5("Development Suggestions", style={"margin-bottom": "10px"}),
                    html.P("Based on your performance pattern, consider these development opportunities:"),
                    html.Div([
                        html.Div([
                            html.Div([
                                html.H6("Advanced Excel for Finance", className="suggestion-title"),
                                html.P("3-week online course to enhance financial modeling skills")
                            ], className="suggestion-card")
                        ], className="flex-1"),
                        html.Div([
                            html.Div([
                                html.H6("Leadership Communication", className="suggestion-title"),
                                html.P("2-day workshop on effective team communication")
                            ], className="suggestion-card")
                        ], className="flex-1"),
                        html.Div([
                            html.Div([
                                html.H6("Time Management Mastery", className="suggestion-title"),
                                html.P("1-day seminar on prioritization and productivity")
                            ], className="suggestion-card")
                        ], className="flex-1")
                    ], className="card-row", style={"margin-top": "15px"})
                ], style={"margin-top": "20px"})
            ], className="card")
        ])


@callback(
    Output('tab-content', 'children', allow_duplicate=True),
    Input('generate-tasks-btn', 'n_clicks'),
    State('dashboard-tabs', 'value'),
    prevent_initial_call=True
)
def generate_new_tasks(n_clicks, current_tab):
    if current_tab == 'overview':
        # Generate a new random task and save to database
        import random
        from datetime import datetime, timedelta
        
        # Task options
        task_options = [
            'Prepare monthly expense report',
            'Schedule team meeting for budget review',
            'Update quarterly forecasts',
            'Create presentation for management meeting',
            'Review invoices for payment processing',
            'Update department budget allocations',
            'Complete compliance training',
            'Review expense claims',
            'Prepare for performance review meeting',
            'Analyze departmental KPIs'
        ]
        
        priority_options = ['High', 'Medium', 'Low']
        
        # Generate random deadline in the next 30 days
        today = datetime.now()
        deadline = today + timedelta(days=random.randint(5, 30))
        deadline_str = deadline.strftime('%Y-%m-%d')
        
        # Create new task
        new_task = {
            'priority': random.choice(priority_options),
            'task': random.choice(task_options),
            'deadline': deadline_str,
            'status': 'New'
        }
        
        # Insert into database
        create_ai_task(EMPLOYEE_ID, new_task['priority'], new_task['task'], new_task['deadline'], new_task['status'])
        
        # Refresh tasks from database
        updated_tasks = fetch_ai_tasks(EMPLOYEE_ID)
        
        # Update global variable to reflect database state
        global ai_tasks
        ai_tasks = updated_tasks
        
        # Return the updated overview tab
        return render_tab_content('overview')
    
    return render_tab_content(current_tab)

# Request leave form modal
@callback(
    Output('tab-content', 'children', allow_duplicate=True),
    Input('request-leave-btn', 'n_clicks'),
    State('dashboard-tabs', 'value'),
    prevent_initial_call=True
)
def show_leave_request_modal(n_clicks, current_tab):
    # In a real implementation, you would show a modal for leave request
    # For now, we'll just return the same content with a mock confirmation
    if current_tab == 'leave':
        # Show a mock confirmation message
        return html.Div([
            html.Div([
                html.Div([
                    html.H4("Leave Request Form", className="card-title"),
                    html.Div([
                        html.Div([
                            html.Label("Leave Type"),
                            dcc.Dropdown(
                                id='leave-type-dropdown',
                                options=[
                                    {'label': 'Annual Leave', 'value': 'annual'},
                                    {'label': 'Sick Leave', 'value': 'sick'},
                                    {'label': 'Parental Leave', 'value': 'parental'},
                                    {'label': 'Bereavement Leave', 'value': 'bereavement'}
                                ],
                                value='annual'
                            )
                        ], className="form-group"),
                        html.Div([
                            html.Label("Start Date"),
                            dcc.DatePickerSingle(
                                id='leave-start-date',
                                date=datetime.datetime.now().date()
                            )
                        ], className="form-group"),
                        html.Div([
                            html.Label("End Date"),
                            dcc.DatePickerSingle(
                                id='leave-end-date',
                                date=datetime.datetime.now().date() + datetime.timedelta(days=1)
                            )
                        ], className="form-group"),
                        html.Div([
                            html.Label("Reason"),
                            dcc.Textarea(
                                id='leave-reason',
                                placeholder='Enter reason for leave...',
                                style={'width': '100%', 'height': 100}
                            )
                        ], className="form-group"),
                        html.Div([
                            html.Button('Submit Request', id='submit-leave-btn', className="action-button"),
                            html.Button('Cancel', id='cancel-leave-btn', className="cancel-button")
                        ], className="button-group")
                    ], className="form-container")
                ], className="card flex-1"),
                
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
                ], className="card flex-1")
            ], className="card-row"),
            
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
                ], className="table-container")
            ], className="card")
        ])
    
    return render_tab_content(current_tab)

# Submit leave request callback - This would insert into the database in a real app
@callback(
    Output('tab-content', 'children', allow_duplicate=True),
    Input('submit-leave-btn', 'n_clicks'),
    State('leave-type-dropdown', 'value'),
    State('leave-start-date', 'date'),
    State('leave-end-date', 'date'),
    State('leave-reason', 'value'),
    State('dashboard-tabs', 'value'),
    prevent_initial_call=True
)
def submit_leave_request(n_clicks, leave_type, start_date, end_date, reason, current_tab):
    if n_clicks and current_tab == 'leave':
        # In a real application, this would insert the leave request into the database
        # For now, just return a success message
        return html.Div([
            html.Div([
                html.Div([
                    html.H4("Request Submitted", className="card-title"),
                    html.Div([
                        html.P("Your leave request has been submitted successfully.", className="success-message"),
                        html.P(f"Leave type: {leave_type}", className="request-detail"),
                        html.P(f"Period: {start_date} to {end_date}", className="request-detail"),
                        html.Button('Back to Leave Management', id='back-to-leave-btn', className="action-button")
                    ], className="confirmation-container")
                ], className="card")
            ])
        ])
    
    return render_tab_content(current_tab)

# Cancel leave request callback - Just return to leave management tab
@callback(
    Output('tab-content', 'children', allow_duplicate=True),
    Input('cancel-leave-btn', 'n_clicks'),
    State('dashboard-tabs', 'value'),
    prevent_initial_call=True
)
def cancel_leave_request(n_clicks, current_tab):
    if n_clicks and current_tab == 'leave':
        return render_tab_content('leave')
    
    return render_tab_content(current_tab)

# Back to leave management callback
@callback(
    Output('tab-content', 'children', allow_duplicate=True),
    Input('back-to-leave-btn', 'n_clicks'),
    State('dashboard-tabs', 'value'),
    prevent_initial_call=True
)
def back_to_leave_management(n_clicks, current_tab):
    if n_clicks and current_tab == 'leave':
        return render_tab_content('leave')
    
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
            .cancel-button {
                background-color: #ecf0f1;
                color: #7f8c8d;
                border: none;
                padding: 10px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 500;
                margin-left: 10px;
                transition: background-color 0.3s;
            }
            .cancel-button:hover {
                background-color: #e0e0e0;
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
            /* Form styles */
            .form-group {
                margin-bottom: 15px;
            }
            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
            }
            .form-container {
                max-width: 100%;
            }
            .button-group {
                margin-top: 20px;
                display: flex;
                justify-content: flex-start;
            }
            .success-message {
                color: #27ae60;
                font-size: 1.1rem;
                margin-bottom: 15px;
            }
            .request-detail {
                margin: 5px 0;
                color: #7f8c8d;
            }
            .suggestion-card {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                height: 100%;
            }
            .suggestion-title {
                color: #2c3e50;
                margin-top: 0;
                margin-bottom: 8px;
            }
            .suggestion-card p {
                margin: 0;
                color: #7f8c8d;
                font-size: 0.9rem;
            }
            .confirmation-container {
                text-align: center;
                padding: 20px 0;
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