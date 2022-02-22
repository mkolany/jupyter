from asyncio import current_task
from colorama import Fore, Back, Style
import time

def log(msg, *args, **kwargs):
    ## Higher is the log_level in the log() argument, the lower is its priority.  

    def get_color(level):
        colors = {
            "WARNING": Fore.LIGHTWHITE_EX+Back.YELLOW,
            "SUCCESS": Fore.LIGHTGREEN_EX,
            "FAIL": Fore.RED,
            "RESET": Style.RESET_ALL,
            "INFO": Fore.BLACK+Back.WHITE,
        }
        return colors.get(level.upper(), Fore.BLUE)

    current_time = time.ctime(time.time())
    
    print(f'{Fore.BLACK+Back.WHITE} {current_time} {Fore.YELLOW+Back.BLACK} {msg}{Style.RESET_ALL}')
    # print("[{}] >> {}{}{} <".format(log_level, get_color(log_level), repr(msg), Style.RESET_ALL))


if __name__ == '__main__':
    log('Test')