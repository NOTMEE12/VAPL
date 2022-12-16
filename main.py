from flask import Flask, render_template, request, make_response
from io import StringIO
from re import sub, escape
import sys

class Code:

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
							'module': '#Inlcude',
							'1-line-comment-start': '%:',
							'm-line-comment-start': '%=',
							'm-line-comment-end': '=%',
							'path-line-start': '/*',
							'path-line-end': '*/'
						   }
		self.globals 	= {'execute': self.run, 'eval': self.eval}
		self.locals 	= {}
		self.modules 	= []
		self.paths		= []
		self.rawCode	= self.code

		class BasicError:
			def __init__(self, line_number, name, context, STOPCODE):
				self.num, self.name, self.cont, self.stop = line_number, name, context, STOPCODE
				print(f"{STOPCODE}:{line_number}|{name}> {context}")

			def __repr__(self):
				return f"{self.stop}:{self.num}|{self.name}> {self.cont}"
		class IllegalVariableName(BasicError):
			def __init__(self, num, context): super().__init__(num, "IllegalVariableName", context, "000-0")
		class IllegalFunctionName(BasicError):
			def __init__(self, num, context): super().__init__(num, "IllegalFunctionName", context, "000-1")
		self.Errs = {
					'IllegalVariableName': IllegalVariableName
					}

	def eval(self, expression):
		return eval(expression, self.globals, self.locals)


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


	def run(self):
		"""Runs code from setup"""
		self.code = self.code.split('\n')
		while self.line_number+1 < len(self.code):
			line = self.code[self.line_number]
			self.execute_line(line)
			self.NextLine()

	def exec(self, code):
		exec(code, self.globals, self.locals)
		return

	def NextLine(self):
		"""DO NOT USE!!!"""
		if self.line_number+1 < len(self.code):
			self.line_number += 1
		line = self.code[self.line_number]
		return line

	def execute_line(self, line: str):
		"""Do not use! It is only necessary to use in method run!\n When used inappropriately it can return lots of bugs!"""
		def exclude_comments(text):
			Start, End = self.declaration['m-line-comment-start'], self.declaration['m-line-comment-start']
			output = sub("%s(.*?)%s" % (escape(Start.replace("\n", "/=n")), escape(End.replace("\n", "/=n"))), "",
					text.replace("\n", "/=n")).replace("/=n", "\n")
			Start = self.declaration['1-line-comment-start']
			End = "\n"
			output = sub("%s(.*?)%s" % (escape(Start.replace("\n", "/=n")), escape(End.replace("\n", "/=n"))), "",
						 text.replace("\n", "/=n")).replace("/=n", "\n")
			return output

		line = exclude_comments(line)
		first = line.split(" ")[0]
		if self.declaration['function'] in first:
			NAME = line.lstrip(self.declaration['function']).split(' ')[0]
			PARAMS = line.split('(')[0].split(')')[1]
			CODE = line.split('{')[1]
			while "{" not in CODE or "}" not in CODE or CODE.count('{') != CODE.count('}'):
				CODE += "\n" + self.NextLine()
			CODE.rstrip('}')

			CONVERT = ""
			DECONVERT = ""
			if self.RemoveSpacesAndTabs(PARAMS):
				for num, par in enumerate(PARAMS.split(',')):
					CONVERT += f"{par} = PARS[{num}]"
					DECONVERT += f"{par} = None"
			BASE_FUNCTION = \
			f"""
			def {NAME} (*PARS):
			\t{CONVERT}
			\tfor line in str(CODE).split('\n'):
			\t\texecute(line)
			\t{DECONVERT}	
			"""
			self.exec(BASE_FUNCTION)

		elif self.declaration['variable'] in first:
			NAME = self.RemoveSpacesAndTabs(self.RemoveSpacesAndTabs(line).lstrip(self.declaration['variable']).split("=")[0])
			VALUE = self.eval(self.RemoveSpacesAndTabs(line).lstrip(self.declaration['variable']).split("=")[1])
			self.exec(f"{NAME} = {VALUE}")

		elif self.declaration['if'] in first:
			statement = line[line.find(self.declaration['if'])+len(self.declaration['if']):line.find(')')+1]
			code = line.split('{')[1] + "{"
			while "{" not in code or "}" not in code or code.count('{') != code.count('}'):
				code += "\n" + self.RemoveSpacesAndTabs(self.NextLine())
			code = code.lstrip("{").rstrip("}")

			if self.eval(statement):
				for line in str(code).split('\n'):
					self.execute_line(line)

		elif self.declaration['print'] in first:
			PRINT = self.RemoveSpacesAndTabs(line).lstrip(self.declaration['print']).lstrip(':')
			print(self.eval(PRINT))

	def getCommands(self):
		"""get all possible commands! (usefully for debugging!)"""
		return self.paths

	def RemoveSpacesAndTabs(self, text: str):
		"""Removes spaces and tabs from the start of the string"""
		return text.lstrip().lstrip('\t').lstrip().lstrip('\t')


class Web:

	def __init__(self, connect_to_server: bool = False, code: Code = Code("")):
		"""Flask object to run code, so you will just need to create code for assistant and save time."""
		if connect_to_server is False:
			self.app = Flask(__name__)
			self.code = code
		else:
			pass

	def run_tutorial(self, host, port, debug: bool=False):
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

	def run(self, host, port, debug: bool=False, HTML_PAGE="Executer.html", ssl_certificate=None):
		code = str(self.code.rawCode)
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
		PRE_COMMANDS = self.code.getCommands()
		COMMANDS = ""
		for command in PRE_COMMANDS:
			COMMANDS += command.replace(':', '<a>').replace(';', '</a>').replace('--', '<a2>').replace('-', '</a2>')

		@self.app.route('/', methods=['GET', 'POST'])
		def execute():
			return render_template(HTML_PAGE, output=whatWasPrinted, COMMANDS=COMMANDS)

		self.app.run(host=host, port=port, debug=debug, ssl_context=ssl_certificate)
