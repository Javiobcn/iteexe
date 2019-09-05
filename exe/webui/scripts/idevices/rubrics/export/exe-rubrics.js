/**
 * Rubrics iDevice
 *
 * Released under Attribution-ShareAlike 4.0 International License.
 * Author: Ignacio Gros (http://gros.es/) for http://exelearning.net/
 *
 * License: http://creativecommons.org/licenses/by-sa/4.0/
 */

// To do:
// i18n: Actividad, Nombre, Fecha, Nota, Reset, Print, Observaciones

var $rubricIdevice = {
	
	// Default strings
	ci18n : {
		"activity" : "Activity",
		"name" : "Name",
		"date" : "Date",
		"score" : "Score",
		"notes" : "Notes",
		"reset" : "Reset",
		"print" : "Print"
	},
    
	init : function(){
        
		$(".RubricIdevice .iDevice_content").each(function(){
			
			var table = $("table",this);
			if (table.length!=1) return;
			
			var ul = $("ul",this);
			if (ul.length==1) {
				// Update $rubricIdevice.ci18n to use the custom strings
				$("li",ul).each(function(){
					if ($rubricIdevice.ci18n[this.className]) {
						$rubricIdevice.ci18n[this.className] = $(this).text();
					}
				});
			}
			
			$("caption",table).append('<a href="#" class="exe-rubric-print" id="print-'+this.id+'"><span>'+$exe_i18n.print+'</span></a>');
			
			$("#print-"+this.id).click(function(){
				$rubricIdevice.printRubric($("caption",table).text(),table.html())
				return false;
			});
			
		});
		
		// Print version
		if (!$("body").hasClass("exe-rubric")) return;
		
		// Add checkboxes
		$("tbody tr").each(function(i){
			$("td",this).each(function(z){
				var val = "";
				var span = $("span",this);
				if (span.length==1) {
					try {
						val = span.text().match(/\(([^)]+)\)/)[1];
					} catch(e){
						val = "";
					}
					if (val!="") {
						val = val.replace(/[^0-9.,]/g, "");
						val = val.replace(/,/g, ".");
						var isNumeric = true;
						if (isNaN(val)) isNumeric = false;
						if (!isNumeric) val = "";
					}
				}
				this.innerHTML += ' <input type="checkbox" name="criteria-'+i+'" id="criteria-'+i+'-'+z+'" value="'+val+'" />';
			});
			// Make those checkboxes work as radio inputs
			$("input",this).change(function(){
				if (this.checked){
					var name = this.name;
					$("input[name='"+this.name+"']").prop("checked",false);
					$(this).prop("checked",true);
				}
				$rubricIdevice.checkScore();
			});
		});
		
		// Clear form button
		$("#clear").click(function(){
			$("input[type='checkbox']").prop("checked",false);
			$("#score,#notes").val("");
			$("#name").val("").focus();
		});
		
		// Print button
		$("#print").click(function(){
			try {
				window.print();
			} catch(e) {
				
			}
		});
		
	},
	
	// Check the score (just add the numeric values of the checked inputs)
	checkScore : function(){
		var res = 0;
		$("tbody input:checked").each(function(){
			res += parseFloat(this.value);
		});
		res = Math.round( res * 10 ) / 10;
		$("#score").val(res);
	},
	
	printRubric : function(tit,html) {
		
		// Strings
		var i18n = this.ci18n;
				
		var a = window.open(tit);
			a.document.open("text/html");
			a.document.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">');
			a.document.write('<html xmlns="http://www.w3.org/1999/xhtml" class="exe-rubric">');
			a.document.write('<head>');
				a.document.write('<title>'+tit+'</title>');
				a.document.write('<link rel="shortcut icon" href="favicon.ico" type="image/x-icon" />');
				a.document.write('<link href="exe-rubrics.css" rel="stylesheet" type="text/css" />');
				a.document.write('<script type="text/javascript" src="exe_jquery.js"></script>');
				a.document.write('<script type="text/javascript" src="exe-rubrics.js"></script>');
			a.document.write('</head>');
			a.document.write('<body class="exe-rubric">');
				a.document.write('<div class="exe-rubric-wrapper">');
					a.document.write('<div class="exe-rubric-content">');
						a.document.write('<div id="exe-rubric-header">');
							a.document.write('<p>');
								a.document.write('<label for="activity">'+i18n.activity+':</label> <input type="text" id="activity" />');
								a.document.write('<label for="date">'+i18n.date+':</label> <input type="text" id="date" />');
							a.document.write('</p>');
							a.document.write('<p>');
								a.document.write('<label for="name">'+i18n.name+':</label> <input type="text" id="name" />');
								a.document.write('<label for="score">'+i18n.score+':</label> <input type="text" id="score" />');
							a.document.write('</p>');
						a.document.write('</div>');
						a.document.write('<table class="exe-table">'+html+'</table>');
						a.document.write('<div id="exe-rubric-footer">');
							a.document.write('<p>');
								a.document.write('<label for="notes">'+i18n.notes+':</label> <textarea id="notes" cols="32" rows="6"></textarea>');
							a.document.write('</p>');
						a.document.write('</div>');						
					a.document.write('</div>');
					a.document.write('<div id="commands"><input type="button" value="'+i18n.reset+'" id="clear" /> <input type="button" value="'+i18n.print+'" id="print" /></div>');
				a.document.write('</div>');
			a.document.write('</body>');
			a.document.write('</html>');
			a.document.close();

	}
    
}

$(function(){
	
	$rubricIdevice.init();
	
});