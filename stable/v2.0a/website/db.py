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

# Reconnect to the MySQL server, this time specifying the database
db.database = "bot_memory"

# Create Bots Table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS bots (
        id INT AUTO_INCREMENT PRIMARY KEY,
        discord_id BIGINT NOT NULL
        avatar_url VARCHAR(255)
    )
    """
)
# Create Memories Table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS bot_memories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        bot_id INT,
        special_phrase VARCHAR(255),
        memory TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (bot_id) REFERENCES bots(id)
        FOREIGN KEY (discord_id) REFRENCES bots(id)
    )
    """
)
# Create Users Table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)
# Commit changes
db.commit()

# Close the cursor and connection
cursor.close()
db.close()
