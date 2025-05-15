import mysql.connector
from mysql.connector import Error

try:
    # Connect to MySQL
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="iron",
    )

    cursor = db.cursor()

    # Create Database if it doesn't exist
    cursor.execute("DROP DATABASE IF EXISTS bot_memory")
    cursor.execute("CREATE DATABASE IF NOT EXISTS bot_memory")

    db.database = "bot_memory"

    # Create Bots Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bots (
            id INT AUTO_INCREMENT PRIMARY KEY,
            discord_id BIGINT NOT NULL,
            name VARCHAR(255) NOT NULL,
            alias VARCHAR(255),
            avatar_url VARCHAR(255)
        )
    """
    )

    # Create Memories Table (Fixed foreign key syntax)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bot_memories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            bot_id INT,
            special_phrase VARCHAR(255),
            memory TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE
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

    # Create Personality Traits Table (Added unique constraint for bot_id)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS personality_traits (
            id INT AUTO_INCREMENT PRIMARY KEY,
            bot_id INT UNIQUE,
            name VARCHAR(255),
            age VARCHAR(50),
            role VARCHAR(255),
            description TEXT,
            likes TEXT,
            dislikes TEXT,
            FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE
        )
    """
    )

    db.commit()
    print("Database and tables created successfully")

except Error as e:
    print(f"Error: {e}")

finally:
    if "cursor" in locals():
        cursor.close()
    if "db" in locals():
        db.close()
    print("MySQL connection closed")
