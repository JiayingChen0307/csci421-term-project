import apis.publisher as publisher
import apis.admin as admin
import apis.user as user

# program state
state = {
  "publisherLogged": False,
  "loggedInPublisher": -1,
  "userLogged": False,
  "loggedInUser": ""
}

def initProceed(cmd: int) -> str:
  if cmd == 0:
    return 'QUIT'
  elif cmd == 1:
    if state["userLogged"]:
      print("Welcome User: {}".format(state["loggedInUser"]))
      return "USER_LOGGED"
    return 'USER_UNLOGGED'
  elif cmd == 2:
    return 'ADMIN'
  elif cmd == 3:
    if state["publisherLogged"]:
      print("Welcome Publisher {}".format(state["loggedInPublisher"]))
      return "PUBLISHER_LOGGED"
    return 'PUBLISHER_UNLOGGED'
  
  print("Invalid Command: Please Select 0, 1, 2 or 3\n")
  return 'INIT'

def userUnloggedProceed(cmd: int) -> str:
  if cmd == 1:
    ok, user_email = user.login()
    if ok:
      state["loggedInUser"] = user_email
      state["userLogged"] = True
      return 'USER_LOGGED'
    return 'USER_UNLOGGED'
  elif cmd == 2:
    ok, user_email = user.register()
    if ok:
      state["loggedInUser"] = user_email
      state["userLogged"] = True
      return 'USER_LOGGED'
    return 'USER_UNLOGGED'
  elif cmd == 0:
    return 'INIT'

  print("Invalid Command: Please Select 0, 1, or 2\n")
  return 'USER_UNLOGGED' 


def userLoggedProceed(cmd: int) -> str:
  if cmd == 0:
    return 'INIT'
  elif cmd == 1:
    user.list_songs()
  elif cmd == 2:
    user.song_detail()
  elif cmd == 3:
    user.play_version(state["loggedInUser"])
  elif cmd == 4:
    user.search_by_artist()
  elif cmd == 5:
    user.list_playlists()
  elif cmd == 6:
    user.create_playlist(state["loggedInUser"])
  elif cmd == 7:
    user.delete_playlist(state["loggedInUser"])
  elif cmd == 8:
    user.add_to_playlist(state["loggedInUser"])
  elif cmd == 9:
    user.remove_from_playlist(state["loggedInUser"])
  elif cmd == 10:
    print("User {} unlogged".format(state["loggedInUser"]))
    state["userLogged"] = False
    state["loggedInUser"] = ""
    return "INIT"
  elif cmd == 11:
    user.my_subscription(state["loggedInUser"])
  elif cmd == 12:
    user.subscribe(state["loggedInUser"])
  elif cmd == 13:
    user.unsubscribe(state["loggedInUser"])
  else:
    print("Invalid Command: Please select from 0 - 12")
  return 'USER_LOGGED'

def publisherUnloggedProceed(cmd: int) -> str:
  if cmd == 1:
    ok, publisher_id = publisher.login()
    if ok:
      state["loggedInPublisher"] = publisher_id
      state["publisherLogged"] = True
      return 'PUBLISHER_LOGGED'
    return 'PUBLISHER_UNLOGGED'
  elif cmd == 2:
    ok, publisher_id = publisher.register()
    if ok:
      state["loggedInPublisher"] = publisher_id
      state["publisherLogged"] = True
      return 'PUBLISHER_LOGGED'
    return 'PUBLISHER_UNLOGGED'
  elif cmd == 0:
    return 'INIT'
  else:
    print("Invalid Command: Please Select 0, 1, or 2\n")
  return 'PUBLISHER_UNLOGGED' 

def publisherLoggedProceed(cmd: int) -> str:
  if cmd == 0:
    return 'INIT'
  elif cmd == 1:
    publisher.list_contracts(state["loggedInPublisher"])
  elif cmd == 2:
    publisher.list_contracts_detail(state["loggedInPublisher"])
  elif cmd == 3:
    publisher.add_song_to_contracts(state["loggedInPublisher"])
  elif cmd == 4:
    publisher.add_version_to_song(state["loggedInPublisher"])
  elif cmd == 5:
    publisher.require_privilege(state["loggedInPublisher"])
  elif cmd == 6:
    print("Publisher {} unlogged".format(state["loggedInPublisher"]))
    state["loggedInPublisher"] = -1
    state["publisherLogged"] = False
    return "INIT"
  else:
    print("Invalid Command: Please select from 0 - 6")
  return 'PUBLISHER_LOGGED'

def adminProceed(cmd: int) -> str:
  if cmd == 0:
    return 'INIT'
  #print("Not Implemented")
  elif cmd == 1:
    admin.get_user_stats()
  elif cmd == 2:
    admin.get_song_stats()
  elif cmd == 3:
    admin.get_user_subscription()
  elif cmd == 4:
    admin.get_publisher_contract()
  else:
    print("Invalid Command: Please Select from 0 - 4")
  return 'ADMIN'

transition = {
  'INIT': initProceed,
  'USER_UNLOGGED': userUnloggedProceed,
  'USER_LOGGED': userLoggedProceed,
  'ADMIN': adminProceed,
  'PUBLISHER_UNLOGGED': publisherUnloggedProceed,
  'PUBLISHER_LOGGED': publisherLoggedProceed
}

def proceed(state: str, cmd: int) -> str:
  if state in transition:
    return transition[state](cmd)
  print("UnKnown State: {}".format(state))
  return state
