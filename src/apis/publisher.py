from typing import Tuple
import psycopg2

def connect():
  conn = psycopg2.connect(host="localhost", port="5432", dbname="music_player")
  cur = conn.cursor()
  return (conn, cur)

def quit(conn, cur):
  conn.commit()
  cur.close()
  conn.close()

def login() -> Tuple[bool, int]:
  '''
  Prompt User to give a publisher id
  check if matches with existing record.
  If so, login and return (true, publisher_id)
  if not, return (false, anything)

  Possible Error:
  1. publisher_id not exists
  print corresponding error message before return
  '''
  flag = False
  id = -1
  conn, cur = connect()
  try:
    publisher_id = int(input("Please Enter Your Id: "))
    query = "select * from publisher where publisher_id = %s"
    cur.execute(query, (publisher_id,))
    publisher = cur.fetchone()
    if publisher is not None:
      print("Login Success! Welcome: {}".format(publisher[1]))
      flag = True
      id = publisher_id
    else:
      print("Login Failed: No Record For id: {}".format(publisher_id))
  except ValueError:
    print("Id Should be a Number")

  quit(conn, cur)
  return (flag, id)

def register() -> Tuple[bool, int]:
  '''
  Prompt User to give a publisher id and register

  Possible Error:
  1. publisher_id already exists
  print corresponding error message before return
  '''
  flag = False
  id = -1

  user_input = input("Please Enter an Id and Name split by ',': ").split(',')
  if len(user_input) != 2:
    print("Invalid Input: Please Enter Exactly two arguments")
    return (False, 0)
  publisher_id = 0
  publisher_name = user_input[1]
  try:
    publisher_id = int(user_input[0])
  except ValueError:
    print("Invalid Input: Publisher Id should be a number")
    quit(conn, cur)
    return (flag, id)

  query = "insert into publisher values (%s, %s)"
  conn, cur = connect()
  try:
    cur.execute(query, (publisher_id, publisher_name))
    print("Successfully Registered publisher {}: {}".format(publisher_id, publisher_name))
    flag = True
    id = publisher_id
  except psycopg2.errors.UniqueViolation:
    print("Publisher ID Already Exists: Please Login")

  quit(conn, cur)
  return (flag, id)

def list_contracts(publisher_id: int):
  '''
  List all contracts belong to the publisher
  '''
  query = "select * from contract_t where publisher_id = %s"
  conn, cur = connect()
  cur.execute(query, (publisher_id, ))
  print("---------Contract Detail For Publisher: {}---------".format(publisher_id))
  for record in cur:
    contract_id = record[0]
    contract_title = record[2]
    start_date = record[3]
    end_date = record[4]
    print("Contract ID: {}, Title: {}, From {} to {}".format(contract_id, contract_title, start_date, end_date))
  print("---------Finished Contract Detail-------------------")
  quit(conn, cur)

def list_contracts_detail(publisher_id: int):
  '''
  Prompt User for a contract id,
  list all songs belong to the contract

  possible errors:
  1. contract does not exist
  2. contract belongs to another publisher
  '''

  contract_query = "select * from contract_t where contract_id = %s"
  query = "select * from song where contract_id = %s"
  try:
    contract_id = int(input("Please Enter Contract ID: "))
    conn, cur = connect()
    cur.execute(contract_query, (contract_id,))
    contract = cur.fetchone()

    if contract is None:
      print("Contract of ID {} Does not exist".format(contract_id))
      quit(conn, cur)
      return

    # we do not allow publisher to view other's contract
    contract_owner = contract[1]
    if contract_owner != publisher_id:
      print("You can only view your own contract!")
      quit(conn, cur)
      return

    # list songs that belongs to this contract
    cur.execute(query, (contract_id,))
    print("---------Songs included in Contract {}-{}---------".format(contract[0], contract[2]))
    for song in cur:
      song_id = song[0]
      title = song[2]
      language = song[3]
      description = song[4]
      artist = song[5]
      print("Song ID: {}, Title: {}, Language: {}, Description: {}, Written By: {}"
              .format(song_id, title, language, description, artist))
    print("-----------Finished Song Detail-----------------")
    quit(conn, cur)
  except ValueError:
    print("Invalid Input: Contract ID has to be a number")

def add_song_to_contracts(publisher_id: int):
  '''
  Prompt User to give: contract_id,song_id,title,language,description,artist
  possible errors:
  1. contract does not exists or does not belong to this publisher
  2. song_id not unique
  3. song_id not Number
  4. language not in "EN-US", "ZH-CN", "JA-JP", "RU-RU", "KO-KR"
  '''
  contract_query = "select * from contract_t where contract_id = %s"
  insert_query = "insert into song values (%s, %s, %s, %s, %s, %s)"

  user_input=input("Please Enter contract_id, song_id, song_title, language, description, artist seperated by ',': ").split(',')
  if len(user_input) != 6:
    print("Invalid Input: You have to enter exactly 6 arguments")
    return
  for i in user_input:
    if not i:
      print("Invalid Input: You have to enter exactly 6 arguments")
      return

  # parse input
  contract_id = -1
  song_id = -1
  try:
    contract_id = int(user_input[0])
  except ValueError:
    print("Invalid Input: Contract Id has to be a number")
    return
  try:
    song_id = int(user_input[1])
  except ValueError:
    print("Invalid Input: Song id has to be a number")
    return

  song_title = user_input[2]
  language = user_input[3]
  description = user_input[4]
  artist = user_input[5]

  conn, cur = connect()
  # check contract constraint
  cur.execute(contract_query, (contract_id,))
  contract = cur.fetchone()
  if contract is None:
    print("Contract of ID {} does not exist".format(contract_id))
    quit(conn, cur)
    return
  contract_owner = contract[1]
  if contract_owner != publisher_id:
    print("You can only view your own contract!")
    quit(conn, cur)
    return

  # ok, perform operation
  try:
    cur.execute(insert_query, (song_id, contract_id, song_title, language, description, artist))
    print("Successfully Inserted Song {} to Contract {}".format(song_id, contract_id))
  except psycopg2.errors.UniqueViolation:
    print("Insert Failed: Song Id {} already exists".format(song_id))
  except psycopg2.errors.InvalidTextRepresentation:
    print("Language can only be chosen from 'EN-US', 'ZH-CN', 'JA-JP', 'RU-RU', 'KO-KR'")

  quit(conn, cur)


def add_version_to_song(publisher_id: int):
  '''
  Prompt User for (song_id, version_id, version_name, resource_url)

  possible errors:
  1. song does not exists
  2. song belongs to other's contract
  3. song_id, version_id is not unique
  '''
  contract_query = "select distinct publisher_id from song join contract_t using (contract_id) where song_id = %s"
  insert_query = "insert into version values (%s, %s, %s, %s)"

  user_input = input("Please Enter song_id, version_id, version_name, resource_url separated by ',': ").split(',')
  if len(user_input) != 4:
    print("Invalid Input: You have to enter exactly 4 arguments")
    return
  for i in user_input:
    if not i:
      print("Invalid Input: You have to enter exactly 4 arguments")
      return

  song_id = -1
  version_id = -1
  try:
    song_id = int(user_input[0])
  except ValueError:
    print("Invalid Input: song_id has to be a number")
    return

  try:
    version_id = int(user_input[1])
  except ValueError:
    print("Invalid Input: version_id has to be a number")
    return

  version_name = user_input[2]
  resource_url = user_input[3]

  # contract constraint
  conn, cur = connect()
  cur.execute(contract_query, (song_id,))
  song_owner = cur.fetchone()
  if song_owner is None:
    print("Song of ID {} does not exists".format(song_id))
    quit(conn, cur)
    return
  if song_owner[0] != publisher_id:
    print("Song of ID {} is not your grant!".format(song_id))
    quit(conn, cur)
    return

  # ok, perform operation
  try:
    cur.execute(insert_query, (song_id, version_id, version_name, resource_url))
    print("Successfully inserted song id {}, version {}".format(song_id, version_id))
  except psycopg2.errors.UniqueViolation:
    print("Song Version ({}-{}) already exists".format(song_id, version_id))

  quit(conn, cur)

def require_privilege(publisher_id: int):
  '''
  Prompt User for (song_id, version_id, privilege_title)

  possible error:
  1. song does not belong to this publisher
  2. song_id, version_id does not reference a valid version
  3. privilege title does not reference a valid privilege
  4. this requirement already exists
  '''
  contract_query = "select distinct publisher_id from song join contract_t using (contract_id) where song_id = %s"
  insert_query = "insert into requires_privilege values (%s, %s, %s)"

  user_input = input("Please Enter song_id, version_id, privilege_title separated by ',': ").split(',')

  if len(user_input) != 3:
    print("Invalid Input: You have to enter exactly 3 arguments")
    return
  for i in user_input:
    if not i:
      print("Invalid Input: You have to enter exactly 3 arguments")
      return
      
  song_id = -1
  version_id = -1

  try:
    song_id = int(user_input[0])
  except ValueError:
    print("Invalid Input: Song id has to be a number")
    return

  try:
    version_id = int(user_input[1])
  except ValueError:
    print("Invalid Input: Version id has to be a number")

  privilege_title = user_input[2]

  # check contract constraint
  conn, cur = connect()
  cur.execute(contract_query, (song_id,))
  publisher = cur.fetchone()
  if publisher is None:
    print("Song of ID {} does not exists".format(song_id))
    quit(conn, cur)
    return
  if publisher[0] != publisher_id:
    print("Song if ID {} is granted by publisher {}: You can only access your own song".format(song_id, publisher[0]))
    quit(conn, cur)
    return

  # ok, perform operation
  try:
    cur.execute(insert_query, (song_id, version_id, privilege_title))
    print("Successfully added privilege requirement: {} for song id {} version {}".format(privilege_title, song_id, version_id))
  except psycopg2.errors.UniqueViolation:
    print("Song {} version {} already requires privilege '{}'".format(song_id, version_id, privilege_title))
  except psycopg2.errors.ForeignKeyViolation:
    # check which foreign key violation
    if privilege_title not in ['User', 'VIP']:
      print("Privilege Should be in 'User', 'VIP'")
    else:
      print("Song {} Version {} does not exist".format(song_id, version_id))

  quit(conn, cur)
