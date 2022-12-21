from flask import Flask, render_template, request, make_response
from io import StringIO
from re import sub, escape
from difflib import SequenceMatcher
import sys

Version = '0.0.108'
# LIST OF ERRORS
################
# Ill-v >> IllegalVariableName 	:> Char that python doesn't support when declaring VARIABLE
# Ill-f >> IllegalFunctionName 	:> Char that python doesn't support when declaring FUNCTION
################
# Eva-l >> EvaluationError 		:> Error during evaluation (operations (math. Btw. you should kno what is evaluation))
################
# Typ-e >> TypeError			:> Adding two wrongs types of variable
# Div-0 >> DivisionByZero		:> trying to divide number by zero
################
# Exi-t >> GracefulExit			:> when interpreter ends interpreting or user calls `exit()`.
################
# Nam-e >> NameNotKnown			:> user tries to call but name of variable, function, etc. is not known.
################
# Mis-c >> MissingChar			:> when char is missing
# Mis-m >> MissingModule		:> Module is not found

class BasicError:
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

	def print_length(self):
		LEN1 = len(self.__repr__().split('\n')[0])
		LEN2 = len(self.__repr__().split('\n')[1])
		if LEN1 > LEN2:
			print(f"{self.prefix} | " + '-' * (LEN1 - 8))
		else:
			print(f"{self.prefix} | " + '-' * (LEN2 - 8))

	def __repr__(self):
		return f"{' '*8}{self.stop} | On line {self.num} happened: \n{' '*8}{self.stop} | {self.name} >> {self.cont}"


class IllegalVariableName(BasicError):
	def __init__(self, num, context=None): super().__init__(num, "Illegal Character in variable name", "Ill-v", context)


class IllegalFunctionName(BasicError):
	def __init__(self, num, context=None): super().__init__(num, "Illegal Character in function name", "Ill-f", context)


class EvaluationError(BasicError):
	def __init__(self, num, context=None):
		super().__init__(num,
						 "error during evaluation" if context is not None else f"error during evalution >{context}<",
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


class MissingModule(BasicError):
	def __init__(self, num, moduleName): super().__init__(num, f"Module not found {moduleName}", "Mis-m")

class NotInModule(BasicError):
	def __init__(self, num, n, moduleName): super().__init__(num, f"Cannot not find \'{n}\' in {moduleName}")

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
		'debug'
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

	def eval(self, expression):
		try:
			return eval(expression, self.globals, self.locals)
		except ZeroDivisionError:
			DivisionByZero(self.line_number)
		except TypeError:
			VTypeError(self.line_number)
		except Exception as err:
			EvaluationError(self.line_number, expression)

	def setup_new_code(self, SCRIPT_OR_PATH, IS_PATH: bool or int = False, debug=False):
		"""setups new code that can be run using run method."""
		def setup():
			self.locals = {}
			self.globals = {}
			self.paths = []
			self.modules = []
			self.line_number = 0
			self.debug = debug

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

	def QuickSetupAndRun(self, Code, IS_FILEPATH=False, AllowGracefulExit=True):
		"""
		Setups new code, runs it and changes it back to old. \n
		Difference is that it saves and runs new code WITH old globals and locals variables, functions, paths,  etc.
		"""

		OldCode = self.code
		lineNumber = self.line_number
		Globals, Locals = self.globals, self.locals
		paths = self.paths
		self.setup_new_code(Code, IS_FILEPATH)
		self.globals, self.locals = Globals, Locals
		self.run(AllowGracefulExit)
		self.setup_new_code(OldCode)
		self.line_number = lineNumber
		self.globals, self.locals = Globals, Locals
		self.paths = paths

	def configure_PATHS(self):
		"""
		configures and saves PATHS to dict
		"""
		if self.declaration['path-start'] not in self.code: self.code += self.declaration['path-start']
		if self.declaration['path-end'] not in self.code: self.code += self.declaration['path-end']
		self.paths = []
		START = self.code.find(self.declaration['path-start'])
		END = self.code.find(self.declaration['path-end'], START) + 2
		PATHS = self.code[START:END]
		self.code = self.code.replace(PATHS, "")
		PATHS = PATHS.replace(self.declaration['path-start'], "").replace(self.declaration['path-end'], "")
		# ALL PATHS ARE COMPLETED AND DELETED FROM MAIN CODE.
		# NOW THEY WILL BE SAVED.
		for PATH in PATHS.split('\n'):
			PATH = self.RemoveSpacesAndTabs(PATH)
			if PATH != "":
				TEXT = PATH.split(';>')[0]
				try: CODE = PATH.split(';>')[1]
				except: CODE = ""
				START = TEXT.find('(') + 1
				END = TEXT.find(')', START)
				PARAM = TEXT[START:END]
				TEXT = TEXT.replace(f"({PARAM})", "")
				payload = {
					'text': eval(str(self.RemoveSpacesAndTabs(TEXT)).rstrip().rstrip('\t').rstrip().rstrip('\t')),
					'param': PARAM,
					'code': CODE
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
		for PATH in self.paths:
			CMD_LEN = len(PATH['text'].split(' '))
			CMD = PATH['text'].lower().rstrip().lstrip()
			UserInputCMD = ' '.join(UserInput.split(' ')[0: CMD_LEN-1])
			R = match(UserInputCMD.lower(), CMD)
			self.debug_print(f'ratio of [\"{CMD}\"]/[\"{UserInputCMD}\"] is {R}', end="")
			if R > HIGHEST['r']:
				HIGHEST['payload'] = PATH
				HIGHEST['r'] = R
		self.debug_print()
		self.debug_print(HIGHEST, sep="\n", end="")
		self.debug_print(end="")
		self.debug_print(self.paths, sep="\n", end="")
		if HIGHEST['r'] >= MINIMUM:
			CMD_LEN = len(HIGHEST['payload']['text'].split(' '))-1
			CMD = HIGHEST['payload']['text'].lower()
			UserInputCMD = ' '.join(UserInput.split(' ')[CMD_LEN: len(UserInput.split(' '))])
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
				print(whatWasPrinted)
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
		self.configure_PATHS()
		self.code = self.code.split('\n')
		while self.line_number + 1 < len(self.code):
			line = self.code[self.line_number]
			self.execute_line(line)
			self.next_line()
		if self.line_number + 1 == len(self.code) and AllowGracefulError:
			GracefulExit(self.line_number + 2)

	def exec(self, code):
		try:
			exec(code, self.globals, self.locals)
		except NameError:
			NameNotKnown(self.line_number)
		except ModuleNotFoundError as err:
			print(err)
			MissingModule(self.line_number, err)
		except ImportError as Iee:
			print(Iee)
			NotInModule(self.line_number, Iee, Iee)
		except SyntaxError:
			VSyntaxError(self.line_number, "Check your syntax ")


	def loop_for_more_context(self, text, char1, char2):
		while char1 not in text or char2 not in text or text.count(char1) != text.count(char2):
			text += '\n' + self.RemoveSpacesAndTabs(self.next_line())
		return text

	def next_line(self):
		"""DO NOT USE!!!"""
		if self.line_number + 1 < len(self.code):
			self.line_number += 1
		line = self.code[self.line_number]
		return '\n' + line

	def execute_line(self, line: str):
		"""Do not use! It is only necessary to use in method run!\n When used inappropriately it can return lots of bugs!"""
		def CaptureMissingChars(char):
			if char not in line: MissingChar(self.line_number, char)

		first = self.RemoveSpacesAndTabs(line).split(" ")[0]
		line = self.RemoveSpacesAndTabs(line)
		if self.declaration['module'] in first:
			CaptureMissingChars('[')
			CaptureMissingChars(']')
			NAME = line.split('[')[1].split(']')[0]
			line = line.replace(NAME, "")
			ImportSomething =self.RemoveSpacesAndTabs(line.split('>')[1]) if line.count('>') > -1 else ""
			if line.count('{') > -1 and line.count('}') > -1:
				AsSomething = self.RemoveSpacesAndTabs(line.split('{')[1].split('}')[0])
			else: AsSomething = ""
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
			print(RESULT)

		elif self.declaration['function'] in first:

			NAME = line.split(self.declaration['function'])[1].split('(')[0]
			PARAMS = line.split('(')[1].split(')')[0]
			CODE = '{' + line.split('{')[1]

			CODE = self.loop_for_more_context(CODE, '{', '}')
			CODE = CODE.rstrip('}').lstrip('{')
			CONVERT = ""
			RECONVERT = ""
			if self.RemoveSpacesAndTabs(PARAMS):
				for num, par in enumerate(PARAMS.split(',')):
					CONVERT += f"{par} = PARS[{num}]\n"
					RECONVERT += f"del {par}\n"
			CONVERT, RECONVERT = "", ""
			BASE_FUNCTION = \
				f"""def {NAME} (*PARS):\n{CONVERT}\n  execute('''{CODE}''')\n{RECONVERT}	
			"""
			self.exec(BASE_FUNCTION)

		elif self.declaration['variable'] in first:
			NAME = self.RemoveSpacesAndTabs(
				self.RemoveSpacesAndTabs(line).lstrip(self.declaration['variable']).split("=")[0])
			if line.find("=") != -1:
				VALUE = self.RemoveSpacesAndTabs(line).split("=")[1]
				if self.RemoveSpacesAndTabs(VALUE) == "":
					VALUE = None
			else:
				VALUE = None
			self.exec(f"{NAME} = {VALUE}")

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
			FUNCTION = self.RemoveSpacesAndTabs(line.split(self.declaration['call'])[1].lstrip(':'))
			self.exec(FUNCTION)

		elif self.RemoveSpacesAndTabs(line) != "":
			VSyntaxError(self.line_number, line)

	def getCommands(self):
		"""get all possible commands!"""
		return self.paths

	@staticmethod
	def RemoveSpacesAndTabs(text: str):
		"""Removes spaces and tabs from the start of the string"""
		return text.lstrip().lstrip('\t').lstrip().lstrip('\t')


class Web:
	__slots__ = [
		'app',
		'code'
	]

	def __init__(self, connect_to_server: bool = False, code: Code = Code("")):
		"""Flask object to run code, so you will just need to create code for assistant and save time."""
		if connect_to_server is False:
			self.app = Flask(__name__)
			self.code = code
		else:
			pass

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

	def run(self, host, port, debug: bool = False, HTML_PAGE="Executer.html", ssl_certificate=None):
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
		PRE_COMMANDS = self.code.getCommands()
		COMMANDS = "<ul>"
		for command in PRE_COMMANDS:
			COMMANDS += '<li>' + command['text'] + '<a>' + command['param'] + '</a>' + '<br>'
		COMMANDS += "</ul>"

		@self.app.route('/', methods=['GET', 'POST'])
		def execute():
			return render_template(HTML_PAGE, output=whatWasPrinted, COMMANDS=str(COMMANDS))

		@self.app.route('/cmd', methods=['GET', 'POST'])
		def cmd():
			TEXT = request.form['TEXT']
			print(TEXT)
			return self.code.get_response(TEXT)

		self.app.run(host=host, port=port, debug=debug, ssl_context=ssl_certificate)
