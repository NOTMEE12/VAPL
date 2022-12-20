

def redirect(url):
	print(
	f'''
	<script> 
	window.open('{url}', '_blank')
	</script>
	''')
	#print(f'<a href=\'{url}\'> test </a>')
	return
