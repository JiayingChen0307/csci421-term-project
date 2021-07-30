import random
import string
import typer
from rich.progress import track
from rich import print
from datetime import datetime
import psycopg2


num_publisher = 10
num_contracts_per_publisher = 50
num_song_per_contract = 1000

weeks = [
  datetime(2021, 1, 1).strftime("%Y-%m-%d %H:%M:%S"),
  datetime(2021, 1, 7).strftime("%Y-%m-%d %H:%M:%S"),
  datetime(2021, 1, 14).strftime("%Y-%m-%d %H:%M:%S"),
  datetime(2021, 1, 21).strftime("%Y-%m-%d %H:%M:%S"),
  datetime(2021, 1, 28).strftime("%Y-%m-%d %H:%M:%S"),
  datetime(2021, 2, 4).strftime("%Y-%m-%d %H:%M:%S"),
  datetime(2021, 2, 11).strftime("%Y-%m-%d %H:%M:%S"),
  datetime(2021, 2, 18).strftime("%Y-%m-%d %H:%M:%S")]

num_versions = 3
versions = ['Normal', 'HD', 'Best']

num_user = 2000
users = []

privilege = ['User', 'VIP', 'Super VIP']
privilege_d = ['Normal Logged in user', 'VIP subscription', 'Supser VIP subscription']

num_play_list_per_user = 10
num_song_included = 40

# insert into f publishers id from 0 -> n-1
def generate_publishers(cur):
  for i in track(range(num_publisher), description="generating publishers..."):
    random_publisher_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
    cur.execute("insert into publisher values ({}, '{}');\n".format(i, random_publisher_name))

def generate_contract(cur):
  contract_id = 0
  for i in track(range(num_publisher), description="generating contracts for publisher"):
    for j in range(num_contracts_per_publisher):
      title = 'PUBLISHER_{}_CONTRACT_{}'.format(i, j)
      start_date = datetime(2021, 1, 1).strftime("%Y-%m-%d %H:%M:%S")
      end_date = datetime(2031, 1, 1).strftime("%Y-%m-%d %H:%M:%S")
      cur.execute("insert into contract_t values ({}, {}, '{}', '{}', '{}');\n".format(contract_id, i, title, start_date, end_date))
      contract_id += 1

def generate_song(cur):
  num_contracts = num_contracts_per_publisher * num_publisher
  song_id = 0
  for i in track(range(num_contracts), description="generating songs"):
    for j in range(num_song_per_contract):
      title = 'CONTRACT_{}_SONG_{}'.format(i, j)
      description = 'This is song {} from contract {}'.format(j, i)
      artist = ''.join(random.choices(string.ascii_letters, k=20))
      cur.execute("insert into song values ({}, {}, '{}', 'EN-US', '{}', '{}');\n".format(song_id, i, title, description, artist))
      song_id += 1
    
def generate_song_stat(cur):
  num_songs = num_contracts_per_publisher * num_publisher * num_song_per_contract
  for i in track(range(num_songs), description="generating stats for songs"):
    for j in range(len(weeks) - 1):
      hit_rate = round(random.randint(0, 10000))
      avg_rating = round(random.uniform(0, 5), 2)
      start_week = weeks[j]
      end_week = weeks[j+1]
      cur.execute("insert into song_stats values ({}, '{}', '{}', {}, {});\n".format(i, start_week, end_week, hit_rate, avg_rating))

def generate_versions(cur):
  num_songs = num_contracts_per_publisher * num_publisher * num_song_per_contract
  for i in track(range(num_songs), description="generating versions"):
    for j in range(num_versions):
      version_name = versions[j]
      resource_url = 'N/A'
      cur.execute("insert into version values ({}, {}, '{}', '{}');\n".format(i, j, version_name, resource_url))

def generate_users(cur):
  for i in track(range(num_user), description="generating users"):
    email = ''.join(random.choices(string.ascii_letters, k=10)) + '@' + ''.join(random.choices(string.ascii_lowercase, k=3)) + '.com'
    users.append(email)
    alias = ''.join(random.choices(string.ascii_lowercase, k=5))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    cur.execute("insert into user_t values ('{}', '{}', '{}');\n".format(email, alias, password))

def generate_user_stats(cur):
  for user in track(users, description="generating user_stats"):
    for j in range(len(weeks) - 1):
      week_start = weeks[j]
      week_end = weeks[j+1]
      active_hours = round(random.uniform(0, 40), 2)
      favorite_song = random.randint(0, num_publisher * num_contracts_per_publisher * num_song_per_contract - 1)
      cur.execute("insert into user_stats values ('{}', '{}', '{}', {}, {});\n".format(user, week_start, week_end, active_hours, favorite_song))

def generate_privilege(cur):
  for i in track(range(len(privilege)), description="generating privilege"):
    p = privilege[i]
    description = privilege_d[i]
    cur.execute("insert into privilege values ('{}', '{}');\n".format(p, description))

def generate_have_privilege(cur):
  for user in track(users, description="generating user privilege"):
    cur.execute("insert into have_privilege values ('{}', 'User');\n".format(user))
    dice = random.randint(0, 10)
    if dice <= 5:
      cur.execute("insert into have_privilege values ('{}', 'VIP');\n".format(user))
    if dice <= 2:
      cur.execute("insert into have_privilege values ('{}', 'Super VIP');\n".format(user))

def generate_require_privilege(cur):
  num_songs = num_publisher * num_contracts_per_publisher * num_song_per_contract
  for i in track(range(num_songs), description="generating version privilege requirement"):
    fmt = "insert into requires_privilege values ({}, {}, '{}');\n"
    cur.execute(fmt.format(i, 0, privilege[0]))
    cur.execute(fmt.format(i, 1, privilege[1]))
    cur.execute(fmt.format(i, 2, privilege[2]))

def generate_play_list(cur):
  labels= ['Pop', 'Classic', 'Nostalgic', 'Remix']
  for user in track(users, description="generating playlist"):
    for i in range(num_play_list_per_user):
      title = "{} Playlist_{}".format(user, i)
      description = "Play list {} created by user {}".format(i, user)
      creation_time = datetime(2021, 3, 23).strftime("%Y-%m-%d %H:%M:%S")
      label = labels[random.randint(0, 3)]
      cur.execute("insert into play_list (created_by, title, description, creation_time, label) values ('{}', '{}', '{}', '{}', '{}');\n"
              .format(user, title, description, creation_time, label))
    
def generate_play_list_songs(cur):
  num_play_list = num_user * num_play_list_per_user
  num_songs = num_publisher * num_contracts_per_publisher * num_song_per_contract
  for i in track(range(1, num_play_list), description="generating songs in playlist"):
    song_list = random.sample(range(num_songs), num_song_included)
    for song_id in song_list:
      cur.execute("insert into include_song values ({}, {});\n".format(i, song_id))
  
def main(
  database: str
):
  conn = psycopg2.connect(host="localhost", port="5432", dbname=database)
  cur = conn.cursor()
  print("[italic bold red]Generating Record[/italic bold red]")
  start_time = datetime.now()
  generate_publishers(cur)
  generate_contract(cur)
  generate_song(cur)
  generate_song_stat(cur)
  generate_versions(cur)
  generate_users(cur)
  generate_user_stats(cur)
  generate_privilege(cur)
  generate_have_privilege(cur)
  generate_require_privilege(cur)
  generate_play_list(cur)
  generate_play_list_songs(cur)
  conn.commit()
  end_time = datetime.now()
  delta = end_time - start_time
  print("[italic bold red]Finished Generating Record, Used Time: {}[/italic bold red]".format(delta))
if __name__ == "__main__":
  typer.run(main)
  
