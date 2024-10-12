import sqlite3
import json
from datetime import datetime

connection = sqlite3.connect("database.db")
cursor = connection.cursor()


class DataBase:
    
    def create_table_users():
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY,
            telegram_id BIGINTEGER
            )
        ''')

    def create_table_applications():
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Applications (
            id INTEGER PRIMARY KEY,
            user_id BIGINTEGER,
            message_id TEXT,
            created DATETIME
            )
        ''')

    def create_table_answers():
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Answers (
            id INTEGER PRIMARY KEY,
            application_id INTEGER,
            message INTEGER,
            author BIGINTEGER
            )
        ''')
        
    def select_user(telegram_id):
        sql = 'SELECT * FROM Users WHERE telegram_id=?' 
        cursor.execute(sql, (telegram_id,))
        return cursor.fetchone()
    
    def add_user(telegram_id):
        sql = 'INSERT INTO Users (telegram_id) VALUES (?)' 
        cursor.execute(sql, (telegram_id,))     
        connection.commit()
        
    def add_application(user_id, message_id):
        # message_id = json.dumps(message_id)
        created = datetime.today().strftime('%y-%m-%d %H:%M')
        sql = 'INSERT INTO Applications (user_id, message_id, created) VALUES (?, ?, ?)' 
        cursor.execute(sql, (user_id, message_id, created,))     
        connection.commit()
    
    def update_application(app_id, message_id):
        sql = 'UPDATE Applications SET message_id=? WHERE id=?' 
        cursor.execute(sql, (message_id, app_id,))     
        connection.commit()
    
    def select_application(message_id):
        sql = 'SELECT * FROM Applications WHERE message_id=?' 
        cursor.execute(sql, (message_id,))
        return cursor.fetchone()
    
    def select_application_by_user(user_id, message_id):
        sql = 'SELECT * FROM Applications WHERE user_id=? AND message_id=?' 
        cursor.execute(sql, (user_id, message_id,))
        return cursor.fetchone()
    
    def select_application_by_id(user_id, id):
        sql = 'SELECT * FROM Applications WHERE user_id=? AND id=?' 
        cursor.execute(sql, (user_id, id,))
        return cursor.fetchone()
    
    def select_user_applications(user_id):
        sql = 'SELECT * FROM Applications WHERE user_id=?' 
        cursor.execute(sql, (user_id,))
        return cursor.fetchall()
    
    def add_app_message(application_id, message, author):
        created = datetime.today().strftime('%y-%m-%d %H:%M')
        sql = 'INSERT INTO Answers (application_id, message, author) VALUES (?, ?, ?)' 
        cursor.execute(sql, (application_id, message, author,))     
        connection.commit()
        
    def select_application_answers(application_id):
        sql = 'SELECT * FROM Answers WHERE application_id=?' 
        cursor.execute(sql, (application_id,))
        return cursor.fetchall()
