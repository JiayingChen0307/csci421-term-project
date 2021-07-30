from typing import Tuple
import psycopg2
from datetime import datetime
import pandas as pd

### helper functions ###
def connect():
    conn = psycopg2.connect(host = "localhost", port = "5432", dbname = "music_player")
    cur = conn.cursor()
    return conn, cur

def quit(conn, cur):
    cur.close()
    conn.close()

def login() -> Tuple[bool, str]:
  '''
  Prompt User to give an email and password,
  check if matches with existing record.
  If so, login and return (true, user_email)
  if not, return (false, anything)

  Possible Error:
  1. user_email not in the table
  2. user_email is in the table but password doesn't match
  print corresponding error message before return
  '''


  # check if the provided email and password match to a record in user_t
  query = "select * from user_t\
  where user_email = %s and password = %s"

  user_input = input("Please enter the email and password for your account separated by comma: ")
  user_input = user_input.split(',')

  if len(user_input) != 2:
      print("Login failed. Please provide BOTH the email and password for your account")
      return (False, 0)

  conn, cur = connect()

  cur.execute(query, (user_input[0], user_input[1]))
  user_info = cur.fetchone()
  if not user_info:
      print("Login failed. Incorrect email or password.")
      quit(conn, cur)
      return (False, 0)

  user_id = user_info[0]
  print("Login successful. You are logged in as: " + user_info[1] + ".")
  quit(conn, cur)
  return (True, user_id)


def register() -> Tuple[bool, str]:
  '''
  Prompt User to give an email and password and an alias(user name),
  register, and return (true, user_email) if success and (false, anything) otherwise.

  Note: if successful, also insert a record in have privilege table
  Also: note the size constraint in the table

  Possible Error:
  1. user_email already exists (UniqueViolation)
  2. user_email is not the right form
  3. alias/password too long (Not likely just in case)
  4. Not null violation for any of the three values
  '''

  user_insert = "insert into user_t values(%s, %s, %s)"

  user_input  = input("Please enter an email address, alias, and password for your account separated by commas: ")
  user_input = user_input.split(',')

  # check for number of inputs
  if len(user_input) != 3:
      print("Registration failed: incorrect number of inputs. Please enter all THREE pieces of required information.")
      return (False, 0)
  if user_input[2] == '' or user_input[1] == '':
      print("Registration failed: None of the required information can be empty.")
      return (False, 0)

  conn, cur = connect()

  # try inserting the record and check for potential exceptions
  try:
       cur.execute(user_insert, (user_input[0], user_input[1], user_input[2]))
       print("Registration successful.")
  except psycopg2.errors.UniqueViolation:
      print("Registration failed. The inputted email address already exists. Please login.")
      quit(conn, cur)
      return (False, 0)
  except psycopg2.errors.CheckViolation:
      print("Registration failed. Incorrect format for the inputted email address. Must be in the form ***@***.***")
      quit(conn, cur)
      return (False, 0)
  except psycopg2.errors.NotNullViolation:
      print("Registration failed. None of the required information can be empty.")
      quit(conn, cur)
      return (False, 0)
  except psycopg2.errors.InvalidTextRepresentation:
      print("Registration failed. Please double check your input values. Password/alias could be too long.")
      quit(conn, cur)
      return (False, 0)
  except psycopg2.Error:
      print("Registration failed. Unknown error.")
      quit(conn, cur)
      return (False, 0)

  privilege_query = "insert into have_privilege values(%s, %s)"
  cur.execute(privilege_query, (user_input[0], 'User'))
  conn.commit()

  quit(conn, cur)
  return (True, user_input[0])

def list_songs():
    conn, cur = connect()
    query = "select song_id, title, language, artist from song"
    #cur.execute(query)
    print(pd.read_sql(query,conn).set_index('song_id'))

    quit(conn, cur)

def song_detail():
    query = "select title, language, description, artist, version_id, version_name\
     from song natural join version where song_id = %s"

    user_input  = input("Please enter a song id to see more detailed information: ")
    try:
        user_input = int(user_input)
    except ValueError:
        print("Invalid Input! Please enter an integer for song id.")
        return

    conn, cur = connect()
    cur.execute(query, (user_input,))

    song_details = pd.read_sql(query,conn, params = (user_input,)).set_index('version_id')
    if len(song_details):
        print(song_details)
    else:
        print("Song does not exist.")
    quit(conn, cur)
    return

def play_version(user_id):
    user_input = input("Please enter a song id and a corresponding version id separated by comma: ")
    user_input = user_input.split(',')

    # check for number of inputs
    if len(user_input) != 2:
        print("Play request failed: incorrect number of inputs. Please enter a song id and a corresponding version id.")
        return

    conn, cur = connect()

    song_exist_query = ("select * from song where song_id = %s")
    version_exist_query = ("select * from version where song_id = %s and version_id = %s")
    query = ("with requires(title) as (\
    select privilege_title from requires_privilege where song_id = %s and version_id = %s),\
    have(user_email, title) as (\
    select user_email, privilege_title from have_privilege where user_email = %s)\
    select user_email from have, requires\
    where have.title = requires.title")

    try:
        cur.execute(song_exist_query,  (user_input[0],))
    except psycopg2.errors.InvalidTextRepresentation:
        print("Please enter an integer value for song id.")
        quit(conn, cur)
        return
    song_name = cur.fetchone()
    if not song_name:
        print("Song does not exist.")
        quit(conn, cur)
        return
    try:
        cur.execute(version_exist_query, (user_input[0], user_input[1]))
    except psycopg2.errors.InvalidTextRepresentation:
        print("Please enter an integer value for version id.")
        quit(conn, cur)
        return
    if not cur.fetchone():
        print("The selected version does not exist.")
        quit(conn, cur)
        return

    cur.execute(query, (user_input[0], user_input[1], user_id))
    if cur.rowcount == 0:
        print("You need a higher subscription level to listen to the selected version of the song. Trust me, it is worth it!")
        quit(conn, cur)
        return
    else:
        print("Playing {}... (Such a lovely song, isn't it?)".format(song_name[2]))
        quit(conn, cur)
        return

def search_by_artist():
    # prompt user to input an artist's name; use lower() to ignore case
    user_input = input("Search for songs by this artist (please enter the full name of the artist): ")
    user_input = user_input.lower()

    conn, cur = connect()
    query = "select song_id, title, language, description from song\
    where lower(artist) = %s"

    songs = pd.read_sql(query, conn, params = (user_input,)).set_index('song_id')

    if len(songs):
        print(songs)
    else:
        print("No songs by this artist.")
    quit(conn, cur)
    return

def list_playlists():
    conn, cur = connect()
    playlist_id_query = """select play_list_id, title, created_by from play_list;"""
    cur.execute(playlist_id_query)

    content_query = """select S.title, S.artist, S.language from include_song as I join song as S on I.song_id=S.song_id where play_list_id = %s;"""
    for record in cur:
        print(f"{record[1]} (ID: {record[0]}) by {record[2]}: ")
        cur_tmp = conn.cursor()
        cur_tmp.execute(content_query, (record[0],))
        for song in cur_tmp:
          print(', '.join([song[0], song[1], song[2]]))
        print('\n')
    quit(conn, cur)

def create_playlist(user_id):
    conn, cur = connect()

    user_input = input("Please enter the title, description, and label of your new playlist, seperated by comma: ")
    user_input = user_input.split(',')
    user_input[-1] = user_input[-1][0].upper() + user_input[-1][1:]

    if len(user_input) != 3:
        print('Failed to create the playlist. Please enter the correct number of arguments. ')
        return

    query = "INSERT INTO play_list(created_by, title, description, creation_time, label) VALUES(%s, %s, %s, %s, %s);"

    try:
        cur.execute(query, (user_id, user_input[0].strip(), user_input[1].strip(), datetime.now(), user_input[2].strip()))
        #test_q = "select * from play_list;"
        #cur.execute(test_q)
        #for r in cur:
        #    print(r)
        conn.commit()
        print(f"\nSuccessfully created playlist '{user_input[0]}'.")
    except psycopg2.errors.ForeignKeyViolation:
        print("Creation Failed: User doesn't exists.")
    except psycopg2.errors.UniqueViolation:
        print("Creation Failed: Playlist exists.")
    except psycopg2.errors.InvalidTextRepresentation:
        print("Creation Failed: Please choose a label from 'Pop', 'Classic', 'Nostalgic', 'Remix', and 'None'. ")
    except psycopg2.Error:
        print("Creation Failed: Unknown Error")

    conn.commit()
    quit(conn, cur)

def check_authentication(user_id, cur, user_input):
    check_auth_query = "select play_list_id, created_by from play_list where created_by = %s"
    cur.execute(check_auth_query, (user_id,))
    is_author = False
    for row in cur:
        if row[0] == int(user_input[1]):
          is_author = True
    return is_author

def delete_playlist(user_id):
    conn, cur = connect()

    user_input = input("Please enter the ID of the playlist you want to delete: ")

    is_author = check_authentication(user_id, cur, [None,user_input])

    if not is_author:
        print("You don't have the permission to delete the playlist created by another user.")
        return

    query = "delete from play_list where play_list_id = %s;"
    try:
        cur.execute(query, (user_input.strip(),))
        conn.commit()
        print(f"\nSuccessfully deleted playlist {user_input}.")
    except psycopg2.Error:
        print("Deletion Failed: Unknown Error")

    conn.commit()
    quit(conn, cur)

def add_to_playlist(user_id):
    conn, cur = connect()

    user_input = input("Addition: Please enter the song ID and the playlist ID, separated by comma: ")
    user_input = user_input.split(',')

    if len(user_input) != 2:
        print('Addition failed. Please enter the correct number of arguments. ')
        return

    is_author = check_authentication(user_id, cur, user_input)

    if not is_author:
        print("You don't have the permission to add to the playlist created by another user.")
        return

    query = "INSERT INTO include_song VALUES(%s, %s)"

    try:
        cur.execute(query, (user_input[1].strip(), user_input[0].strip()))
        #test_q = "select * from include_song;"
        #cur.execute(test_q)
        #for r in cur:
        #    print(r)
        conn.commit()
        print(f"\nSuccessfully added song '{user_input[0]}' to playlist '{user_input[1]}'.")
    except psycopg2.errors.ForeignKeyViolation:
        print("Insertion Failed: Playlist or song doesn't exist.")
    except psycopg2.errors.InvalidTextRepresentation:
        print("Insertion Failed: Please enter integer arguments.")
    except psycopg2.errors.UniqueViolation:
        print("Insertion Failed: Song exists.")
    except psycopg2.Error:
        print("Insertion Failed: Unknown Error")

    conn.commit()
    quit(conn, cur)

def remove_from_playlist(user_id):
    conn, cur = connect()

    user_input = input("Removal - Please enter the song ID and the playlist ID, separated by comma: ")
    user_input = user_input.split(',')

    if not user_input[0]:
        print("Please enter the song id to delete. ")
        return
    is_author = check_authentication(user_id, cur, user_input)

    if not is_author:
        print("You don't have the permission to remove from the playlist created by another user.")
        return

    query = "delete from include_song where play_list_id = %s and song_id = %s;"
    try:
        delete_count = cur.execute(query, (user_input[1].strip(), user_input[0].strip()))
        conn.commit()
        if delete_count:
            print(f"\nSuccessfully removed song '{user_input[0]}' from playlist '{user_input[1]}'.")
        else:
            print(f"Playlist {user_input[1]} does not contain song {user_input[0]}.")
    except psycopg2.Error:
        print("Removel Failed: Unknown Error")

    conn.commit()
    quit(conn, cur)

def my_subscription(user_id):
    query = 'select title, description from have_privilege join privilege on title = privilege_title where user_email = %s'
    conn, cur = connect()
    cur.execute(query, (user_id,))
    print("User {}'s Privilege Status: ".format(user_id))
    for result in cur:
        print("Title: {}, Description: {}".format(result[0], result[1]))

def subscribe(user_id):
    show_query = "select title from privilege"
    conn, cur = connect()
    cur.execute(show_query)
    print("Following are our subscription choices: ")
    for privilege in cur:
        if privilege[0] != 'User':
            print("Title: {}".format(privilege[0]))
    user_input = input("Please Enter the title of subscription you want to make: ")

    subscribe_query = "insert into have_privilege values (%s, %s)"
    try:
        cur.execute(subscribe_query, (user_id, user_input))
        conn.commit()
        print("User {} successfully subscribes for {}".format(user_id, user_input))
    except psycopg2.errors.UniqueViolation:
        print("Failed: User {} already has subscription {}".format(user_id, user_input))
    except psycopg2.errors.ForeignKeyViolation:
        print("Failed: Privilege {} does not exist".format(user_input))
    finally:
        quit(conn, cur)

def unsubscribe(user_id):
    user_input = input("Please enter the privilege title from which you want to unsubscribe: ")
    if user_input == "User":
        print("You can't unsubscribe being a user")
        return
    unsubscribe_query = "delete from have_privilege where user_email = %s and privilege_title = %s returning privilege_title"
    conn, cur = connect()
    cur.execute(unsubscribe_query, (user_id, user_input))
    result = cur.fetchall()
    if len(result) == 0:
        print("Failure: User {} does not have privilege {} or privilege doesn't exist".format(user_id, user_input))
    else:
        print("User {} successfully unsubscribed as {}".format(user_id, user_input))
    conn.commit()
    quit(conn, cur)

if __name__ == "__main__":
    #login()
    #register()
    #search_by_artist()
    #list_songs()
    #song_detail()
    #play_version('mer@gmail.com')
    list_playlists('kkk@123.com')
    #create_playlist('kkk@123.com')
    #add_to_playlist('kkk@123.com')
    #remove_from_playlist('kkk@123.com')
