

def redirect(url):
	print('<style onload=\"window.open(\'%s\', \'_blank\');\"\\>' % url)
	return

def runJS(JS):
	print(f'<style onload=\"{JS}\"\\>')