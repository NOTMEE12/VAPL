function delay(MS) { return new Promise(resolve => { setTimeout(() => { resolve('') }, MS);})}

async function DangerousShowText(id, text, delayMS=700){
	TARGET = document.getElementById(id)
	// shows text! can execute malicious code!
	let AlreadyDone = ""
	let tag = ''
	for (const letter of Array(text)) {
		if (letter != '<'){
			AlreadyDone += letter
			TARGET.innerHTML = AlreadyDone
			delay(delayMS)
		} else if (letter == '>') {
			AlreadyDone += tag
			TARGET.innerHTML = AlreadyDone
		} else {
			tag += letter
		}
	}
	TARGET.innerHTML = AlreadyDone
}