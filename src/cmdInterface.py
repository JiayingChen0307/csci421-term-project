from prompts import state_to_prompt
from state import proceed

def main() -> int:
  # set initial state
  state = 'INIT'
  while state != 'QUIT':
    try:
      # read an option
      cmd = int(input('\033[1m'+state_to_prompt[state]+'\033[0m'))
      # state machine going forward
      state = proceed(state, cmd)
    except ValueError:
      print("Invalid Command: Please Enter a Number")

  # quit
  print("Good Bye\n")
  return 0
if __name__ == "__main__":
  main()
