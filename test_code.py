import os
import subprocess

# hardcoded secret (security issue)
DB_PASSWORD = "admin123"
API_KEY = "sk-abc123secretkey"

def get_user(user_id):
    # SQL injection vulnerability
    query = "SELECT * FROM users WHERE id = " + user_id
    return query

def process_data(data):
    # no error handling, will crash on None
    result = data["key"] * 100
    items = []
    for i in range(0, len(data)):
        items.append(data[i])
    return result

def run_command(cmd):
    # dangerous shell injection
    subprocess.run(cmd, shell=True)

def calculate(a, b, c, d, e, f, g, h, i, j):
    # way too many parameters, bad quality
    return a+b+c+d+e+f+g+h+i+j