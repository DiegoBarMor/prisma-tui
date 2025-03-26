import datetime

# //////////////////////////////////////////////////////////////////////////////
class Debug:
    def __init__(self, path: str):
        self.path = path
        with open(self.path, 'w') as file:
            file.write(f"{datetime.datetime.now()}\n\n")

    def log(self, *text, sep = ' ', end = '\n'):
        text = sep.join(map(str, text))
        with open(self.path, 'a') as file:
            file.write(text + end)


# //////////////////////////////////////////////////////////////////////////////
# from prisma.debug import Debug; d = Debug("name.log")
