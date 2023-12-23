import sys
import os

from transliterate import translit

from src.messages import *
from src.commands import *
from src.config import CONFIG


# working with filesystem
def open_file_and_read(path: str) -> list:
    """
    Open file, read and return it
    """
    with open(path, 'r') as origin_file:
        return origin_file.readlines()


def create_file_and_write(path: str, new_code: str) -> None:
    """
    Create file and write information
    """
    with open(path, 'w+') as translated_file:
        # writing to the new file
        translated_file.write(new_code)


# handling code
def handle_code(old_code: list) -> (bool, str):
    """
    translates code and returns status boolean
    True - success, False - error
    """
    new_code = ''

    # replacing
    for i in range(len(old_code)):
        line = old_code[i]

        for key in COMMANDS:
            if COMMANDS[key] in line:
                error = (f'Unexpected: `{COMMANDS[key]}` should be `{key}`'
                         + SYNTAX_ERROR['message'] + f' in line {i + 1}'
                         + '\ncode: ' + SYNTAX_ERROR['code'])
                return False, error
            line = line.replace(key, COMMANDS[key])
        new_code += line

    return True, new_code


def russia_to_english(text: str) -> str:
    """
    obvious. e.g. слово - slovo
    """
    return translit(text, 'ru')


def translate(x: str) -> None:
    """
    Translates the file and saves it to the dir
    at the same directory.

    x - path to the original file.
    """

    full_path = '/'.join(x.split('/')[:-1]) if '/' in x else './'   # getting filepath
    save_to_dir = CONFIG['DIRS']['translated_dir']  # defining dir
    temp = x.split("/")[-1].split('.')  # list of filename and extension
    path = f'{full_path}/{save_to_dir}/{temp[0]}.py'  # full path to translated file

    if temp[-1] != CONFIG['EXTENSION']:
        print(NOT_YASH_EXCEPTION['message'] + '\ncode: ' + NOT_YASH_EXCEPTION['code'])
        return

    os.makedirs(f'{full_path}/{save_to_dir}', exist_ok=True)

    # reading .huilang file and translating it
    old_code = open_file_and_read(x)
    is_ok, new_code = handle_code(old_code)

    # looking for errors
    if not is_ok:
        print(new_code)
        return

    # if status ok
    create_file_and_write(path, new_code)


# main function
def main() -> None:
    # checking if there is not enough args
    if len(sys.argv) == 2:
        print(NOT_ENOUGH_ARGUMENTS['message'] + '\ncode: ' + NOT_ENOUGH_ARGUMENTS['code'])
        return

    match sys.argv[1]:
        case 'build_py':
            # translating to python
            translate(sys.argv[2])
        case 'build_hui':
            pass
        case _:
            print('invalid argument')


if __name__ == '__main__':
    main()
