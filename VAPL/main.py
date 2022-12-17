from flask import Flask, render_template, request, make_response
from io import StringIO
from re import sub, escape
from difflib import SequenceMatcher
import sys


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


class BasicError:
	def __init__(self, line_number, BaseContext, STOPCODE, OptionalContext=None, name=None):
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
		if LEN1 > LEN2: print("Error | "+'-'*(LEN1-8))
		else: 			print("Error | "+'-' * (LEN2-8))

	def __repr__(self):
		return f"\t{self.stop} | On line {self.num} happened: \n\t{self.stop} | {self.name} >> {self.cont}"


class IllegalVariableName(BasicError):
	def __init__(self, num, context=None): super().__init__(num, "Illegal Character in variable name", "Ill-v", context)


class IllegalFunctionName(BasicError):
	def __init__(self, num, context=None): super().__init__(num, "Illegal Character in function name", "Ill-f", context)


class EvaluationError(BasicError):
	def __init__(self, num, context=None):
		super().__init__(num,
						 "error during evaluation" if context is not None else f"error during evalution >{context}<"
						 , "Eva-l")


class VTypeError(BasicError):
	def __init__(self, num, context=None):
		super().__init__(num, "You forgot the type of the variable.", "Typ-e", name="TypeError")


class DivisionByZero(BasicError):
	def __init__(self, num): super().__init__(num, "You can't divide by zero.", "Div-0")


class VSyntaxError(BasicError):
	def __init__(self, num, context): super().__init__(num, "invalid Syntax", "Stx-E", "SyntaxError", context)


class GracefulExit(BasicError):
	def __init__(self, num): super().__init__(num, "Exited gracefully", "Exi-t")


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
		'exit'
	]

	def __init__(self, SCRIPT_OR_PATH, IS_PATH: bool or int = False):
		if IS_PATH is True or IS_PATH == 1:
			file = open(SCRIPT_OR_PATH, 'r')
			self.code = file.read()
			file.close()
		else:
			self.code = SCRIPT_OR_PATH

		self.line_number = 0
		self.declaration = {
			'function': 'define',
			'variable': 'var',
			'print': 'out',
			'BuiltIn': '$:',
			'if': 'if',
			'else': 'else',
			'then': 'then',
			'exit': 'exit',
			'module': '#Inlcude',
			'1-line-comment-start': '%:',
			'm-line-comment-start': '%=',
			'm-line-comment-end': '=%',
			'path-start': '/*',
			'path-end': '*/'
		}
		self.globals = {'execute': self.run, 'eval': self.eval}
		self.locals = {}
		self.modules = []
		self.paths = []
		self.rawCode = self.code

	def eval(self, expression):
		try:
			return eval(expression, self.globals, self.locals)
		except ZeroDivisionError:
			DivisionByZero(self.line_number)
		except TypeError:
			VTypeError(self.line_number)
		except Exception as err:
			EvaluationError(self.line_number, expression)

	def setup_new_code(self, SCRIPT_OR_PATH, IS_PATH: bool or int = False):
		if IS_PATH is True or IS_PATH == 1:
			file = open(SCRIPT_OR_PATH, 'r')
			self.code = file.read()
			file.close()
			self.globals = {'execute': self.execute_line, 'eval': self.eval}
			self.locals = {}
		else:
			self.code = SCRIPT_OR_PATH

	def QuickSetupAndRun(self, Code, IS_FILEPATH=False):
		"""Setups new code, runs it and changes it back to old"""
		OldCode = self.code
		self.setup_new_code(Code, IS_FILEPATH)
		self.run()
		self.setup_new_code(OldCode)

	def configure_PATHS(self):
		if self.declaration['path-start'] not in self.code: self.code += self.declaration['path-start']
		if self.declaration['path-end'] not in self.code: self.code += self.declaration['path-end']
		START = self.code.find(self.declaration['path-start'])
		END = self.code.find(self.declaration['path-end'], START) + 2
		PATHS = self.code[START:END]
		self.code = self.code.replace(PATHS, "")
		PATHS = PATHS.replace(self.declaration['path-start'], "").replace(self.declaration['path-end'], "")
		# ALL PATHS ARE COMPLETED AND DELETED FROM MAIN CODE
		# NOW THEY WILL BE SAVED
		for PATH in PATHS.split('\n'):
			PATH = self.RemoveSpacesAndTabs(PATH)
			if PATH != "":
				TEXT = PATH.split(';>')[0]
				try: CODE = PATH.split(';>')[1]
				except: CODE = ""
				START = TEXT.find('(')+1
				END = TEXT.find(')', START)
				PARAM = TEXT[START:END]
				TEXT = TEXT.replace(f"({PARAM})", "")
				payload = {
					'text': eval(str(self.RemoveSpacesAndTabs(TEXT)).rstrip().rstrip('\t').rstrip().rstrip('\t')),
					'param': PARAM,
					'code': CODE
				}
				print(payload)
				self.paths.append(payload)

	def get_response(self, UserInput: str):
		def match(text1, text2): return int(SequenceMatcher(None, text1, text2).ratio() * 100)

		UserInput = UserInput.lower()
		HIGHEST = {'payload': None, 'r': 0}
		MINIMUM = 50
		for PATH in self.paths:
			R = match(UserInput, PATH['text'])
			if R > HIGHEST['r']:
				HIGHEST['payload'] = PATH
				HIGHEST['r'] = R
		if HIGHEST['r'] >= MINIMUM:
			INPUT_PARAM = '"' + UserInput.lower().replace(HIGHEST['payload']['text'].lower(), "")+'"'
			if not INPUT_PARAM != "" and not HIGHEST['payload']['param'] != "":
				print("Parameters not given.")
				print("Try again.")
			else:
				INPUT_PARAM = self.eval(INPUT_PARAM)
				self.locals[HIGHEST['payload']['param']] = INPUT_PARAM
				print("Executing command " + HIGHEST['payload']['text'])
				self.execute_line(HIGHEST['payload']['code'])
		else:
			print("No commands found")

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

	def run(self):
		"""Runs code from setup"""
		self.exclude_comments()
		self.configure_PATHS()
		self.code = self.code.split('\n')
		while self.line_number + 1 < len(self.code):
			line = self.code[self.line_number]
			self.execute_line(line)
			self.next_line()
		if self.line_number + 1 == len(self.code):
			GracefulExit(self.line_number + 2)

	def exec(self, code):
		exec(code, self.globals, self.locals)
		return

	def loop_for_more_context(self, text, char1, char2):
		while char1 not in text or char2 not in text or text.count(char1) != text.count(char2):
			text += "\n" + self.RemoveSpacesAndTabs(self.next_line())
		return text

	def next_line(self):
		"""DO NOT USE!!!"""
		if self.line_number + 1 < len(self.code):
			self.line_number += 1
		line = self.code[self.line_number]
		return line

	def execute_line(self, line: str):
		"""Do not use! It is only necessary to use in method run!\n When used inappropriately it can return lots of bugs!"""
		first = self.RemoveSpacesAndTabs(line).split(" ")[0]
		line = self.RemoveSpacesAndTabs(line)
		if self.declaration['function'] in first:

			NAME = line.lstrip(self.declaration['function']).split(' ')[0]
			PARAMS = line.split('(')[0].split(')')[1]
			CODE = line.split('{')[1]

			CODE = self.loop_for_more_context(CODE, '{', '}')
			CODE.rstrip('}')

			CONVERT = ""
			RECONVERT = ""
			if self.RemoveSpacesAndTabs(PARAMS):
				for num, par in enumerate(PARAMS.split(',')):
					CONVERT += f"{par} = PARS[{num}]"
					RECONVERT += f"{par} = None"

			BASE_FUNCTION = \
				f"""
			def {NAME} (*PARS):
			\t{CONVERT}
			\tfor line in str(CODE).split('\n'):
			\t\texecute(line)
			\t{RECONVERT}	
			"""
			self.exec(BASE_FUNCTION)

		elif self.declaration['variable'] in first:
			NAME = self.RemoveSpacesAndTabs(
				self.RemoveSpacesAndTabs(line).lstrip(self.declaration['variable']).split("=")[0])
			VALUE = self.eval(self.RemoveSpacesAndTabs(line).lstrip(self.declaration['variable']).split("=")[1])
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
			PRINT = self.RemoveSpacesAndTabs(line).lstrip(self.declaration['print']).lstrip(':')
			print("CODE  | ", self.eval(PRINT))

		elif self.declaration['exit'] in first:
			GracefulExit(self.line_number)

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
		run welcome page with the documentation!
		In this mode you can't make assistant :(
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
		COMMANDS = ""
		for command in PRE_COMMANDS:
			COMMANDS += command.replace(':', '<a>').replace(';', '</a>').replace('--', '<a2>').replace('-', '</a2>')

		@self.app.route('/', methods=['GET', 'POST'])
		def execute():
			return render_template(HTML_PAGE, output=whatWasPrinted, COMMANDS=COMMANDS)

		self.app.run(host=host, port=port, debug=debug, ssl_context=ssl_certificate)
