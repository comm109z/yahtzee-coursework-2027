import random 
from yahtzee_backend import *

# change debug mode to True if you want to 
# see the content and structure of game_state
# displayed as the game progresses
DEBUG_MODE = False

def display_message(msg):
    print(msg)

def display_game_state_debug(game_state):
    game_state_str = f"""\
    game_state = {{
       'player': '{game_state['player']}',
       
       'round': {game_state['round']},
       'roll': {game_state['roll']},
       'status': '{game_state['status']}',
       'dice': {game_state['dice']},
       'locked': {game_state['locked']},

       # UPPER
       '1': {game_state['1']}, # ONES
       '2': {game_state['2']}, # TWOS
       '3': {game_state['3']}, # THREES
       '4': {game_state['4']}, # FOURS
       '5': {game_state['5']}, # FIVES
       '6': {game_state['6']}, # SIXES

       # LOWER
       'T': {game_state['T']}, # THREE OF A KIND
       'F': {game_state['F']}, # FOUR OF A KIND
       'S': {game_state['S']}, # SHORT STRAIGHT
       'L': {game_state['L']}, # LONG STRAIGHT
       'H': {game_state['H']}, # FULL HOUSE
       'C': {game_state['C']}, # CHANCE
       'Y': {game_state['Y']}, # YAHTZEE
       
       'UPPER TOTAL':      {game_state['UPPER TOTAL']},
       'BONUS':            {game_state['BONUS']},
       'LOWER TOTAL':      {game_state['LOWER TOTAL']},
       'TOTAL SCORE':      {game_state['TOTAL SCORE']}
    }}
    """
    print(game_state_str)

def display_game_state_default(game_state):
    
    round_info = f"ROUND: {game_state['round']} of 13"
    
    roll_info = f"ROLL: {game_state['roll']} of 3"
    
    score_card = get_score_card(game_state)
    
    ui_dashboard = ( f"-------------------------------------------\n"
                   + f"SCORE CARD FOR {game_state['player']}\n"
                   + f"-------------------------------------------\n"
                   + f"{score_card}" 
                   + f"-------------------------------------------\n"
                   + f"{round_info}\n" 
                   + f"{roll_info}\n" 
                   + f"-------------------------------------------\n" 
                   + f"DICE: {game_state['dice']}\n" 
                   + f"-------------------------------------------\n" )
    
    display_message(ui_dashboard)

if DEBUG_MODE:
    display_game_state = display_game_state_debug
else:
    display_game_state = display_game_state_default


def get_score_card(game_state):
    score_card = ""
    # upper
    for row_char in upper_rows:
        row = char_to_row.get(row_char, "")
        score = game_state.get(row_char, "")
        if score is None: 
            score = "-"
        score_card += f"{row_char} | {row:<30} | {score}\n"
    score_card += "\n"
    # lower
    for row_char in lower_rows:
        row = char_to_row.get(row_char, "")
        score = game_state.get(row_char, "")
        if score is None: 
            score = "-"
        score_card += f"{row_char} | {row:<30} | {score}\n"
    score_card += "\n"
    # totals
    for row in misc_rows:
        score = game_state.get(row, "")  
        if score is None: 
            score = "-"
        score_card += f"{row:<30}     | {score}\n"
    return score_card


def ui_roll_dice(game_state):
    if game_state['roll'] == 1:
        input("Press enter to roll dice...\n")
    roll_dice(game_state)
    game_state['dice'] = sorted(game_state['dice'])
    return

    
def ui_select_dice(game_state):
    selection_complete = False
    first = True
    while selection_complete == False:
        
        if not first:
            display_message("Invalid selection please try again")
            first = False

        user_vals = input("Which dice would you like to keep?\n Enter as csv e.g. 2,3\n")
        dice_to_keep = []
        vals = user_vals.split(",")
        for val in vals:
            if val in ['1','2','3','4','5','6','']:
                if val != '':
                    dice_to_keep.append(int(val))
            else: 
                continue
                
        result = lock_dice(game_state, dice_to_keep)        
        if result==False:
            selection_complete = False
        else:
            selection_complete = True

def ui_enter_score(game_state):
    instructions = get_score_card(game_state) #get_score_instructions(game_state) 
    #display_message(instructions)
    #display_message(f"Final roll: {game_state['dice']}")

    row_char = None
    while row_char is None:
        display_message("Where do you want to score your roll?")
        row_char = input("Enter a character code from left hand column\n")
        result = update_scorecard(game_state, row_char)
        if result == False:
            display_message("Can't do that!")
            row_char = None
    return True


def ui_run_game_loop(game_state):
    
    display_game_state(game_state)
    
    status = game_state['status']
    round_num = game_state['round']
    roll = game_state['roll']

    finished = False
    
    if status == "WAIT_FOR_ROLL":
        ui_roll_dice(game_state)
        if roll < 3:
            game_state['status'] = "WAIT_FOR_SELECT"
        else:
            game_state['status'] = "WAIT_FOR_SCORE"
    elif status == "WAIT_FOR_SELECT":
        ui_select_dice(game_state)
        if roll < 3 and sum(game_state['locked']) != 5:
            game_state['status'] = "WAIT_FOR_ROLL"
            game_state['roll'] = game_state['roll'] + 1
        else:
            game_state['roll'] = 3
            game_state['status'] = "WAIT_FOR_SCORE"
    elif status == "WAIT_FOR_SCORE":
        entered_score = False
        while entered_score == False:
            entered_score = ui_enter_score(game_state)
        if game_state['roll'] == 3:
            game_state['roll'] = 1
            reset_dice(game_state)
            game_state['round'] = game_state['round'] + 1
        else:
            game_state['roll'] = game_state['roll'] + 1
        
        if round_num < 13:
            game_state['status'] = "WAIT_FOR_ROLL"
        else:
            game_state['status'] = "GAME_ENDED"
    else:
        finished = True

    return finished


def ui_run_full_game():
    display_message("Welcome to Yahtzee!")

    game_state = initialise_game()
    
    player = ""
    while player.strip() == "":
        display_message("Enter your name:")
        player = input("> ")
    
    game_state['player'] = player.upper()
    
    if load_existing_game(game_state):
        display_message("Resuming game")

    finished = False
    while finished == False:
        finished = ui_run_game_loop(game_state)

    display_message("Game ended!")
    display_message(f"Your score was: {game_state['TOTAL SCORE']}")

    formatted_score_card = get_score_card(game_state)
    display_message(formatted_score_card)

    if player!="":
        game_state['player_name'] = player
        save_score(game_state)
        formated_stats = get_stats(game_state)
        display_message(formated_stats)       


if __name__ == '__main__':
    ui_run_full_game()