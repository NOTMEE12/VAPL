# _**VAPL**_ - Voice Assistant programming language

### STYLE
- VARIABLE - ```var NAME = VALUE or EXPRESSION, STATEMENT```
- FUNCTION - ```define NAME(PAR1, PAR2){ CODE  }```
- print - ```out: EXPRESSION or VALUE```
- one-line comment start - ```%: TEXT```
- multiple-lines comments - ```%= TEXT ... some lines ... this function... =%```
- builtIn modules that can be accessed using ```#[NAME] > Import something > As something```
- if-then-else - ```if(STATEMENT) (optional - then )  { CODE }```
- PATHS
- running functions and some other actions - ```call: x+=1; test(x)```
- uses python evaluation - example ```if(x==5 or x == -5) then {out: "x is equal to 5 or -5"}```
### ABOUT PATHS
- starts with /* and ends with */
- are basically list of instructions
- when path is activated it will run code after ;>
- uses strings (WHEN TEXT IS IN BETWEEN '(' AND ')' IT CAN BE USED AS VARIABLE IN CODE)
- example:
```
var HELLO = "hello (NAME)"
/*
HELLO	;> out: "hello " + NAME + "!"
*/
```
## HOW TO INSTALL
```commandline
pip install -i https://test.pypi.org/simple/ VAPL
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
%; WHEN USING Speech To text it will ignore the name and $ignore
%: But name will be displayed as title
$name = 'bob'
$ignore = ['hej']
out: f'Hello, I am {$name} Vapl.'
out: 'I am the voice assistant made in custom language.'
out: 'You can too!'
out: 'Search for VAPL in testpypi or pypi!'
out: ''
define spotify(){
	call: tts('Otwieram spotify')
	call: redirect('https://open.spotify.com/collection/tracks')
}

/*
'zdrastwujtie' ;> call: tts(f'zdrastwujtie')
'daswidania'  ;> call: tts(f'daswidania')
f'inicjalizuj {$name}' ;> call: tts(f'initializacja programu {$name}')
'otwórz spotify' ;> call: spotify()
*/
```
