
def redirect(url):
	print('<style onload=\"window.open(\'%s\', \'_blank\');\"\\>' % url)
	return


def html(text):
	print(text)
	return


def run_javascript(JS):
	print(f'<style onload=\"{JS}\"\\>')
	return


def tts(text):
	return