init_prompt=\
"\nWelcome To 'notGoodAtJava' Music Player !\n\
You can proceed as:\n\
1 -> User\n\
2 -> Administrater\n\
3 -> Publisher\n\
0 -> Quit\n"

unlogged_prompt=\
"\nWelcome To 'notGoodAtJava' Music Player !\n\
Please first:\n\
1 -> Log in\n\
2 -> Register\n\
0 -> Back to Home Page\n"

user_loggedin_prompt=\
"\nWelcome To 'notGoodAtJava' Music Player !\n\
Please Select an Operation:\n\
1 -> Browse Songs\n\
2 -> Browse Version Detail of a song\n\
3 -> Play a version of song\n\
4 -> Search for Song by Artist\n\
5 -> Browse Playlists\n\
6 -> Create Playlist\n\
7 -> Delete Playlist\n\
8 -> Add Song to Playlist\n\
9 -> Remove Song from Playlist\n\
10 -> Unlog\n\
11 -> My Subscription\n\
12 -> Subscribe\n\
13 -> UnSubscribe\n\
0 -> Back to Home Page\n"

admin_prompt=\
"\nWelcome To 'notGoodAtJava' Music Player !\n\
Please Select an Operation:\n\
1 -> Browse Weekly User Stats\n\
2 -> Search Song Stats\n\
3 -> Browse Users with subscription detail\n\
4 -> Browse Publishers with contracts detail\n\
0 -> Back to Home Page\n"

publisher_prompt=\
"\nWelcome To 'notGoodAtJava' Music Player !\n\
Plese Select an Operation:\n\
1 -> List Your Contracts\n\
2 -> See Contract Detail\n\
3 -> Add Song to Contract\n\
4 -> Add Version to Song\n\
5 -> Require Privilege for your song version\n\
6 -> Unlog\n\
0 -> Back to Home Page\n"

state_to_prompt = {
  'INIT': init_prompt,
  'USER_UNLOGGED': unlogged_prompt,
  'USER_LOGGED': user_loggedin_prompt,
  'ADMIN': admin_prompt,
  'PUBLISHER_UNLOGGED': unlogged_prompt,
  'PUBLISHER_LOGGED': publisher_prompt
}