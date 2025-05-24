import os
import time
import random
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

current_word = ""
formatted_word = ""
unlock_progress = []
death_progress = 0
discard_pile = [""]
hint_used = False
hint_char = ""

invalid_chars = ["", " "]

seperator = "========="
word_def = "word"

def load():
    clear_console()
    show_title_card()
    print(
        "Version v0.1\n\n"
        "Commands:\n"
        "  -play - Play PY-MAN\n"
        "  -rules - View the rules\n"
        "  -quit - Quit the game.\n"
    )

    selection = input()

    match selection:
        case "play":
            start_game()
            return
        case "rules":
            show_rules()
            return
        case "quit":
            clear_console()
            exit()
            return
        
    load()

def start_game():
    clear_console()
    show_title_card()
    print(
        "Select game type:\n"
        "  -standard - Pulls words from 'words.txt'. IF THIS FILE DOES NOT EXIST, IT WILL CRASH!\n"
        "  -custom - Set your own word! This is for playing with groups of friends!"
    )
    
    type = input()
    word = ""

    match type:
        case "standard":
            clear_console()
            show_title_card()

            file_paths = []

            for root, _, files in os.walk(os.path.join(dir_path, "words")):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_paths.append(file_path)

            if len(file_paths) <= 0:
                print("No files found in words folder!")
                time.sleep(1)
                start_game()

            print(
                "Select category (by number):\n"
                "  Custom categories can be added in the 'words' folder!"
            )

            for i in range(len(file_paths)):
                print(f"[{i}] - {os.path.splitext(os.path.basename(file_paths[i]))[0]}")

            try:
                selectedPath = int(input())
            except:
                start_game()
        
            with open(file_paths[selectedPath], "r") as file:
                content = file.read()
                words = content.split("\n")
                word = random.choice(words)

            print("Selected word!")
        case "custom":
            word = parse_text(input("Type a word! (Make sure nobody is looking!)\n"))
            print(f"The word '{word}' was selected!")
        case _:
            start_game()
            return

    time.sleep(1)
    clear_console()
    play(word)

def show_rules():
    clear_console()
    print(
        "=========================\n"
        " ___  _ _  _    ___  ___ \n"
        "| . \| | || |  | __>/ __>\n"
        "|   /| ' || |_ | _> \__ \\\n"
        "|_\_\`___'|___||___><___/\n"
        "\n"
        "=========================\n"
        "Your goal is to guess the word.\n"
        "Every time you guess a wrong letter, the man gets hung.\n"
        "6 wrong letters and you lose!\n\n"
        "Type 'hint' at any time for a hint.\n"
        "Typing your answer in quotes (\"\") will count as a word guess.\n"
        "Press enter to exit\n\n"
        "|-------\n"
        "|      |\n"
        "|      |\n"
        f"|     O\n"
        f"|    /|\\\n"
        f"|    / \\\n"
        "|\n"
        "|\n"
        "___________\n\n"
    )

    input()
    load()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_title_card():
    print(
        "===================================\n"
        " ____ ___  _      _      ____  _     \n"
        "/  __\\\\  \//     / \__/|/  _ \/ \  /|\n"
        "|  \/| \  /_____ | |\/||| / \|| |\ ||\n"
        "|  __/ / / \____\| |  ||| |-||| | \||\n"
        "\_/   /_/        \_/  \|\_/ \|\_/  \|\n"
        "\n"
        "==================================="
    )

def play(word):
    global current_word
    global formatted_word
    global unlock_progress
    global death_progress
    global discard_pile
    global hint_used
    global hint_char
    global word_def
    complete = False

    current_word = str(word)
    formatted_word = str(word).replace(" ", "")
    unlock_progress = []
    discard_pile = []

    if " " in current_word:
        word_def = "words"

    if formatted_word == "":
        load()
        return
    
    for char in current_word:
        if char != " ":
            unlock_progress.append(0)

    reload_board()

    while not complete:
        if death_progress == 6:
            lose()
            return

        any = False
        typedChar = parse_text(input())

        if typedChar.lower() == "hint":
            if can_use_hint():
                hint_used = True
                hint_char = random.choice(get_unguessed_chars())

            reload_board()
            continue

        if typedChar.startswith("\""):
            typedChar = typedChar.strip("\"")

            if typedChar == current_word:
                reveal()
                reload_board()
                win()

        typedChar = typedChar[0] # Use first character only

        if typedChar in invalid_chars or typedChar in discard_pile:
            reload_board()
            continue

        for i in range(len(formatted_word)):
            char = formatted_word[i]

            if char.lower() == typedChar.lower():
                unlock_progress[i] = 1
                any = True
            

        if 0 not in unlock_progress:
            complete = True
        if not any:
            death_progress += 1
            discard_pile.append(typedChar)

        reload_board()

    win()

def reload_board():
    global current_word
    global formatted_word
    global word_def

    clear_console()

    # Title
    print(f"Guess the {word_def}!\n")

    # Man
    # defining these here so they can be changed whenever
    # IGNORE HOW BAD THIS IS I'M LAZY
    head = "O" if death_progress >= 1 else " "
    body = "|" if death_progress >= 2 else " "
    arm_l = "/" if death_progress >= 3 else " "
    arm_r = "\\" if death_progress >= 4 else " "
    leg_l = "/" if death_progress >= 5 else " "
    leg_r = "\\" if death_progress >= 6 else " "

    print (
        "|-------\n"
        "|      |\n"
        "|      |\n"
        f"|      {head}\n"
        f"|     {arm_l}{body}{arm_r}\n"
        f"|     {leg_l} {leg_r}\n"
        "|\n"
        "|\n"
        "___________\n\n"
    )

    # Current Word
    wordStr = ""
    index = 0 # seperate variable used here to track non-spaces

    for i in range(len(current_word)):
        char = current_word[i]

        if char == " ":
            wordStr += "  "
        else:
            if unlock_progress[index] == 0:
                wordStr += "_ "
            else:
                wordStr += f"{char} "

            index += 1

    print(f"{wordStr}\n")

    # Discard Pile
    print(f"\n{seperator}\nDiscard Pile:")

    return_str = ""
    for discarded_char in discard_pile:
        return_str += f"[{discarded_char}] "

    if return_str == "":
        return_str = "None discarded yet!"

    print(f"{return_str}\n{seperator}")

    # Hint Text
    can_use = can_use_hint()
    
    if can_use:
        print("Hint avaliable! Type 'hint' to use.")
    else:
        print("Hint unavaliable!")

    if (hint_used):
        print(get_hint_text(hint_char))

    print(f"{seperator}\n")

def can_use_hint():
    return (not hint_used) and (unlock_progress.count(0) > 3)

def get_hint_text(hint_char):
    global word_def

    return random.choice([
        f"Don't tell anyone, but [{hint_char}] might be used...",
        f"I have a feeling [{hint_char}] might be in the {word_def} somewhere...",
        f"My favorite letter is [{hint_char}]...",
        f"The letter [{hint_char}] calls your name...",
        f"{hint_char}{hint_char}{hint_char}{hint_char}{hint_char} whoops, sorry, dropped my [{hint_char}]s...",
        f"The letter {hint_char} is the letter of the winners!",
        f"Did someone say {hint_char}?"
    ])

def reset():
    global current_word, formatted_word, unlock_progress, death_progress, discard_pile, hint_used, hint_char
    current_word = ""
    formatted_word = ""
    unlock_progress = []
    death_progress = 0
    discard_pile = []
    hint_used = False
    hint_char = ""

def win():
    global word_def
    print(f"The {word_def} was {current_word}!")
    end()

def lose():
    global word_def

    reveal()
    reload_board()

    print(f"The man has been hung! The {word_def} was '{current_word}'.")
    end()

def reveal():
    for i in range(len(unlock_progress)):
        unlock_progress[i] = 1

def parse_text(text):
    if str(text).lower() == "kill":
        exit()

    return str(text.strip())

def get_unguessed_chars():
    arr = []

    for i in range(len(formatted_word)):
        if unlock_progress[i] == 0 and formatted_word[i] not in arr:
            arr.append(formatted_word[i])

    return arr

def end():
    print("Press enter to continue!\n")
    input()
    reset()
    load()
    
load()