import mysql.connector

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="iron"
)

cursor = db.cursor()

print("Enter SQL query or 'exit' to quit.")

cursor.execute("CREATE DATABASE IF NOT EXISTS bot_memory")

cursor.execute(
"""
CREATE TABLE memories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    memory TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
)

cursor.execute("DROP DATABASE notes")