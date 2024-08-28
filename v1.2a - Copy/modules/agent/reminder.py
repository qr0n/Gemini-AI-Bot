"""
This file is how the bot handles reminders from modules/AIAgent.py
"""

import json
import mysql.connector

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

db_config = {
    'user': config["SQL_CREDENTIALS"]["username"],
    'password': config["SQL_CREDENTIALS"]["password"],
    'host': config["SQL_CREDENTIALS"]["host"],
    'database': config["SQL_CREDENTIALS"]["database"],
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

class Reminder:

    async def add_reminder(reminder_name, reminder_time, reminder_channel_id, reminder_message_author):
        """
        Description:
        This function adds a reminder to the database along a name, and time.
        
        Arguments:
        reminder_name : str
        reminder_time : str
        reminder_channel_id : int
        reminder_message_author : int
        
        Returns:
        TODO
        """
        sql = """INSERT INTO reminders (reminder_name, reminder_time, channel_id, message_author) VALUES (%s, %s, %s, %s)"""
        values = (reminder_name, reminder_time, reminder_channel_id, reminder_message_author)

        cursor.execute(sql, values)
        conn.commit()

        print("[Reminder] Executed query")


