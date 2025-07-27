import mysql.connector
import datetime
import hashlib
from mysql.connector import Error
from datetime import timedelta
import re


class TutoringSystem:
    def __init__(self):
        self.current_user_id = None
        self.current_user_role = None
        self.current_user_name = None
        self.connection = None
        self.connect_to_database()
        self.init_db()

    def get_db_config(self):
        """Returns database configuration"""
        return {
            'host': 'mysql-1579901e-alustudent-6e44.f.aivencloud.com',
            'port': 25379,
            'user': 'avnadmin',
            'password': 'AVNS_jqnnOJisae0B9tdYVj3',
            'database': 'tms',
            'ssl_disabled': False
        }

    def connect_to_database(self):
        """Establishes database connection and creates database if needed"""
        config = self.get_db_config()

        try:
            # First connect without specifying a database
            temp_connection = mysql.connector.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                ssl_disabled=config['ssl_disabled']
            )

            cursor = temp_connection.cursor()

            # Check if database exists
            cursor.execute(f"SHOW DATABASES LIKE '{config['database']}'")
            result = cursor.fetchone()

            if not result:
                # Create the database if it doesn't exist
                cursor.execute(f"CREATE DATABASE {config['database']}")
                print(f"Created database {config['database']}")

            cursor.close()
            temp_connection.close()

            # Now connect to the specific database
            self.connection = mysql.connector.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                ssl_disabled=config['ssl_disabled']
            )

            print("Successfully connected to database")

        except Error as e:
            print(f"Database connection failed: {e}")
            raise
