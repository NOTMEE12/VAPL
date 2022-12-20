function delay(MS) { return new Promise(resolve => { setTimeout(() => { resolve('') }, MS);})}

async function DangerousShowText(id, text, delayMS){
	TARGET = document.getElementById(id)
	// shows text! can execute malicious code!
	/*
	let AlreadyDone = ""
	for (const letter of Array(text)) {
		AlreadyDone += letter
		TARGET.innerHTML = AlreadyDone
		await delay(delayMS)
	}
	TARGET.innerHTML = text
	*/
	TARGET.innerHTML = text
}