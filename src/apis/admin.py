import psycopg2
import pandas as pd
from datetime import timedelta, datetime

### helper functions ###
def connect():
    conn = psycopg2.connect(host = "localhost", port = "5432", dbname = "music_player")
    cur = conn.cursor()
    return conn, cur

def quit(conn, cur):
    cur.close()
    conn.close()

### admin functions ###
def get_user_stats():
    conn, cur = connect()

    #user_input = input("Please enter the end date (mm/dd/yyyy) of the week you want to lookup: ")
    #user_input.split('/')

    query = """select week_end, avg(active_hours) as avg_content_hour, count(user_email) as num_of_active_user
               from user_stats
               group by week_end
               order by week_end DESC;"""
    #end_date = datetime(user_input[2], user_input[0], user_input[1])
    print(pd.read_sql(query,conn))
    quit(conn, cur)

def get_song_stats():
    conn, cur = connect()
    user_input = input("Please enter the end date (mm/dd/yyyy) of the week you want to lookup: ")
    user_input = user_input.split("/")

    try:
        end_date = datetime(int(user_input[2]), int(user_input[0]), int(user_input[1]))
    except:
        print("Please enter the end date in the format mm/dd/yyyy.")
        return

    query = """select * from (select * from song_stats where week_end >= %s and week_end < %s) as T
               join (select song_id, title, artist, language from song) as S on T.song_id = S.song_id
               order by hit_rate DESC;"""

    results = pd.read_sql(query,conn, params=(end_date, end_date + timedelta(hours=24)))
    if len(results) > 0:
        print(results)
    else:
        print("Week does not exist.")

    quit(conn, cur)

def get_user_subscription():
    conn, cur = connect()
    user_input = input("Please enter the user email: ").strip()

    query = """select * from have_privilege where user_email = %s;"""
    results = pd.read_sql(query, conn, params=(user_input,))
    if len(results):
        print(results)
    else:
        print(f"User {user_input} does not exist.")
    quit(conn, cur)

def get_publisher_contract():
    user_input = input("Please enter the publisher ID: ").strip()
    try:
      song_id = int(user_input)
    except ValueError:
      print("Invalid Input: publisher id has to be an integer.")
      return

    conn, cur = connect()

    publisher_query = "select * from publisher where publisher_id = %s"
    cur.execute(publisher_query, (user_input,))
    if not cur.fetchone():
        print(f"Publisher {user_input} does not exist.")
        return

    query = """select P.publisher_id, P.publisher_name, C.contract_id, C.contract_title, C.start_date, C.end_date from contract_t as C join publisher as P on C.publisher_id = P.publisher_id where C.publisher_id = %s;"""
    results = pd.read_sql(query, conn, params=(user_input,))
    if len(results):
        print(results)
    else:
        print(f"There is no contract associated with publisher {user_input}.")

    quit(conn, cur)


#get_user_stats()
#get_song_stats()
#get_user_subscription()
#get_publisher_contract()
