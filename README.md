# _**VAPL**_ - Voice Assistant programming language

### STYLE
- VARIABLE - ```var NAME = VALUE or EXPRESSION, STATEMENT```
- FUNCTION - ```define NAME(PAR1, PAR2){ CODE  }```
- print - ```out: EXPRESSION or VALUE```
- one-line comment start - ```%: TEXT```
- multiple-lines comments - ```%= TEXT ... some lines ... this function... =%```
- builtIn modules that can be accessed using ```#[NAME] > Import something > As something```
- for loop - ```for ( var VARIABLE; ITERATOR ) { CODE }```
- while loop - ```while ( STATEMENT ) { CODE }```
- if-then-else - ```if(STATEMENT) (optional - then )  { CODE }```
- PATHS
- running functions and some other actions - ```call: x+=1; test(x)```
- uses python evaluation - example ```if(x==5 or x == -5) then {out: "x is equal to 5 or -5"}```
### ABOUT PATHS
- starts with /* and ends with */
- are basically list of instructions
- when path is activated it will run code after ;> **ONLY ONE-LINE**
- uses strings (WHEN TEXT IS IN BETWEEN '(' AND ')' IT CAN BE USED AS VARIABLE IN CODE)
- example:
```
var HELLO = "hello (NAME)"
/*
HELLO	;> out: "hello " + NAME + "!"
*/
```
### Builtin modules:
- Web:
	+ redirect ( url ) - redirects to a website
	+ html ( HTML ) - runs html code 
	+ tts ( text ) - TextToSpeech

## HOW TO INSTALL
```commandline
pip install VAPL
```

## CODE EXAMPLE
### main.py
```python
import VAPL

Code = VAPL.Code('code.vapl', True)
web = VAPL.Web(False)
web.run('127.0.0.1', 81)
```
### code.vapl
```shell
%: BuiltIn Module
#[VAPL.Modules.Web] > redirect, tts
%: WHEN USING Speech To text it will ignore the name and $ignore
%: But name will be displayed as title
$name = 'bob'
$ignore = ['']
out: f'Hello, I am {$name} Vapl.'
out: 'I am the voice assistant made in custom language.'
out: 'You can make me too!'
out: 'Search for VAPL in testpypi or pypi!'
out: ''
define spotify(){
	call: tts('opening spotify')
	call: redirect('https://open.spotify.com/collection/tracks')
}

/*
'hi' ;> call: tts(f'hi')
'goodbye'  ;> call: tts('goodbye')
f'initialize {$name}' ;> call: tts(f'initializing {$name}')
'open spotify' ;> call: spotify()
*/
```
