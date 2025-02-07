import mysql.connector

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace with your username
    password="iron",  # Replace with your password
    # Do not specify the database here
)

cursor = db.cursor()

# Create Database if it doesn't exist
cursor.execute("CREATE DATABASE IF NOT EXISTS bot_memory")

cursor.close()

cursor = db.cursor()
# Reconnect to the MySQL server, this time specifying the database
db.database = "bot_memory"

# Create Memories Table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS memories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        channel_id VARCHAR(255) NOT NULL,
        special_phrase TEXT NOT NULL,
        memory TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS bot_db (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_content TEXT NOT NULL,
    message_id BIGINT NOT NULL,
    jump_url TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS reminders (
    reminder_name TEXT NOT NULL,
    reminder_time DATETIME,
    channel_id BIGINT NOT null,
    message_author BIGINT not null
    );

    """,
    multi=True,
)

# Commit changes
db.commit()

# Close the cursor and connection
cursor.close()
db.close()
