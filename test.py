import readline

commands = ["help", "add", "all", "show", "edit", "remove", "quit", "play", "import", "export", "csv", "important"]

def completer(text: str, state: int) -> str | None:
    options = [command for command in commands if command.startswith(text)]
    if state < len(options):
        return options[state]
    return None


def setup_readline() -> None:
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

while True:
    setup_readline()
    user = input(">>> ")
    if user == "find":
        commands = ["pizda", "huy", "vagina", "sex"]
    else:
        commands = ["help", "add", "all", "show", "edit", "remove", "quit", "play", "import", "export", "csv", "important"]
