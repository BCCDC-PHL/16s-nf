#!/usr/bin/env python3

import pandas as pd

#cols = 'qseqid sseqid pident qlen slen mismatch gapopen qstart qend sstart send bitscore'.split(' ')
result_table_nt = pd.read_csv("output_nt/combined_blast_species_genus_results.csv",index_col=None)
result_table_silva = pd.read_csv("output_silva/combined_blast_species_genus_results.csv",index_col=None)
result_table_gg = pd.read_csv("output_gg/combined_blast_species_genus_results.csv",index_col=None)
result_table_rdp = pd.read_csv("output_rdp/combined_blast_species_genus_results.csv",index_col=None)

result_table_nt['database'] = 'nt'
result_table_silva['database'] = 'silva'
result_table_gg['database'] = 'greengenes'
result_table_rdp['database'] = 'rdp'

#result_table_nt['database'] = result_table_nt['query_seq_id'].apply(lambda x: starts)

result_table = pd.concat([result_table_nt, result_table_silva,result_table_gg,result_table_rdp])

result_table["species"] = result_table["species"].apply(lambda x: "" if x=="a" else x)
#result_table.apply(lambda x: '16s NR' if x["query_seq_id"].startswith('NR_') else x["database"])
result_table = result_table.sort_values(['query_seq_id', 'bitscore'],ascending=False)

result_table['percent_identity'] = result_table['percent_identity'].apply(lambda x: round(x))
result_table['percent_coverage'] = result_table['percent_coverage'].apply(lambda x: round(x))
#with open('result.txt') as f:
#    lines = f.readlines()

#id =  [x.split(' ')[0].replace('>','') for x in lines]

#des = [' '.join(x.split(' ')[1::]) for x in lines]

#res = dict(zip(id, des))

#blast_results['sseqid'] = blast_results['sseqid'].apply(lambda x: x.split('|')[-2])
#blast_results['description'] = blast_results['sseqid'].apply(lambda x: res[x])
#blast_results['coverage'] = blast_results['qlen'] * 100 / blast_results['slen']

#best_bitscores = blast_results[['qseqid','sseqid', 'bitscore']].groupby(['qseqid','sseqid']).max().reset_index()
#blast_results = pd.merge(blast_results, best_bitscores, on=['qseqid','sseqid', 'bitscore'])

#result_table = blast_results[["qseqid","sseqid","description","bitscore","coverage","pident"]].drop_duplicates()

#write out report in html
result_table = result_table.drop_duplicates(subset=['query_seq_id','subject_accession','species','genus','percent_identity','percent_coverage','bitscore'], keep = 'first')
result_table = result_table[~(((result_table['species'] == 'uncultured bacterium') | (result_table['species'] == 'uncultured organism') | (result_table['species'] == 'uncultured microorganism ')) & (result_table['genus'] == 'environmental samples'))]
result_table = result_table.fillna('')

qseq = result_table['query_seq_id'].drop_duplicates()

#qseq.to_csv("report_table.csv")

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

TABLE = '''
        <h3 class = "first">{}</h3>
        <table>
            <tbody>
                <tr class="header">
                    <th>subject_accession</th>
                    <th>species</th>
                    <th>genus</th>
                    <th>bitscore</th>
                    <th>percent_coverage</th>
                    <th>percent_identity</th>
                    <th>database</th>
                </tr>             
{}

            </tbody>
            <tbody id="{}_extra" style="display:none">
{}
            </tbody>
            <tbody>
                <tr>
                    <td id="{}_show" align="center" colspan="6">Displaying 20/500 matches. <a href="#{}_extra" onclick="toggle('{}_extra'); toggle('{}_show'); toggle('{}_hide');">Show the remaining results.</a></td>
                    <td id="{}_hide" align="center" colspan="6" style="display:none"><a href="#{}" onclick="toggle('{}_extra'); toggle('{}_show'); toggle('{}_hide');">Hide the last 480 results.</a></td>
                </tr>
            </tbody>
        </table>

'''

FOOT = '''
    </body>
</html>
'''

ROW = ' ' * 20 + "<tr><td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%s</td></tr>"

Func = open("report.html","w")
Func.write(HEAD)

for q in qseq:
    ptable = result_table[result_table['query_seq_id'] == q]
    
    print(q)
    row_list = []
    if len(ptable) < 20:
        for i in range(1,len(ptable)):
            instr = ROW % (ptable.iloc[i,2], ptable.iloc[i,19], ptable.iloc[i,20], ptable.iloc[i,16], round(ptable.iloc[i,12]), round(ptable.iloc[i,11]),ptable.iloc[i,21])
            row_list.append(instr)
        strTable = TABLE.format(q,'\n'.join(row_list),q,q,q,q,q,q,q,q,q,q,q,q)
    else:

        for i in range(1,20):
            instr = ROW % ( ptable.iloc[i,2], ptable.iloc[i,19], ptable.iloc[i,20], ptable.iloc[i,16], round(ptable.iloc[i,12]), round(ptable.iloc[i,11]),ptable.iloc[i,21])
            row_list.append(instr)
        hiden_row_list = []
        for i in range(21,min(len(ptable),500)):
            instr = ROW % ( ptable.iloc[i,2], ptable.iloc[i,19], ptable.iloc[i,20], ptable.iloc[i,16], round(ptable.iloc[i,12]), round(ptable.iloc[i,11]),ptable.iloc[i,21])
            hiden_row_list.append(instr)
        strTable = TABLE.format(q,'\n'.join(row_list),q,'\n'.join(hiden_row_list),q,q,q,q,q,q,q,q,q,q)
        Func.write(strTable)

Func.write(FOOT)
Func.close()

