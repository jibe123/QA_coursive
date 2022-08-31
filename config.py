from decouple import config

# TELEGRAM BOT
ADMIN_USER_ID = config('ADMIN_USER_ID')
TOKEN = config('TOKEN')

# MYSQL DATABASE
MYSQL_DATABASE = config('MYSQL_DATABASE')
MYSQL_USER = config('MYSQL_USER')
MYSQL_PASSWORD = config('MYSQL_PASSWORD')
MYSQL_HOST = config('MYSQL_HOST')