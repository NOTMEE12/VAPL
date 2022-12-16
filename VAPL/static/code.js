/* SEND CODE AND GET CMD */
function send() {
	var script = document.getElementById("code").value
	console.log(script)
  document.getElementById("Console").value = ""
	$.ajax({
	  type: 'POST',
		url: '/code',
		data: {'code': script},
		success: function(data) {
      console.log(data)
			document.getElementById("Console").value = data
      let STATUS = false
      data = data.split("\n")
      data.forEach(function(line){
        console.log(line)
        if(line.startsWith("Err")){
          STATUS = true
          console.log("FOUND")
        }
      })

      if(STATUS) {
        $('#CodeTest').removeClass('NO-ERROR')
        $('#CodeTest').addClass('ERROR')
      } else {
        $('#CodeTest').removeClass('ERROR')
        $('#CodeTest').addClass('NO-ERROR')
      }
		}, error: (error) => {
      console.warn("Fatal error appeared!")
      document.getElementById("Console").value = "Fatal error appeared!"
    }
	})

}

/* SET TEXTAREA ON LOAD aka. on call xD */
function onload() {
  document.getElementById('code').value = '%: Możesz podmieniać kod ;)  \nvar przywitanie = "Witaj"  \nout: przywitanie + " ktośiu" + "!"  \nif(przywitanie == "Witaj") then {  \n\tout: "Już się przywitałem, teraz twoja kolej!"\n}'
}


var observe;
if (window.attachEvent) {
    observe = function (element, event, handler) {
        element.attachEvent('on'+event, handler);
    };
}
else {
    observe = function (element, event, handler) {
        element.addEventListener(event, handler, false);
    };
}

function init () {
  var text = document.getElementById('code');
  function resize () {
    text.style.height = 'auto';
    text.style.height = text.scrollHeight+'px';
  }
  /* 0-timeout to get the already changed text */
  function delayedResize () {
    window.setTimeout(resize, 0);
  }
  observe(text, 'change',  resize);
  observe(text, 'cut',     delayedResize);
  observe(text, 'paste',   delayedResize);
  observe(text, 'drop',    delayedResize);
  observe(text, 'keydown', delayedResize);

  // SET LINE COUNTER
  code = document.getElementById('code')

  function update_lines() {
    let line_number = code.value.split("\n").length
    console.log(line_number)
    document.getElementById('Console-liner').value = Array(line_number).fill('<span></span>').join('')
  }
  observe(code, 'change', update_lines)
  observe(code, 'cut', update_lines)
  observe(code, 'paste', update_lines)
  observe(code, 'drop', update_lines)
  observe(code, 'keydown', update_lines)
  observe(code, 'keyup', update_lines)

  text.focus();
  text.select();
  resize();
}


/* AUTOMATIC WORD COLORS */

var keywords_orange = ["var", "if", "else", "out", "define", "ret", "$", "call"]
var keywords_purple = ["$", ".", "/*", "*/"]
var keywords_grey   = ["%=", '=%']
var keywords_green  = ['>', ';>', '>#', '/>']

function start(){
  document.querySelector('#code').addEventListener("keydown", e => {
      // SPACE pressed
      if (e.keyCode == 32){
        var newHTML = ""
        // Loop through words
        $(this).text().replace(/[\s]+/g, " ").trim().split(" ").forEach(function(val){
          // If word is statement
          if (keywords_orange.indexOf(val.trim()) > -1)
            newHTML += "<span class='ORANGE'>" + val + "&nbsp;</span>"
          else if(keywords_purple.indexIf(val.trim()) > -1)
            newHTML += "<span class='PURPLE'>" + val + "&nbsp;</span>"
          else
            newHTML += val
        })
        console.log(newHTML)
        $(this).html(newHTML)

        // Set cursor postion to end of text
        var child = $(this).children()
        var range = document.createRange()
        var sel = window.getSelection()
        range.setStart(child[child.length-1], 1)
        range.collapse(true)
        sel.removeAllRanges()
        sel.addRange(range)
        this.focus()
    }
  })
}
