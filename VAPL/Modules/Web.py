
def redirect(url):
	print('<style onload=\"window.open(\'%s\', \'_blank\');\"\\>' % url)
	return


def html(text):
	print(text)
	return


def tts(text):
	print(f'<style onload=\'speak({text})\'')