from config import CONFIG

SUCCESS = {'message': 'success! successfully translated', 'code': '0'}
NOT_YASH_EXCEPTION = {'message': f'failed! file should have `.{CONFIG["EXTENSION"]}` extension', 'code': '1'}
SYNTAX_ERROR = {'message': 'failed! syntax error', 'code': '2'}
NOT_ENOUGH_ARGUMENTS = {'message': 'failed! not enough arguments', 'code': '3'}
