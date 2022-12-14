# CBPL
### CBPL - programming language to easily make voice assistants in python using custom language made in it!

### UNIQUE STYLE
- VARIABLE - "var"
- FUNCTION - "define"
- print - "out"
- one-line comment start - "%:"
- multiple-lines comment start - "%="
- multiple-lines comment end - "=%"
- PATHS
### ABOUT PATHS
- starts with /* and ends with */
- Paths are just basically list of instructions
- when path is activated it will run code after ;>
```
var HELLO = "hello :NAME:"
/*
1.HELLO	;> out: "hello " + NAME + "!"
*/
```
## HOW TO INSTALL
```commandline
pip install CBPL
```

## CODE EXAMPLE
```python
import CBPL.src as CBPL
web = CBPL.Web(False)
web.run_tutorial('0.0.0.0', 81)
```
