HEAD = '''
<!DOCTYPE html>
<html>
	<head>   
		<style>
				body {
					font-size:1em;
				}
				table, tr {
					width: 100%;
				}
				table {
					border-collapse: collapse;
					border: 1px solid black;
				}
				tr.header {
					background-color: lightgrey;
				}
				th {
					border: 1px solid black;
				}
				td {
					border-left: 1px solid black;
					border-right: 1px solid black;
					border-bottom: 1px dashed grey;
				}
				td.descr {
					font-size: 80%;
				}
				h3 {
					page-break-before: always;
					color: blue;
				}
				h3.first {
					page-break-before: avoid;
				}
				span.super {
					color: navy;
					font-size: 75%%;
					vertical-align: top;
				}          
		</style>
		<script>
				function toggle(id){
				var element = document.getElementById(id)
				console.log(id)
				if (element.style.display == 'none') {
					//console.log(element.tagName);
					if (element.tagName == 'TBODY') element.style.display = 'table-row-group';
					else if (element.tagName == 'TD') element.style.display = 'table-cell';
					else element.style.display = 'block';
				} else {
					element.style.display = 'none';
				}
			}
		
		</script>
	</head>
	<body>
'''


DBNOTE="<p>NCBI Database name: {}, version: {}, date: {};\n Integrated Database name: {}, version:{}, date:{};\n EzBio Database name: {}, version: {}, date: {}</p>"

def build_table(name, col_names, table_rows, hidden_rows=None):
	hidden_rows = '' if not hidden_rows else hidden_rows
	table_header = '</th>\n<th>'.join(col_names)
	return f'''
			<h3 class = "first">{name}</h3>
			<table>
				<tbody>
					<tr class="header">
						<th>{table_header}</th>
					</tr>             
	{table_rows}

				</tbody>
				<tbody id="{name}_extra" style="display:none">
	{hidden_rows}
				</tbody>
				<tbody>
					<tr>
						<td id="{name}_show" align="center" colspan="6">Displaying 20/300 matches. <a href="#{name}_extra" onclick="toggle('{name}_extra'); toggle('{name}_show'); toggle('{name}_hide');">Show the remaining results.</a></td>
						<td id="{name}_hide" align="center" colspan="6" style="display:none"><a href="#{name}" onclick="toggle('{name}_extra'); toggle('{name}_show'); toggle('{name}_hide');">Hide the last 280 results.</a></td>
					</tr>
				</tbody>
			</table>

	'''
def build_row(series, row_names):
	# original: 	ROW = ' ' * 20 + "<tr><td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%.3f</td><td>%.3f</td><td>%s</td></tr>"
	row_string = "</td><td>".join(series[row_names].astype(str))
	return  ' ' * 20 + '<tr><td>' + row_string + '</td></tr>'


FOOT = '''
	</body>
</html>
'''
