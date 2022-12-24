from flask import Flask, render_template, request, make_response
from io import StringIO
from re import sub, escape
from difflib import SequenceMatcher
import sys
from os.path import abspath, dirname
import ast

Version = '0.0.114'


# LIST OF ERRORS
################
# Ill-v >> IllegalVariableName 		:> Char that python doesn't support when declaring VARIABLE
# Ill-f >> IllegalFunctionName 		:> Char that python doesn't support when declaring FUNCTION
################
# Eva-l >> EvaluationError 			:> Error during evaluation (operations (math. Btw. you should kno what is evaluation))
################
# Typ-e >> TypeError				:> Adding two wrongs types of variable
# Div-0 >> DivisionByZero			:> trying to divide number by zero
################
# Exi-t >> GracefulExit				:> when interpreter ends interpreting or user calls `exit()`.
################
# Nam-e >> NameNotKnown				:> user tries to call but name of variable, function, etc. is not known.
################
# Mis-c >> MissingChar				:> when char is missing
# Mis-m >> MissingModule			:> Module is not found
# Mdc-M >> ModuleDoesntContainsThat :> User tries to import something that package does not provide
# Mis-p >> MissingParameter			:> parameter not given to function from modules
#   									(since in VAPL interpreter doesn't care)


class BasicError:
	notes = []

	def __init__(self, line_number, BaseContext, STOPCODE, OptionalContext=None, name=None, prefix="Error"):
		self.prefix = prefix[0:5]
		if OptionalContext is not None:
			context = OptionalContext
		else:
			context = BaseContext
		if name is None:
			name = type(self).__name__
		self.num, self.name, self.cont, self.stop = line_number, name, context, STOPCODE
		self.print_length()
		print(self)
		self.print_length()
		self.notes = []

	def AddNote(self, note: str):
		self.notes.append(f'NOTES | ' + ' ' * len(note))
		self.notes.append(note)
		self.notes.append(f'NOTES | ' + ' ' * len(note))

	def print_length(self):
		LEN1 = len(self.__repr__().split('\n')[0])
		LEN2 = len(self.__repr__().split('\n')[1])
		if LEN1 > LEN2:
			print(f"{self.prefix} | " + '-' * (LEN1 - 8))
		else:
			print(f"{self.prefix} | " + '-' * (LEN2 - 8))

	def __repr__(self):
		return f"{' ' * 8}{self.stop} | On line {self.num} happened: \n{' ' * 8}{self.stop} | {self.name} >> {self.cont}" + \
			   f'\n'.join(self.notes)


class IllegalVariableName(BasicError):
	def __init__(self, num, context=None): super().__init__(num, "Illegal Character in variable name", "Ill-v", context)


class IllegalFunctionName(BasicError):
	def __init__(self, num, context=None): super().__init__(num, "Illegal Character in function name", "Ill-f", context)


class EvaluationError(BasicError):
	def __init__(self, num, context=None):
		super().__init__(num,
						 "error during evaluation" if context is None else f"error during evalution > [{context}]",
						 "Eva-l")


class VTypeError(BasicError):
	def __init__(self, num):
		super().__init__(num, "You forgot the type of the variable.", "Typ-e", name="TypeError")


class DivisionByZero(BasicError):
	def __init__(self, num): super().__init__(num, "You can't divide by zero.", "Div-0")


class VSyntaxError(BasicError):
	def __init__(self, num, context): super().__init__(num, "invalid Syntax", "Stx-E", context, "SyntaxError")


class GracefulExit(BasicError):
	def __init__(self, num): super().__init__(num, "Exited gracefully", "Exi-t", prefix="GEXIT")


class NameNotKnown(BasicError):
	def __init__(self, num): super().__init__(num, f"Name not known", "Nam-e")


class MissingChar(BasicError):
	def __init__(self, num, char): super().__init__(num, f"Missing char {char}", "Mis-c")


class MissingParameter(BasicError):
	def __init__(self, num, func, param):
		super().__init__(num, f"""Function {func} requires {param.replace("'", '')}""", "Mis-P")


class MissingModule(BasicError):
	def __init__(self, num, moduleName): super().__init__(num, f"Module not found {moduleName}", "Mis-m")


class ModuleDoesntContainThat(BasicError):
	def __init__(self, num, n, moduleName): super().__init__(num, f"Cannot not find \'{n}\' in {moduleName}", "Mdc-t")


class Code:
	__slots__ = [
		'code',
		'line_number',
		'declaration',
		'globals',
		'locals',
		'modules',
		'paths',
		'rawCode',
		'exit',
		'debug',
		'BuiltIns',
		'replacement'
	]

	def __init__(self, SCRIPT_OR_PATH, IS_PATH: bool or int = False, debug=False):
		self.setup_new_code(SCRIPT_OR_PATH, IS_PATH, debug)
		self.declaration = {
			'function': 'define',
			'variable': 'var',
			'print': 'out',
			'BuiltIn': '$:',
			'if': 'if',
			'else': 'else',
			'then': 'then',
			'exit': 'exit',
			'module': '#[',
			'call': 'call',
			'1-line-comment-start': '%:',
			'm-line-comment-start': '%=',
			'm-line-comment-end': '=%',
			'path-start': '/*',
			'path-end': '*/'
		}
		self.replacement = {
			'BuiltIn': 'BuiltIn__'
		}

	def eval(self, expression):
		try:
			_expr = ast.parse(expression.replace(self.declaration['BuiltIn'], self.replacement['BuiltIn']),
							  '<expression>', mode='eval')
			for node in ast.walk(_expr):
				if isinstance(node, ast.Str):
					node.s = node.s.replace(self.replacement['BuiltIn'], self.declaration['BuiltIn'])
			COMPILE = compile(_expr, '<expression>', 'eval')
			return eval(expression, self.globals, self.locals)
		except ZeroDivisionError:
			DivisionByZero(self.line_number)
		except TypeError as Type:
			print(Type)
			VTypeError(self.line_number)
		except SyntaxError:
			VSyntaxError(self.line_number, expression)
		except NameError:
			NameNotKnown(self.line_number)
		except Exception as exc:
			EvaluationError(self.line_number, str(exc) + '::'+expression)

	def setup_new_code(self, SCRIPT_OR_PATH, IS_PATH: bool or int = False, debug=False):
		"""setups new code that can be run using run method."""

		def setup():
			self.paths = []
			self.modules = []
			self.line_number = 0
			self.debug = debug
			self.BuiltIns = {
				'name': 'VAPL',
				'ignore': None,
			}

			def execute(src):
				self.QuickSetupAndRun(src, AllowGracefulExit=False)

			self.globals = {'execute': execute, 'eval': self.eval}
			self.locals = {}

		if IS_PATH is True or IS_PATH == 1:
			file = open(SCRIPT_OR_PATH, 'r')
			self.code = file.read()
			self.rawCode = self.code
			file.close()
			setup()
		else:
			self.code = SCRIPT_OR_PATH
			self.rawCode = self.code
			setup()

	def QuickSetupAndRun(self, code, IS_FILEPATH=False, AllowGracefulExit=True):
		"""
		Setups new code, runs it and changes it back to old. \n
		Difference is that it saves and runs new code WITH old globals and locals variables, functions, paths,  etc.
		"""

		OldCode = self.code
		lineNumber = self.line_number
		Globals, Locals = self.globals, self.locals
		paths = self.paths
		self.setup_new_code(code, IS_FILEPATH)
		self.globals, self.locals = Globals, Locals
		self.run(AllowGracefulExit)
		self.setup_new_code(OldCode)
		self.line_number = lineNumber
		self.globals, self.locals = Globals, Locals
		self.paths = paths

	def configure_paths(self):
		"""
		configures and saves PATHS to dict
		"""
		if self.declaration['path-start'] not in self.code:
			self.code += self.declaration['path-start']
		if self.declaration['path-end'] not in self.code:
			self.code += self.declaration['path-end']
		self.paths = []
		START = self.code.find(self.declaration['path-start'])
		END = self.code.find(self.declaration['path-end'], START) + 2
		PATHS = self.code[START:END]
		self.code = self.code.replace(PATHS, "")
		PATHS = PATHS.replace(self.declaration['path-start'],
							  "").replace(self.declaration['path-end'], "")
		# ALL PATHS ARE COMPLETED AND DELETED FROM MAIN CODE.
		# NOW THEY WILL BE SAVED.
		for PATH in PATHS.split('\n'):
			PATH = self.remove_spaces_and_tabs(PATH)
			if PATH != "":
				TEXT = PATH.split(';>')[0]
				try:
					CODE = PATH.split(';>')[1]
				except:
					CODE = ""
				if TEXT.find('(') > -1 and TEXT.find(')') > -1:
					START = TEXT.find('(') + 1
					END = TEXT.find(')')
				else:
					START = 0
					END = 0
				PARAM = TEXT[START:END]
				TEXT = TEXT.replace(f"({PARAM})", "")
				payload = {
					'text':
						self.eval(
							str(self.remove_spaces_and_tabs(TEXT)).rstrip().rstrip(
								'\t').rstrip().rstrip('\t')),
					'param':
						PARAM,
					'code':
						CODE
				}
				self.paths.append(payload)

	def debug_print(self, *values, sep="", end='\n'):
		"""print function for debugging!"""
		if self.debug: print(str(values).lstrip('(').rstrip(')').replace(',', sep)
							 .lstrip("\'").lstrip('\"').rstrip("\'").rstrip('\"'), end)

	def get_response(self, UserInput: str) -> str:
		"""
		Returns response using UserInput and paths configured before \n
		(if none were configured then it would return "COMMANDS NOT FOUND")\n
		:return: str
		"""

		def match(text1, text2):
			return int(SequenceMatcher(None, text1, text2).ratio() * 100)

		UserInput = UserInput
		HIGHEST = {'payload': None, 'r': 0}
		MINIMUM = 90
		self.debug_print("GETTING RESPONSE")
		self.debug_print(end="")
		self.debug_print(self.paths, sep="\n", end="")
		for PATH in self.paths:
			print(PATH['text'])
			CMD_LEN = len(PATH['text'].rstrip().split(' '))
			CMD = PATH['text'].lower().rstrip().lstrip()
			UserInputCMD = ' '.join(UserInput.rstrip().split(' ')[0: CMD_LEN])
			R = match(UserInputCMD.lower(), CMD)
			self.debug_print(f'ratio of [\"{CMD}\"]/[\"{UserInputCMD}\"] is {R}', end="")
			if R > HIGHEST['r']:
				HIGHEST['payload'] = PATH
				HIGHEST['r'] = R
		self.debug_print()
		self.debug_print(HIGHEST, sep="\n", end="")
		if HIGHEST['r'] >= MINIMUM:
			CMD_LEN = len(HIGHEST['payload']['text'].split(' ')) - 1
			CMD = HIGHEST['payload']['text'].lower()
			UserInputCMD = ' '.join(UserInput.split(' ')[CMD_LEN: len(UserInput.split(' ')) + 1])
			INPUT_PARAM = '"' + UserInputCMD + '"'
			self.debug_print(f"INPUT_PARAM: |{INPUT_PARAM}| :")
			if not INPUT_PARAM != "" and not HIGHEST['payload']['param'] != "":
				print("Parameters not given.")
				print("Try again.")
				return "Parameters not given. Try again later with parameters!"
			else:
				INPUT_PARAM = self.eval(INPUT_PARAM)
				old_stdout = sys.stdout  # Memorize the default stdout stream
				sys.stdout = buffer = StringIO()
				self.locals[HIGHEST['payload']['param']] = INPUT_PARAM
				print("Executing command " + HIGHEST['payload']['text'])
				self.execute_line(HIGHEST['payload']['code'])
				sys.stdout = old_stdout  # Put the old stream back in place
				whatWasPrinted = buffer.getvalue()
				print(whatWasPrinted.encode().decode())
				return whatWasPrinted
		else:
			print("No commands found")
			return "No commands found"

	def exclude_comments(self):
		text = self.code
		Start, End = self.declaration['m-line-comment-start'], self.declaration['m-line-comment-start']
		output = sub("%s(.*?)%s" % (escape(Start.replace("\n", "/=n")), escape(End.replace("\n", "/=n"))), "",
					 text.replace("\n", "/=n")).replace("/=n", "\n")
		Start = self.declaration['1-line-comment-start']
		End = "\n"
		output = sub("%s(.*?)%s" % (escape(Start.replace("\n", "/=n")), escape(End.replace("\n", "/=n"))), "",
					 text.replace("\n", "/=n")).replace("/=n", "\n")
		self.code = output

	def run(self, AllowGracefulError=True):
		"""Runs code from setup"""
		self.exclude_comments()
		self.configure_paths()
		self.code = self.code.split('\n')
		while self.line_number + 1 < len(self.code):
			line = self.code[self.line_number]
			self.execute_line(line)
			self.next_line()
		if self.line_number + 1 == len(self.code) and AllowGracefulError:
			GracefulExit(self.line_number + 2)

	def exec(self, code):
		try:
			code = ast.parse(code, '<string>', mode='exec')
			for node in ast.walk(code):
				if isinstance(node, ast.Str):
					node.s = node.s.replace(self.replacement['BuiltIn'], self.declaration['BuiltIn'])
			code = compile(code, '<string>', 'eval')
			exec(code, self.globals, self.locals)
		except NameError:
			NameNotKnown(self.line_number)
		except ModuleNotFoundError as err:
			MissingModule(self.line_number, err)
		except ImportError as Iee:
			print(Iee)
			ModuleDoesntContainThat(self.line_number, Iee, Iee)
		except SyntaxError:
			VSyntaxError(self.line_number, 'Check your syntax!')
		except TypeError as Type:
			print(Type)
			if not str(Type).startswith("unsupported operand type(s) for"):
				FUNC = str(Type).split(' ')[0]
				PARAMS = ''#str(Type).split(':')[1]
				MissingParameter(self.line_number, FUNC, PARAMS)
			else:
				VTypeError(self.line_number)

	def loop_for_more_context(self, text, char1, char2):
		while char1 not in text or char2 not in text or text.count(char1) != text.count(char2):
			text += '\n' + self.remove_spaces_and_tabs(self.next_line())
		return text

	def next_line(self):
		"""DO NOT USE!!!"""
		if self.line_number + 1 < len(self.code):
			self.line_number += 1
		line = self.code[self.line_number]
		return '\n' + line

	def execute_line(self, line: str):
		"""Do not use! It is only necessary to use in method run!\n When used inappropriately it can return lots of bugs!"""

		def capture_missing_chars(char):
			if char not in line: MissingChar(self.line_number, char)

		first = self.remove_spaces_and_tabs(line).split(" ")[0]
		line = self.remove_spaces_and_tabs(line)
		if self.declaration['module'] in first:
			capture_missing_chars('[')
			capture_missing_chars(']')
			NAME = line.split('[')[1].split(']')[0]
			line = line.replace(NAME, "")
			if line.find('>') > -1:
				ImportSomething = self.remove_spaces_and_tabs(line.split('>')[1])
			else:
				ImportSomething = ""
			if line.find('{') > -1 and line.find('}') > -1:
				AsSomething = self.remove_spaces_and_tabs(line.split('{')[1].split('}')[0])
			else:
				AsSomething = ""
			if AsSomething != "" and ImportSomething != "":
				RESULT = f"from {NAME} import {ImportSomething} as {AsSomething}"
				self.exec(RESULT)
			elif ImportSomething != "":
				RESULT = f"from {NAME} import {ImportSomething}"
				self.exec(RESULT)
			elif AsSomething != "":
				RESULT = f"import {NAME} as {AsSomething}"
				self.exec(f"import {NAME} as {AsSomething}")
			else:
				RESULT = f"import {NAME}"
				self.exec(RESULT)

		elif self.declaration['function'] in first:

			NAME = line.split(self.declaration['function'])[1].split('(')[0]
			PARAMS = line.split('(')[1].split(')')[0]
			CODE = '{' + line.split('{')[1]

			CODE = self.loop_for_more_context(CODE, '{', '}')
			CODE = CODE.rstrip('}').lstrip('{')
			CONVERT = ""
			RECONVERT = ""
			if self.remove_spaces_and_tabs(PARAMS):
				for num, par in enumerate(PARAMS.split(',')):
					CONVERT += f"{par} = PARS[{num}]\n"
					RECONVERT += f"del {par}\n"
			# CONVERT, RECONVERT = "", ""
			BASE_FUNCTION = \
				f"""def {NAME} (*PARS):\n{CONVERT}\n  execute('''{CODE}''')\n{RECONVERT}	
			"""
			self.exec(BASE_FUNCTION)

		elif self.declaration['variable'] in first:
			NAME = self.remove_spaces_and_tabs(
				self.remove_spaces_and_tabs(line).lstrip(self.declaration['variable']).split("=")[0])
			if line.find("=") != -1:
				VALUE = self.remove_spaces_and_tabs(line.split("=")[1])
				if VALUE == "":
					VALUE = None
			else:
				VALUE = None
			print(NAME, ' = ', VALUE)
			self.globals[NAME] = VALUE
			print(self.globals[NAME])
			# self.exec(f"{NAME} = {VALUE}")

		elif self.declaration['BuiltIn'] in first:
			NAME = self.remove_spaces_and_tabs(line.split('=')[0].lstrip(self.declaration['BuiltIn']))
			if NAME == "":
				VSyntaxError(self.line_number, f'can\'t edit \'{self.declaration["BuiltIn"]}\'')
			VALUE = self.eval(self.remove_spaces_and_tabs(line.split('=')[1]))
			if VALUE == "":
				VSyntaxError(self.line_number, f'tried to assign nothing to \'{self.declaration["BuiltIn"]}:{VALUE}\'')
			for builtin in self.BuiltIns:
				if NAME.lower() == builtin:
					self.globals[f'{self.declaration["BuiltIn"]}:{NAME}'] = VALUE
					break
			else:
				VSyntaxError(self.line_number, f'\'$\' doesn\'t have {NAME}')

		elif self.declaration['if'] in first:
			statement = line[line.find(self.declaration['if']) + len(self.declaration['if']):line.find(')') + 1]
			code = line.split('{')[1] + "{"
			code = self.loop_for_more_context(code, '{', '}')
			code = code.lstrip("{").rstrip("}")

			if self.eval(statement):
				for line in str(code).split('\n'):
					self.execute_line(line)

		elif self.declaration['print'] in first:
			PRINT = line.split(self.declaration['print'])[1].lstrip(':')
			print("CODE  | ", self.eval(PRINT))

		elif self.declaration['exit'] in first:
			GracefulExit(self.line_number)

		elif self.declaration['call'] in first:
			# I COULD MAKE THAT SO WHEN "self.globals in first or self.locals in first: ..." instead of new CALL
			# but with it this language is now special!
			FUNCTION = self.remove_spaces_and_tabs(line.split(self.declaration['call'])[1].lstrip(':'))
			self.exec(FUNCTION)

		elif self.remove_spaces_and_tabs(line) != "":
			VSyntaxError(self.line_number, line)

	def get_commands(self):
		"""get all possible commands!"""
		return self.paths

	@staticmethod
	def remove_spaces_and_tabs(text: str):
		"""Removes spaces and tabs from the start of the string"""
		return text.lstrip().lstrip('\t').lstrip().lstrip('\t')


class Web:
	__slots__ = [
		'app',
		'code',
		'debug'
	]

	def __init__(self, connect_to_server: bool = False, code: Code = Code(""), debug: bool = False):
		"""Flask object to run code, so you will just need to create code for assistant and save time."""
		self.debug: bool = debug
		if connect_to_server is False:
			print(dirname(__file__))
			self.app = Flask(
				abspath(__file__),
				root_path=dirname(__file__),
				template_folder="",
				static_folder=""
			)
			self.print_all()
			self.code = code
		else:
			pass

	def print_all(self):
		self.debug_print('========================================')
		self.debug_print("FLASK            >> " + self.app.instance_path[0: self.app.instance_path.rfind('\\')])
		self.debug_print('========================================')
		self.debug_print("FLASK NAME       >> " + self.app.name)
		self.debug_print("ROOT PATH        >> " + self.app.root_path)
		self.debug_print("TEMPLATE FOLDER  >> " + self.app.template_folder)
		self.debug_print("STATIC FOLDER    >> " + self.app.static_folder)
		self.debug_print('========================================')

	def debug_print(self, *text, sep=",", end="\n"):
		if self.debug is True:
			print(sep.join(text), end=end)

	def run_tutorial(self, host, port, debug: bool = False):
		"""
		runs welcome page with the documentation!
		In this mode you can't make voice assistants and any other things similar as it does not provide to do it :(
		"""

		@self.app.route('/docs', methods=['GET'])
		def DOCUMENTATION():
			return render_template('docs.html')

		@self.app.route('/', methods=['GET'])
		def index():
			return render_template('index.html')

		@self.app.route('/code', methods=['get', 'post'])
		def run():
			code = str(request.form['code'])
			print(code)
			old_stdout = sys.stdout  # Memorize the default stdout stream
			sys.stdout = buffer = StringIO()
			try:
				self.code.setup_new_code(code)
				self.code.run()
			except:
				print("Err: " + str(self.code.line_number), str(), sep="=:")
			sys.stdout = old_stdout  # Put the old stream back in place
			whatWasPrinted = buffer.getvalue()
			print(whatWasPrinted)
			return whatWasPrinted

		@self.app.errorhandler(404)
		def PageNotFound(url):
			url = request.base_url.lstrip("http://").lstrip('https://').lstrip(request.host).lstrip('/')
			return make_response(render_template('PageNotFound.html', URL=url), 404)

		self.app.run(host=host, port=port, debug=debug)

	def run(self, host, port, debug: bool = False, HTML_PAGE=None, ssl_certificate=None):
		if HTML_PAGE is None:
			path = abspath(__file__)[len(self.app.root_path) + 1:__file__.rfind('\\')]
			HTML_PAGE = "Executer.html"
			self.app.static_folder = "static"
			self.app.template_folder = "templates"
			del path
		else:
			self.app.root_path = self.app.instance_path[0: self.app.instance_path.rfind('\\')]
		self.print_all()
		code = str(self.code.rawCode)
		old_stdout = sys.stdout  # Memorize the default stdout stream
		sys.stdout = buffer = StringIO()
		try:
			self.code.setup_new_code(code)
			self.code.run()
		except:
			print("Err: " + str(self.code.line_number), str(), sep="=:")
		sys.stdout = old_stdout  # Put the old stream back in place
		whatWasPrinted = buffer.getvalue()
		PRE_COMMANDS = self.code.get_commands()
		COMMANDS = "<ul>"
		for command in PRE_COMMANDS:
			COMMANDS += '<li>' + str(command['text']) + '<a>' + command['param'] + '</a>' + '<br>'
		COMMANDS += "</ul>"

		@self.app.route('/', methods=['GET', 'POST'])
		def execute():
			try:
				return render_template(HTML_PAGE, output=whatWasPrinted, COMMANDS=str(COMMANDS))
			except Exception as Exc:
				return "Error " + str(Exc)

		@self.app.route('/cmd', methods=['GET', 'POST'])
		def cmd():
			TEXT = request.form['TEXT']
			print(TEXT)
			return self.code.get_response(TEXT)

		self.app.run(host=host, port=port, debug=debug, ssl_context=ssl_certificate)
