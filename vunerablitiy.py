from dash import Dash, html, dcc, Input, Output
import sqlite3
import os
import json
from flask import request

# Vulnerable application with intentional flaws aligned to OWASP Top 10
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # To integrate with any WSGI server if needed
go_back = "Go back to Home"

# Vulnerable SQLite database setup
DATABASE_PATH = "vulnerable.db"
if not os.path.exists(DATABASE_PATH):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
    conn.commit()
    conn.close()

# Application layout
def index_layout():
    return html.Div([
        html.H1("Vulnerable Dash Application - OWASP Top 10"),
        html.Div([
            dcc.Link("Go to SQL Injection Page", href="/sql-injection"), html.Br(),
            dcc.Link("Go to XSS Page", href="/xss"), html.Br(),
            dcc.Link("Go to File Upload Page", href="/file-upload"), html.Br(),
            dcc.Link("Go to Broken Access Control Page", href="/access-control"), html.Br(),
        ]),
    ])

def sql_injection_layout():
    return html.Div([
        html.H2("SQL Injection Page"),
        html.Label("Enter Username:"),
        dcc.Input(id="sql-username", type="text"),
        html.Label("Enter Password:"),
        dcc.Input(id="sql-password", type="password"),
        html.Button("Login", id="sql-login-btn"),
        html.Div(id="sql-login-output"),
        dcc.Link(go_back, href="/"),
    ])

def xss_layout():
    return html.Div([
        html.H2("XSS Page"),
        html.Label("Enter a comment:"),
        dcc.Input(id="xss-input", type="text"),
        html.Button("Submit", id="xss-submit-btn"),
        html.Div(id="xss-output"),
        dcc.Link(go_back, href="/"),
    ])

def file_upload_layout():
    return html.Div([
        html.H2("File Upload Page"),
        dcc.Upload(
            id='upload-data',
            children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
        ),
        html.Div(id="upload-output"),
        dcc.Link(go_back, href="/"),
    ])

def access_control_layout():
    return html.Div([
        html.H2("Broken Access Control Page"),
        html.Label("Enter Secret Code:"),
        dcc.Input(id="access-code", type="text"),
        html.Button("Access", id="access-control-btn"),
        html.Div(id="access-control-output"),
        dcc.Link(go_back, href="/"),
    ])

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])

# Callbacks for navigation
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/sql-injection":
        return sql_injection_layout()
    elif pathname == "/xss":
        return xss_layout()
    elif pathname == "/file-upload":
        return file_upload_layout()
    elif pathname == "/access-control":
        return access_control_layout()
    else:
        return index_layout()

# Vulnerable SQL Injection Callback
@app.callback(
    Output("sql-login-output", "children"),
    [Input("sql-login-btn", "n_clicks")],
    [Input("sql-username", "value"), Input("sql-password", "value")]
)
def sql_injection_login(n_clicks, username, password):
    if n_clicks:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print("Executing query:", query)  # For debugging purposes
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            conn.close()
            if result:
                return "Login successful! Welcome, " + result[1]
            else:
                return "Login failed! Incorrect credentials."
        except Exception as e:
            return f"Error: {e}"
    return ""

# Vulnerable XSS Callback
@app.callback(
    Output("xss-output", "children"),
    [Input("xss-submit-btn", "n_clicks")],
    [Input("xss-input", "value")]
)
def handle_xss(n_clicks, comment):
    if n_clicks:
        return f"Comment submitted: {comment}"
    return ""

# Vulnerable File Upload Callback
@app.callback(
    Output("upload-output", "children"),
    [Input("upload-data", "contents")]
)
def handle_file_upload(contents):
    if contents:
        return "File uploaded successfully!"
    return ""

# Broken Access Control Example
@app.callback(
    Output("access-control-output", "children"),
    [Input("access-control-btn", "n_clicks")],
    [Input("access-code", "value")]
)
def broken_access_control(n_clicks, code):
    if n_clicks:
        if code == "1234":
            return "Access granted to sensitive information!"
        else:
            return "Access denied! Incorrect code."
    return ""


if __name__ == '__main__':
    app.run_server(debug=True, host="172.28.112.1")
