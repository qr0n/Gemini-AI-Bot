import mysql.connector

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="iron",
    database="bot_memory"
)

cursor = db.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS bot_memory")

cursor.execute("DROP TABLE memories")

cursor.execute(
"""
CREATE TABLE memories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    special_phrase TEXT NOT NULL,
    memory TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
)