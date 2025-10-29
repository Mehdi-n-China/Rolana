import json

intro_text = \
"""Welcome to the Rolana Debug Console!
For help, invoke -> help
"""

def handle_flag(flag, value):
    with open("flags.json", "r+") as f:
        data = json.load(f)
        if flag in data:
            data[flag] = value
            f.seek(0)
            f.truncate(0)
            json.dump(data, f, indent=4)
        else:
            print("Could not find flag " + flag)

def main() -> None:
    print(intro_text)
    while True:
        prompt = input("> ").lower().split()
        if prompt[0] == "set":
            if prompt[1] == "flag":
                handle_flag(prompt[2], prompt[3])




if __name__ == '__main__':
    main()