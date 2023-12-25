import sys
import os
import re
import time

from transliterate import translit
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from src.messages import *
from src.commands import *
from config import CONFIG


# functions for running and changing CONFIG
def check_console_args_and_get_mode() -> str:
    """
    arg validation
    """
    # checking if there is not enough args
    if len(sys.argv) == 2:
        print(NOT_ENOUGH_ARGUMENTS['message'] + '\ncode: ' + NOT_ENOUGH_ARGUMENTS['code'])
        return ''
    if '-c' in sys.argv: CONFIG['RUNTIME_PARAMETERS']['-c'] = True
    if '-r' in sys.argv: CONFIG['RUNTIME_PARAMETERS']['-r'] = True

    return sys.argv[1]


def run_script(path: str) -> None:
    print('-'*20 + 'Run' + '-'*20)
    os.system(f'python3 {path}')
    print('-'*20 + 'End' + '-'*20)
    # input('press any key to continue...')


def check_for_updates(path_to_original: str, path_to_translated: str) -> None:
    def on_upd(s):
        os.system('clear')
        print('-'*20 + 'Run' + '-'*20)
        os.system(f'python3 translator.py build_py {path_to_original} -r')
        print('-'*20 + 'End' + '-'*20)
        # input('press any key to continue...')
    # on_upd('')
    patterns = ["*"]
    ignore_patterns = None
    ignore_directories = False
    case_sensitive = True

    # creating handler
    my_event_handler = PatternMatchingEventHandler(
        patterns, ignore_patterns,
        ignore_directories, case_sensitive)

    my_event_handler.on_modified = on_upd

    # configuring the observer
    path = path_to_original
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)

    # starting observing
    my_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()


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
    with open(path, 'w') as translated_file:
        # writing to the new file
        translated_file.write(new_code)


# handling code
def handle_code(old_code: list) -> (bool, str):
    """
    translates code and returns status boolean
    True - success, False - error
    """
    new_code = ''
    # var_pattern = r'[$>][\b|\D]\w+\S'
    var_pattern = r'[$]\S+'
    func_pattern = r'[\s]\w+[<(]'

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

    # regular expression to detect variables
    matches = [{f'{var}': russia_to_english(var[1:])}
               for var in re.findall(pattern=var_pattern, string=new_code)]

    # detecting functions
    # matches += [{f'{func[:-1]}': russia_to_english(func[:-1])}
    #             for func in re.findall(pattern=func_pattern, string=new_code)]
    for func in re.findall(pattern=func_pattern, string=new_code):
        if func[-1] != 'ь':
            matches.append({func[:-1]: russia_to_english(func[:-1])})
            continue
        matches.append({func[:-1]: russia_to_english(func[:-1])})

    # formatting variables
    for match in matches:
        for key in match:
            new_code = new_code.replace(key, match[key])

    return True, new_code


def russia_to_english(text: str, to_eng=True) -> str:
    """
    obvious. e.g. слово - slovo
    """
    return translit(text, 'ru', reversed=to_eng)


def translate_and_get_file_paths(x: str) -> (str, str):
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
        return '', ''

    # if status ok
    create_file_and_write(path, new_code)
    return x, path


# main function
def main() -> None:
    mode = check_console_args_and_get_mode()

    if mode == 'build_py':
        original_file_path, translated_file_path = (
            translate_and_get_file_paths(sys.argv[2]))

        if CONFIG['RUNTIME_PARAMETERS']['-c']:
            # 1) check file updates
            check_for_updates(original_file_path, translated_file_path)
            # 2) clean console and run file run
            run_script(translated_file_path)

        if CONFIG['RUNTIME_PARAMETERS']['-r']:
            run_script(translated_file_path)

    elif mode == 'build_hui': pass
    else: print('invalid argument')


if __name__ == '__main__':
    main()
