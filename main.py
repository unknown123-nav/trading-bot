import time
from bot_engine import run_bots
import mysql.connector

conn = mysql.connector.connect(
    host="hopper.proxy.rlwy.net",
    user="root",
    password="LygrVoBHOocJwSIDejJqBNVIjbziUGxo",   
    database="railway",
    port=28847
)

print("Connected to Railway DB ")
print("Python Bot Engine Started")

while True:
    try:
        run_bots()
    except Exception as e:
        print("ERROR:", e)

    time.sleep(60)
