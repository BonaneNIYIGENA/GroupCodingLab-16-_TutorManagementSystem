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
