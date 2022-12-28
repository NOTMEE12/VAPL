
def redirect(url):
	print('<style onload=\"window.open(\'%s\', \'_blank\');\"\\>' % url)
	return


def html(text):
	print(text)
	return


def run_JS(JS):
	"""PLEASE DON't USE '\n' IN LINES!"""
	for line in JS.split('\n'):
		print(f'<style onload=\"{JS}\"\\>')
	return


def tts(text):
	run_JS()