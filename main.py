import sqlite3
from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect("company.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Employees (
        ID INTEGER PRIMARY KEY,
        Name TEXT,
        Department TEXT,
        Salary INTEGER,
        Hire_Date TEXT
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Departments (
        ID INTEGER PRIMARY KEY,
        Name TEXT,
        Manager TEXT
    )""")
    
    cursor.executemany("INSERT INTO Employees (ID, Name, Department, Salary, Hire_Date) VALUES (?, ?, ?, ?, ?)", [
        (1, 'Alice', 'Sales', 50000, '2021-01-15'),
        (2, 'Bob', 'Engineering', 70000, '2020-06-10'),
        (3, 'Charlie', 'Marketing', 60000, '2022-03-20')
    ])
    
    cursor.executemany("INSERT INTO Departments (ID, Name, Manager) VALUES (?, ?, ?)", [
        (1, 'Sales', 'Alice'),
        (2, 'Engineering', 'Bob'),
        (3, 'Marketing', 'Charlie')
    ])
    
    conn.commit()
    conn.close()

init_db()

# Query processing
def process_query(user_input):
    user_input = user_input.lower()
    conn = sqlite3.connect("company.db")
    cursor = conn.cursor()

    # Match user input with predefined patterns
    if match := re.search(r"show me all employees in the (\w+) department", user_input):
        dept = match.group(1).capitalize()
        cursor.execute("SELECT Name FROM Employees WHERE Department=?", (dept,))
        result = cursor.fetchall()
        return jsonify([row[0] for row in result] or {"message": "No employees found in this department."})

    elif match := re.search(r"who is the manager of the (\w+) department", user_input):
        dept = match.group(1).capitalize()
        cursor.execute("SELECT Manager FROM Departments WHERE Name=?", (dept,))
        result = cursor.fetchone()
        return jsonify({"Manager": result[0]} if result else {"message": "Department not found."})

    elif match := re.search(r"list all employees hired after (\d{4}-\d{2}-\d{2})", user_input):
        date = match.group(1)
        cursor.execute("SELECT Name FROM Employees WHERE Hire_Date > ?", (date,))
        result = cursor.fetchall()
        return jsonify([row[0] for row in result] or {"message": "No employees found."})

    elif match := re.search(r"what is the total salary expense for the (\w+) department", user_input):
        dept = match.group(1).capitalize()
        cursor.execute("SELECT SUM(Salary) FROM Employees WHERE Department=?", (dept,))
        result = cursor.fetchone()
        return jsonify({"Total Salary Expense": result[0]} if result[0] else {"message": "Department not found or no salary data available."})
    
    else:
        return jsonify({"message": "Sorry, I didn't understand the query."})
    
    conn.close()

# Flask API route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("query")
    if not user_input:
        return jsonify({"error": "No query provided."})
    return process_query(user_input)

# Frontend UI route
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

