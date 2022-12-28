
def redirect(url):
	print('<style onload=\"window.open(\'%s\', \'_blank\');\"\\> </style>' % url)
	return


def html(text):
	print(text)
	return


def tts(text):
	print(f'<style onload=\'say(\"{text}\")\'></style>')
	print(text)
