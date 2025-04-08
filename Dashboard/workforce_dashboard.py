import dash
from dash import dcc, html, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json

def create_dash_app(flask_app):
    """Factory function to create Dash application"""
    dash_app = dash.Dash(
        server=flask_app,
        url_base_pathname='/dash-app/',
        suppress_callback_exceptions=True,
        assets_folder=flask_app.config['STATIC_FOLDER']
    )

    # Add custom CSS styles to the Dash app
    dash_app.index_string = '''
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

    def generate_sample_data():
        """Generate sample employee data with Danish leave policies"""
        departments = ['Engineering', 'Architecture', 'Sales', 'HR', 'Finance']
        employees = []
        
        for i in range(1, 101):
            emp_id = f"EMP{i:03d}"
            dept = np.random.choice(departments)
            months_employed = np.random.randint(1, 61)
            
            # Danish leave calculations
            annual_leave_total = min(round(2.08 * months_employed, 1), 25)
            sick_leave_taken = np.random.randint(0, 8)
            parental_leave_total = 32
            paternity_leave_total = 2
            bereavement_leave_total = 3
            
            # Random leaves taken
            annual_taken = np.random.randint(0, int(annual_leave_total) + 1) if annual_leave_total > 0 else 0
            parental_taken = np.random.randint(0, parental_leave_total + 1) if np.random.random() < 0.15 else 0
            paternity_taken = np.random.randint(0, paternity_leave_total + 1) if np.random.random() < 0.1 else 0
            bereavement_taken = np.random.randint(0, bereavement_leave_total + 1) if np.random.random() < 0.05 else 0
            
            # Salary calculations
            base_salary = np.random.randint(30000, 60000)
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
        
        # Generate attendance data
        attendance = []
        danish_holidays = [
            "2025-01-01", "2025-04-17", "2025-04-18", "2025-04-21",
            "2025-05-16", "2025-05-29", "2025-06-09", "2025-12-25", "2025-12-26"
        ]
        
        for day in range(30):
            date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
            is_holiday = date in danish_holidays
            
            for emp in employees:
                if is_holiday:
                    status = 'Public Holiday'
                    check_in = check_out = None
                    overtime_hours = 0
                elif np.random.random() > 0.1:
                    check_in = f"{np.random.randint(7, 10)}:{np.random.randint(0, 60):02d}"
                    check_out = f"{np.random.randint(16, 19)}:{np.random.randint(0, 60):02d}"
                    overtime_hours = max(0, int(check_out.split(':')[0]) - 17)
                    status = 'Late' if check_in > '09:00' else 'On Time'
                else:
                    status = 'Absent'
                    check_in = check_out = None
                    overtime_hours = 0
                
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
        
        # Generate leave data
        leave_types = ['Annual Leave', 'Sick Leave', 'Parental Leave', 'Paternity Leave', 'Bereavement Leave']
        leave_weights = [0.6, 0.25, 0.05, 0.05, 0.05]
        leaves = []
        
        for emp in employees:
            for _ in range(np.random.randint(0, 6)):
                start_date = (datetime.now() - timedelta(days=np.random.randint(1, 60))).strftime('%Y-%m-%d')
                leave_type = np.random.choice(leave_types, p=leave_weights)
                
                if leave_type == 'Annual Leave':
                    duration = np.random.randint(1, 10)
                elif leave_type == 'Sick Leave':
                    duration = np.random.randint(1, 5)
                elif leave_type == 'Parental Leave':
                    duration = np.random.randint(10, 32*7+1)
                elif leave_type == 'Paternity Leave':
                    duration = np.random.randint(1, 15)
                else:
                    duration = np.random.randint(1, 6)
                    
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

    def get_weather_data(location="Copenhagen"):
        """Mock weather data for demonstration"""
        weather_conditions = ['Clear', 'Clouds', 'Rain', 'Snow', 'Thunderstorm']
        return {
            "weather": [{"main": np.random.choice(weather_conditions)}],
            "main": {
                "temp": np.random.randint(-5, 25),
                "feels_like": np.random.randint(-5, 25),
                "humidity": np.random.randint(30, 90)
            },
            "wind": {"speed": np.random.randint(0, 15)},
            "dt": datetime.now().timestamp(),
            "name": location
        }

    def generate_ai_insights(employees_df, attendance_df, leaves_df, overtime_df):
        """Generate analytical insights about workforce"""
        # Department insights
        department_insights = []
        for dept in employees_df['department'].unique():
            dept_employees = employees_df[employees_df['department'] == dept]
            dept_attendance = attendance_df[attendance_df['employee_id'].isin(dept_employees['employee_id'])]
            
            avg_performance = dept_employees['performance_score'].mean()
            perf_comment = "above" if avg_performance > 85 else "below" if avg_performance < 75 else "at"
            
            attendance_pct = (dept_attendance['status'].isin(['On Time', 'Late']).sum() / len(dept_attendance)) * 100
            late_pct = (dept_attendance['status'] == 'Late').sum() / len(dept_attendance) * 100
            avg_overtime = overtime_df[overtime_df['employee_id'].isin(dept_employees['employee_id'])]['total_overtime_hours'].mean()
            
            department_insights.append({
                'department': dept,
                'performance': f"{avg_performance:.1f} ({perf_comment} company average)",
                'attendance': f"{attendance_pct:.1f}%",
                'late_arrivals': f"{late_pct:.1f}%",
                'avg_overtime': f"{avg_overtime:.1f} hours",
                'recommendation': "Consider team-building activities" if avg_performance < 75 else "High performing team" if avg_performance > 85 else "Stable performance"
            })
        
        # Individual insights
        individual_insights = []
        for _, emp in employees_df.iterrows():
            emp_id = emp['employee_id']
            emp_attendance = attendance_df[attendance_df['employee_id'] == emp_id]
            attendance_pct = (emp_attendance['status'].isin(['On Time', 'Late']).sum() / len(emp_attendance)) * 100
            late_pct = (emp_attendance['status'] == 'Late').sum() / len(emp_attendance) * 100
            emp_overtime = overtime_df[overtime_df['employee_id'] == emp_id]['total_overtime_hours'].values[0]
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
        
        # Weather impact analysis
        weather_impact = {
            'attendance': attendance_df['weather_impact'].value_counts(normalize=True).to_dict(),
            'leaves': leaves_df['weather_impact'].value_counts(normalize=True).to_dict(),
            'overtime': overtime_df['weather_impact'].value_counts(normalize=True).to_dict()
        }
        
        return {
            'department_insights': department_insights,
            'individual_insights': individual_insights,
            'weather_impact': weather_impact
        }

    # Generate data and insights
    ai_insights = generate_ai_insights(df_employees, df_attendance, df_leaves, df_overtime)
    weather_data = get_weather_data()

    # Dashboard layout
    dash_app.layout = html.Div([
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
                    html.Ul([html.Li(f"{k}: {v*100:.1f}%") for k, v in ai_insights['weather_impact']['attendance'].items()]),
                    html.P("Leave Impact:"),
                    html.Ul([html.Li(f"{k}: {v*100:.1f}%") for k, v in ai_insights['weather_impact']['leaves'].items()]),
                    html.P("Overtime Impact:"),
                    html.Ul([html.Li(f"{k}: {v*100:.1f}%") for k, v in ai_insights['weather_impact']['overtime'].items()])
                ])
            ], className="card", style={'flex': '1'}),
            
            html.Div([
                html.H3("AI-Powered Workforce Insights"),
                html.H4("Department Performance Summary"),
                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Department"), html.Th("Avg Performance"),
                        html.Th("Attendance"), html.Th("Late Arrivals"),
                        html.Th("Avg Overtime"), html.Th("Recommendation")
                    ])),
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
        
        # Main dashboard content
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
            
            # Dashboard sections (attendance, leaves, overtime, etc.)
            html.Div([
                html.Div([dcc.Graph(id='attendance-overview')], className="card"),
                html.Div([dcc.Graph(id='department-attendance')], className="card")
            ], className="row"),
            
            html.Div([html.Div([dcc.Graph(id='attendance-trends')], className="card")], className="row"),
            
            html.Div([
                html.Div([dcc.Graph(id='leave-distribution')], className="card"),
                html.Div([dcc.Graph(id='leave-status')], className="card")
            ], className="row"),
            
            html.Div([html.Div([dcc.Graph(id='overtime-analysis')], className="card")], className="row"),
            
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

    # Callbacks
    @dash_app.callback(
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
        colors = {
            'On Time': '#2ecc71',
            'Late': '#f39c12',
            'Absent': '#e74c3c',
            'Public Holiday': '#3498db'
        }
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

    # Add other callbacks here following the same pattern
    # ...

    return dash_app  # This must be the last line in the create_dash_app function