from flask import Flask, render_template, request, make_response
from io import StringIO
from re import sub, escape

class Code:

	def __init__(self, SCRIPT_OR_PATH, IS_PATH: bool or int = False):
		if IS_PATH is True or IS_PATH == 1:
			file = open(SCRIPT_OR_PATH, 'r')
			self.code = file.read()
			file.close()
		else:
			self.code = SCRIPT_OR_PATH

	def setup_new_code(self, SCRIPT_OR_PATH, IS_PATH: bool or int = False):
		if IS_PATH is True or IS_PATH == 1:
			file = open(SCRIPT_OR_PATH, 'r')
			self.code = file.read()
			file.close()
		else:
			self.code = SCRIPT_OR_PATH

	def run(self):
		pass

	def compile_to_python(self):
		pass


class Web:

	def __init__(self, connect_to_server: bool = False, code: Code or None=None):
		if not connect_to_server:
			self.app = Flask(__name__)
		else:
			if code is not None:
				self.code = code
				self.run_tutorial = None
				self.run = None


	def run_tutorial(self, host, port, debug: bool=False):
		@self.app.route('/docs', methods='GET')
		def DOCUMENTATION():
			return render_template('docs.html')

		@self.app.route('/', methods=['GET'])
		def index():
			return render_template('index.html')

		self.app.run(host=host, port=port, debug=debug)

	def run(self, host, port, debug: bool=False):
		self.app.run(host=host, port=port, debug=debug)
