# VAPL
VAPL - programming language to easily make voice assistants in python!
----------------------------------------------------------------------
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

```python
import VAPL

web = VAPL.Web(False)
web.run_tutorial('0.0.0.0', 81)
```
