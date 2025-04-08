import dash
from dash import dcc, html, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Generate sample data for demonstration (modified for Danish leave policies)
def generate_sample_data():
    # Sample employee data
    departments = ['Engineering', 'Architecture', 'Sales', 'HR', 'Finance']
    employees = []
    for i in range(1, 101):
        emp_id = f"EMP{i:03d}"
        dept = np.random.choice(departments)
        
        # Calculate months of employment (random between 1-60 months)
        months_employed = np.random.randint(1, 61)
        
        # Danish leave entitlements
        # Annual leave: 2.08 days per month (25 days per year)
        annual_leave_total = round(2.08 * months_employed, 1)
        annual_leave_total = min(annual_leave_total, 25)  # Cap at 25 days
        
        # Sick leave: Full salary during sick leave (no limit)
        # For tracking purposes, we'll just record days taken
        sick_leave_taken = np.random.randint(0, 8)
        
        # Parental leave entitlements
        parental_leave_total = 32  # 32 weeks
        paternity_leave_total = 2   # 2 weeks
        
        # Bereavement leave 
        bereavement_leave_total = 3  # Typically 2-5 days
        
        # Random leaves taken
        annual_taken = np.random.randint(0, int(annual_leave_total) + 1) if annual_leave_total > 0 else 0
        parental_taken = np.random.randint(0, parental_leave_total + 1) if np.random.random() < 0.15 else 0
        paternity_taken = np.random.randint(0, paternity_leave_total + 1) if np.random.random() < 0.1 else 0
        bereavement_taken = np.random.randint(0, bereavement_leave_total + 1) if np.random.random() < 0.05 else 0
        
        # Calculate holiday allowance (12.5% of salary - simulated)
        base_salary = np.random.randint(30000, 60000)  # Base monthly salary in DKK
        holiday_allowance = round(base_salary * 0.125, 2)
        
        employees.append({
            'employee_id': emp_id,
            'name': f"Employee {i}",
            'department': dept,
            'join_date': (datetime.now() - timedelta(days=months_employed*30)).strftime('%Y-%m-%d'),
            'months_employed': months_employed,
            'base_salary': base_salary,
            'holiday_allowance': holiday_allowance,
            'annual_leave_total': annual_leave_total,
            'annual_leave_taken': annual_taken,
            'annual_leave_balance': annual_leave_total - annual_taken,
            'sick_leave_taken': sick_leave_taken,
            'parental_leave_total': parental_leave_total,
            'parental_leave_taken': parental_taken,
            'parental_leave_balance': parental_leave_total - parental_taken,
            'paternity_leave_total': paternity_leave_total,
            'paternity_leave_taken': paternity_taken,
            'paternity_leave_balance': paternity_leave_total - paternity_taken,
            'bereavement_leave_total': bereavement_leave_total,
            'bereavement_leave_taken': bereavement_taken,
            'bereavement_leave_balance': bereavement_leave_total - bereavement_taken,
            'performance_score': np.random.randint(70, 100),
            'engagement_score': np.random.randint(60, 95)
        })
    
    # Sample attendance data for the last 30 days
    attendance = []
    for day in range(30):
        date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
        
        # Check if it's a public holiday in Denmark (simplified list)
        danish_holidays = [
            "2025-01-01",  # New Year's Day
            "2025-04-17",  # Maundy Thursday
            "2025-04-18",  # Good Friday
            "2025-04-21",  # Easter Monday
            "2025-05-16",  # General Prayer Day
            "2025-05-29",  # Ascension Day
            "2025-06-09",  # Whit Monday
            "2025-12-25",  # Christmas Day
            "2025-12-26"   # Second Day of Christmas
        ]
        
        is_holiday = date in danish_holidays
        
        for emp in employees:
            # Some employees might be absent
            if is_holiday:
                check_in = None
                check_out = None
                overtime_hours = 0
                status = 'Public Holiday'
            elif np.random.random() > 0.1:  # 10% chance of absence
                check_in = f"{np.random.randint(7, 10)}:{np.random.randint(0, 60):02d}"
                check_out = f"{np.random.randint(16, 19)}:{np.random.randint(0, 60):02d}"
                
                # Calculate overtime (if any)
                check_out_hour = int(check_out.split(':')[0])
                overtime_hours = max(0, check_out_hour - 17)  # Assuming standard workday ends at 5 PM
                
                status = 'Late' if check_in > '09:00' else 'On Time'
            else:
                check_in = None
                check_out = None
                overtime_hours = 0
                status = 'Absent'
            
            attendance.append({
                'date': date,
                'employee_id': emp['employee_id'],
                'department': emp['department'],
                'check_in': check_in,
                'check_out': check_out,
                'overtime_hours': overtime_hours,
                'status': status,
                'weather_impact': np.random.choice(['None', 'Low', 'Medium', 'High'], p=[0.6, 0.2, 0.15, 0.05])
            })
    
    # Sample leave data
    leave_types = ['Annual Leave', 'Sick Leave', 'Parental Leave', 'Paternity Leave', 'Bereavement Leave']
    leave_weights = [0.6, 0.25, 0.05, 0.05, 0.05]  # Weighted probabilities
    leaves = []
    for emp in employees:
        # Each employee has some leave records
        for _ in range(np.random.randint(0, 6)):
            start_date = (datetime.now() - timedelta(days=np.random.randint(1, 60))).strftime('%Y-%m-%d')
            leave_type = np.random.choice(leave_types, p=leave_weights)
            
            # Duration based on leave type
            if leave_type == 'Annual Leave':
                duration = np.random.randint(1, 10)
            elif leave_type == 'Sick Leave':
                duration = np.random.randint(1, 5)
            elif leave_type == 'Parental Leave':
                duration = np.random.randint(10, 32*7+1)  # Up to 32 weeks (converting to days)
            elif leave_type == 'Paternity Leave':
                duration = np.random.randint(1, 15)  # Up to 2 weeks (in days)
            else:  # Bereavement
                duration = np.random.randint(1, 6)  # 1-5 days
                
            end_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=duration)).strftime('%Y-%m-%d')
            
            leaves.append({
                'employee_id': emp['employee_id'],
                'department': emp['department'],
                'leave_type': leave_type,
                'start_date': start_date,
                'end_date': end_date,
                'duration': duration,
                'status': np.random.choice(['Approved', 'Pending', 'Rejected'], p=[0.8, 0.15, 0.05]),
                'weather_impact': np.random.choice(['None', 'Low', 'Medium', 'High'], p=[0.7, 0.15, 0.1, 0.05])
            })
    
    # Generate overtime summary
    overtime = []
    for emp in employees:
        total_overtime = sum(record['overtime_hours'] for record in attendance if record['employee_id'] == emp['employee_id'])
        overtime.append({
            'employee_id': emp['employee_id'],
            'department': emp['department'],
            'total_overtime_hours': total_overtime,
            'avg_overtime_per_week': round(total_overtime / 4, 1),
            'weather_impact': np.random.choice(['None', 'Low', 'Medium', 'High'], p=[0.6, 0.2, 0.15, 0.05])
        })
    
    return pd.DataFrame(employees), pd.DataFrame(attendance), pd.DataFrame(leaves), pd.DataFrame(overtime)

# Generate sample data
df_employees, df_attendance, df_leaves, df_overtime = generate_sample_data()

# Function to get weather data (mock version - in production would use API)
def get_weather_data(location="Copenhagen"):
    # Mock data for demonstration
    weather_conditions = ['Clear', 'Clouds', 'Rain', 'Snow', 'Thunderstorm']
    return {
        "weather": [{"main": np.random.choice(weather_conditions)}],
        "main": {
            "temp": np.random.randint(-5, 25),
            "feels_like": np.random.randint(-5, 25),
            "humidity": np.random.randint(30, 90)
        },
        "wind": {
            "speed": np.random.randint(0, 15)
        },
        "dt": datetime.now().timestamp(),
        "name": location
    }

# Function to generate AI insights
def generate_ai_insights(employees_df, attendance_df, leaves_df, overtime_df):
    # Analyze attendance patterns
    attendance_rate = attendance_df[attendance_df['status'].isin(['On Time', 'Late'])].groupby('employee_id').size() / 30
    late_rate = attendance_df[attendance_df['status'] == 'Late'].groupby('employee_id').size() / 30
    
    # Analyze leave patterns
    sick_leave_trend = leaves_df[leaves_df['leave_type'] == 'Sick Leave'].groupby('employee_id')['duration'].sum()
    
    # Generate insights for each department
    department_insights = []
    for dept in employees_df['department'].unique():
        dept_employees = employees_df[employees_df['department'] == dept]
        dept_attendance = attendance_df[attendance_df['employee_id'].isin(dept_employees['employee_id'])]
        
        # Performance insights
        avg_performance = dept_employees['performance_score'].mean()
        perf_comment = "above" if avg_performance > 85 else "below" if avg_performance < 75 else "at"
        
        # Attendance insights
        attendance_pct = (dept_attendance['status'].isin(['On Time', 'Late']).sum() / len(dept_attendance)) * 100
        late_pct = (dept_attendance['status'] == 'Late').sum() / len(dept_attendance) * 100
        
        # Overtime insights
        avg_overtime = overtime_df[overtime_df['employee_id'].isin(dept_employees['employee_id'])]['total_overtime_hours'].mean()
        
        department_insights.append({
            'department': dept,
            'performance': f"{avg_performance:.1f} ({perf_comment} company average)",
            'attendance': f"{attendance_pct:.1f}%",
            'late_arrivals': f"{late_pct:.1f}%",
            'avg_overtime': f"{avg_overtime:.1f} hours",
            'recommendation': "Consider team-building activities" if avg_performance < 75 else "High performing team" if avg_performance > 85 else "Stable performance"
        })
    
    # Generate individual insights
    individual_insights = []
    for _, emp in employees_df.iterrows():
        emp_id = emp['employee_id']
        
        # Attendance
        emp_attendance = attendance_df[attendance_df['employee_id'] == emp_id]
        attendance_pct = (emp_attendance['status'].isin(['On Time', 'Late']).sum() / len(emp_attendance)) * 100
        late_pct = (emp_attendance['status'] == 'Late').sum() / len(emp_attendance) * 100
        
        # Overtime
        emp_overtime = overtime_df[overtime_df['employee_id'] == emp_id]['total_overtime_hours'].values[0]
        
        # Performance
        performance = emp['performance_score']
        perf_comment = "exceeds expectations" if performance > 85 else "needs improvement" if performance < 75 else "meets expectations"
        
        individual_insights.append({
            'employee_id': emp_id,
            'name': emp['name'],
            'attendance': f"{attendance_pct:.1f}%",
            'late_arrivals': f"{late_pct:.1f}%",
            'overtime': f"{emp_overtime} hours",
            'performance': f"{performance} ({perf_comment})",
            'recommendation': "Consider flexible hours" if late_pct > 20 else "Potential for leadership role" if performance > 90 else "Standard performance"
        })
    
    return {
        'department_insights': department_insights,
        'individual_insights': individual_insights,
        'weather_impact': {
            'attendance': attendance_df['weather_impact'].value_counts(normalize=True).to_dict(),
            'leaves': leaves_df['weather_impact'].value_counts(normalize=True).to_dict(),
            'overtime': overtime_df['weather_impact'].value_counts(normalize=True).to_dict()
        }
    }

# Generate AI insights
ai_insights = generate_ai_insights(df_employees, df_attendance, df_leaves, df_overtime)

# Get weather data
weather_data = get_weather_data()

# Dashboard layout
app.layout = html.Div([
    html.Div([
        html.H1("Danish Workforce Management Dashboard", className="dashboard-title"),
        html.P("Interactive analytics for attendance, leave management, and workforce planning", className="dashboard-subtitle"),
    ], className="header"),
    
    # Weather and AI Insights Row
    html.Div([
        html.Div([
            html.H3("Current Weather in Copenhagen"),
            html.Div([
                html.Div([
                    html.Img(src="https://openweathermap.org/img/wn/{}@2x.png".format(
                        '01d' if weather_data['weather'][0]['main'] == 'Clear' else
                        '02d' if weather_data['weather'][0]['main'] == 'Clouds' else
                        '09d' if weather_data['weather'][0]['main'] == 'Rain' else
                        '13d' if weather_data['weather'][0]['main'] == 'Snow' else
                        '11d'
                    ), style={'height': '50px'}),
                    html.Div([
                        html.H4(f"{weather_data['weather'][0]['main']}"),
                        html.P(f"Temperature: {weather_data['main']['temp']}°C"),
                        html.P(f"Feels like: {weather_data['main']['feels_like']}°C"),
                        html.P(f"Humidity: {weather_data['main']['humidity']}%"),
                        html.P(f"Wind: {weather_data['wind']['speed']} m/s")
                    ], style={'margin-left': '10px'})
                ], style={'display': 'flex', 'align-items': 'center'})
            ]),
            html.H4("Weather Impact Analysis"),
            html.Div([
                html.P("Attendance Impact:"),
                html.Ul([
                    html.Li(f"{k}: {v*100:.1f}%") for k, v in ai_insights['weather_impact']['attendance'].items()
                ]),
                html.P("Leave Impact:"),
                html.Ul([
                    html.Li(f"{k}: {v*100:.1f}%") for k, v in ai_insights['weather_impact']['leaves'].items()
                ]),
                html.P("Overtime Impact:"),
                html.Ul([
                    html.Li(f"{k}: {v*100:.1f}%") for k, v in ai_insights['weather_impact']['overtime'].items()
                ])
            ])
        ], className="card", style={'flex': '1'}),
        
        html.Div([
            html.H3("AI-Powered Workforce Insights"),
            html.H4("Department Performance Summary"),
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Department"),
                        html.Th("Avg Performance"),
                        html.Th("Attendance"),
                        html.Th("Late Arrivals"),
                        html.Th("Avg Overtime"),
                        html.Th("Recommendation")
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(insight['department']),
                        html.Td(insight['performance']),
                        html.Td(insight['attendance']),
                        html.Td(insight['late_arrivals']),
                        html.Td(insight['avg_overtime']),
                        html.Td(insight['recommendation'])
                    ]) for insight in ai_insights['department_insights']
                ])
            ], className="data-table")
        ], className="card", style={'flex': '2'})
    ], className="row"),
    
    # Original Dashboard Content
    html.Div([
        html.Div([
            dcc.DatePickerRange(
                id='date-range',
                start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                end_date=datetime.now().strftime('%Y-%m-%d'),
                display_format='YYYY-MM-DD'
            ),
            dcc.Dropdown(
                id='department-filter',
                options=[{'label': dept, 'value': dept} for dept in df_employees['department'].unique()],
                value=None,
                placeholder="Select Department"
            )
        ], className="filters"),
        
        html.Div([
            html.Div([
                html.H3("Attendance Overview"),
                dcc.Graph(id='attendance-overview')
            ], className="card"),
            
            html.Div([
                html.H3("Department Attendance"),
                dcc.Graph(id='department-attendance')
            ], className="card")
        ], className="row"),
        
        html.Div([
            html.Div([
                html.H3("Attendance Trends"),
                dcc.Graph(id='attendance-trends')
            ], className="card")
        ], className="row"),
        
        html.Div([
            html.Div([
                html.H3("Leave Distribution"),
                dcc.Graph(id='leave-distribution')
            ], className="card"),
            
            html.Div([
                html.H3("Leave Status"),
                dcc.Graph(id='leave-status')
            ], className="card")
        ], className="row"),
        
        html.Div([
            html.Div([
                html.H3("Overtime Analysis"),
                dcc.Graph(id='overtime-analysis')
            ], className="card")
        ], className="row"),
        
        html.Div([
            html.H3("Employee Records"),
            dcc.Dropdown(
                id='employee-filter',
                options=[{'label': f"{row['name']} ({row['employee_id']})", 'value': row['employee_id']} 
                         for _, row in df_employees.iterrows()],
                value=None,
                placeholder="Select Employee"
            ),
            html.Div(id='employee-records')
        ], className="card full-width")
    ], className="dashboard-content")
], className="dashboard-container")

# Callbacks to update dashboard components
@app.callback(
    Output('attendance-overview', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('department-filter', 'value')]
)
def update_attendance_overview(start_date, end_date, department):
    filtered_df = df_attendance[
        (df_attendance['date'] >= start_date) & 
        (df_attendance['date'] <= end_date)
    ]
    
    if department:
        filtered_df = filtered_df[filtered_df['department'] == department]
    
    status_counts = filtered_df['status'].value_counts()
    
    # Color scheme including public holidays
    colors = {
        'On Time': '#2ecc71',
        'Late': '#f39c12',
        'Absent': '#e74c3c',
        'Public Holiday': '#3498db'
    }
    
    # Get colors in the same order as status_counts
    marker_colors = [colors.get(status, '#95a5a6') for status in status_counts.index]
    
    fig = go.Figure(data=[
        go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=0.5,
            marker_colors=marker_colors
        )
    ])
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

@app.callback(
    Output('department-attendance', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('department-filter', 'value')]
)
def update_department_attendance(start_date, end_date, department):
    filtered_df = df_attendance[
        (df_attendance['date'] >= start_date) & 
        (df_attendance['date'] <= end_date)
    ]
    
    if department:
        filtered_df = filtered_df[filtered_df['department'] == department]
    
    dept_status = filtered_df.groupby(['department', 'status']).size().unstack(fill_value=0)
    
    fig = go.Figure()
    
    for status in dept_status.columns:
        fig.add_trace(go.Bar(
            x=dept_status.index,
            y=dept_status[status],
            name=status
        ))
    
    fig.update_layout(
        barmode='stack',
        xaxis_title="Department",
        yaxis_title="Number of Records",
        margin=dict(l=20, r=20, t=30, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

@app.callback(
    Output('attendance-trends', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('department-filter', 'value')]
)
def update_attendance_trends(start_date, end_date, department):
    filtered_df = df_attendance[
        (df_attendance['date'] >= start_date) & 
        (df_attendance['date'] <= end_date)
    ]
    
    if department:
        filtered_df = filtered_df[filtered_df['department'] == department]
    
    daily_status = filtered_df.groupby(['date', 'status']).size().unstack(fill_value=0).reset_index()
    daily_status = daily_status.sort_values('date')
    
    fig = go.Figure()
    
    for status in daily_status.columns[1:]:
        fig.add_trace(go.Scatter(
            x=daily_status['date'],
            y=daily_status[status],
            mode='lines+markers',
            name=status
        ))
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Employees",
        margin=dict(l=20, r=20, t=30, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

@app.callback(
    Output('leave-distribution', 'figure'),
    [Input('department-filter', 'value')]
)
def update_leave_distribution(department):
    filtered_df = df_leaves
    
    if department:
        filtered_df = filtered_df[filtered_df['department'] == department]
    
    leave_type_counts = filtered_df['leave_type'].value_counts()
    
    # Custom colors for Danish leave types
    colors = {
        'Annual Leave': '#3498db',
        'Sick Leave': '#e74c3c',
        'Parental Leave': '#9b59b6',
        'Paternity Leave': '#2ecc71',
        'Bereavement Leave': '#95a5a6'
    }
    
    # Get colors in the same order as leave_type_counts
    marker_colors = [colors.get(leave_type, '#95a5a6') for leave_type in leave_type_counts.index]
    
    fig = go.Figure(data=[
        go.Bar(
            x=leave_type_counts.index,
            y=leave_type_counts.values,
            marker_color=marker_colors
        )
    ])
    
    fig.update_layout(
        xaxis_title="Leave Type",
        yaxis_title="Number of Requests",
        margin=dict(l=20, r=20, t=30, b=40)
    )
    
    return fig

@app.callback(
    Output('leave-status', 'figure'),
    [Input('department-filter', 'value')]
)
def update_leave_status(department):
    filtered_df = df_leaves
    
    if department:
        filtered_df = filtered_df[filtered_df['department'] == department]
    
    status_counts = filtered_df['status'].value_counts()
    
    # Colors for leave statuses
    colors = {
        'Approved': '#2ecc71',
        'Pending': '#f39c12',
        'Rejected': '#e74c3c'
    }
    
    # Get colors in the same order as status_counts
    marker_colors = [colors.get(status, '#95a5a6') for status in status_counts.index]
    
    fig = go.Figure(data=[
        go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            marker_colors=marker_colors
        )
    ])
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

@app.callback(
    Output('overtime-analysis', 'figure'),
    [Input('department-filter', 'value')]
)
def update_overtime_analysis(department):
    filtered_df = df_overtime
    
    if department:
        filtered_df = filtered_df[filtered_df['department'] == department]
    
    # Sort by total overtime hours
    filtered_df = filtered_df.sort_values('total_overtime_hours', ascending=False).head(15)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=filtered_df['employee_id'],
        y=filtered_df['total_overtime_hours'],
        name='Total Overtime Hours',
        marker_color='#8e44ad'
    ))
    
    fig.update_layout(
        xaxis_title="Employee ID",
        yaxis_title="Overtime Hours",
        margin=dict(l=20, r=20, t=30, b=40),
        title="Top Employees by Overtime Hours"
    )
    
    return fig

@app.callback(
    Output('employee-records', 'children'),
    [Input('employee-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_employee_records(employee_id, start_date, end_date):
    if not employee_id:
        return html.P("Select an employee to view their records")
    
    filtered_attendance = df_attendance[
        (df_attendance['employee_id'] == employee_id) &
        (df_attendance['date'] >= start_date) & 
        (df_attendance['date'] <= end_date)
    ].sort_values('date', ascending=False)
    
    employee_info = df_employees[df_employees['employee_id'] == employee_id].iloc[0]
    employee_leaves = df_leaves[df_leaves['employee_id'] == employee_id]
    employee_overtime = df_overtime[df_overtime['employee_id'] == employee_id].iloc[0]
    ai_employee_insight = next((item for item in ai_insights['individual_insights'] if item['employee_id'] == employee_id), None)
    
    # Calculate overtime summary
    total_overtime = employee_overtime['total_overtime_hours']
    avg_weekly_overtime = employee_overtime['avg_overtime_per_week']
    
    # Style for progress bars
    progress_style = {
        "background-color": "#f1f1f1",
        "border-radius": "5px",
        "padding": "3px",
        "margin-bottom": "10px"
    }
    
    progress_bar_style = {
        "background-color": "#4caf50",
        "height": "24px",
        "border-radius": "3px",
        "color": "white",
        "text-align": "center",
        "line-height": "24px",
        "font-weight": "bold"
    }
    
    return html.Div([
        html.Div([
            html.H4(f"{employee_info['name']} ({employee_info['employee_id']})"),
            html.P(f"Department: {employee_info['department']}"),
            html.P(f"Join Date: {employee_info['join_date']}"),
            html.P(f"Months Employed: {employee_info['months_employed']}"),
            html.P(f"Base Monthly Salary: {employee_info['base_salary']} DKK"),
            html.P(f"Holiday Allowance (12.5%): {employee_info['holiday_allowance']} DKK"),
            
            html.Div([
                html.H4("AI-Powered Insights"),
                html.P(f"Performance: {ai_employee_insight['performance']}"),
                html.P(f"Attendance Rate: {ai_employee_insight['attendance']}"),
                html.P(f"Late Arrival Rate: {ai_employee_insight['late_arrivals']}"),
                html.P(f"Total Overtime: {ai_employee_insight['overtime']}"),
                html.P(f"Recommendation: {ai_employee_insight['recommendation']}")
            ], style={
                'background-color': '#f8f9fa',
                'padding': '15px',
                'border-radius': '5px',
                'margin-top': '15px',
                'border-left': '4px solid #3498db'
            })
        ], className="employee-info"),
        
        html.Div([
            html.H4("Leave Entitlements & Balance"),
            html.Div([
                html.Div("Annual Leave (2.08 days per month)", className="leave-type"),
                html.Div(style=progress_style, children=[
                    html.Div(
                        f"Balance: {employee_info['annual_leave_balance']} days of {employee_info['annual_leave_total']} accrued days",
                        style={
                            **progress_bar_style,
                            "width": f"{(employee_info['annual_leave_balance'] / employee_info['annual_leave_total']) * 100}%" if employee_info['annual_leave_total'] > 0 else "0%"
                        }
                    )
                ]),
                html.Div("Parental Leave (32 weeks total)", className="leave-type"),
                html.Div(style=progress_style, children=[
                    html.Div(
                        f"Balance: {employee_info['parental_leave_balance']} weeks",
                        style={
                            **progress_bar_style,
                            "width": f"{(employee_info['parental_leave_balance'] / employee_info['parental_leave_total']) * 100}%"
                        }
                    )
                ]),
                html.Div("Paternity Leave (2 weeks)", className="leave-type"),
                html.Div(style=progress_style, children=[
                    html.Div(
                        f"Balance: {employee_info['paternity_leave_balance']} weeks",
                        style={
                            **progress_bar_style,
                            "width": f"{(employee_info['paternity_leave_balance'] / employee_info['paternity_leave_total']) * 100}%"
                        }
                    )
                ]),
                html.Div("Bereavement Leave (3 days standard)", className="leave-type"),
                html.Div(style=progress_style, children=[
                    html.Div(
                        f"Balance: {employee_info['bereavement_leave_balance']} days",
                        style={
                            **progress_bar_style,
                            "width": f"{(employee_info['bereavement_leave_balance'] / employee_info['bereavement_leave_total']) * 100}%"
                        }
                    )
                ]),
                html.Div("Sick Leave Taken", className="leave-type"),
                html.P(f"Days taken this year: {employee_info['sick_leave_taken']} days (full salary during illness)")
            ]),
            
            html.Div([
                html.H4("Overtime Summary"),
                html.Div([
                    html.P(f"Total Overtime Hours: {total_overtime} hours"),
                    html.P(f"Average Weekly Overtime: {avg_weekly_overtime} hours")
                ], className="overtime-summary")
            ]),
            
            html.H4("Recent Attendance"),
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Date"),
                        html.Th("Check In"),
                        html.Th("Check Out"),
                        html.Th("Overtime"),
                        html.Th("Status")
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(row['date']),
                        html.Td(row['check_in'] if row['check_in'] else "-"),
                        html.Td(row['check_out'] if row['check_out'] else "-"),
                        html.Td(f"{row['overtime_hours']} hrs" if row['overtime_hours'] > 0 else "-"),
                        html.Td(row['status'])
                    ]) for _, row in filtered_attendance.head(10).iterrows()
                ])
            ], className="data-table"),
            
            html.H4("Leave History"),
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Type"),
                        html.Th("Start Date"),
                        html.Th("End Date"),
                        html.Th("Duration"),
                        html.Th("Status")
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(row['leave_type']),
                        html.Td(row['start_date']),
                        html.Td(row['end_date']),
                        html.Td(f"{row['duration']} {'days' if row['leave_type'] != 'Parental Leave' else 'days (' + str(round(row['duration']/7, 1)) + ' weeks)'}"),
                        html.Td(row['status'])
                    ]) for _, row in employee_leaves.iterrows()
                ])
            ], className="data-table")
        ], className="employee-records")
    ])

# CSS styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <title>Danish Workforce Management Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f7f9fc;
                color: #333;
            }
            .dashboard-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .dashboard-title {
                color: #2c3e50;
                margin-bottom: 0;
            }
            .dashboard-subtitle {
                color: #7f8c8d;
                margin-top: 10px;
            }
            .filters {
                display: flex;
                justify-content: space-between;
                margin-bottom: 20px;
                padding: 15px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            }
            .row {
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
            }
            .card {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
                flex: 1;
            }
            .full-width {
                flex-basis: 100%;
            }
            .card h3 {
                color: #2c3e50;
                margin-top: 0;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
            }
            .employee-info {
                margin-bottom: 20px;
            }
            .employee-records {
                margin-top: 20px;
            }
            .data-table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            .data-table th, .data-table td {
                border: 1px solid #eee;
                padding: 10px;
                text-align: left;
            }
            .data-table th {
                background-color: #f7f9fc;
            }
            .leave-type {
                font-weight: 500;
                margin-top: 10px;
                margin-bottom: 5px;
            }
            .overtime-summary {
                margin-bottom: 20px;
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #8e44ad;
            }
        </style>
    </body>
</html>
'''

# Start the app
if __name__ == '__main__':
    app.run(debug=True, port="8051")