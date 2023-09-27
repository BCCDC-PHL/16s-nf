#!/usr/bin/env python3

import pandas as pd
import argparse
import json

def main(args):


    f = open('/data/ref_databases/blast/16S/silva/2020-08-24_138.1_SSURef_NR99_tax_silva_trunc/metadata.json')

    silva_meta = json.load(f)

    f2 = open('/data/ref_databases/blast/16S/ncbi/2023-09-19_1.1_16S_ribosomal_RNA/metadata.json')

    ncbi_meta = json.load(f2)

    result_table_nt = pd.read_csv("output/output_ncbi16s/combined_blast_species_genus_results.csv",index_col=None)
    result_table_silva = pd.read_csv("output/output_silva/combined_blast_species_genus_results.csv",index_col=None)
    result_table_rdp = pd.read_csv("output/output_rdp/combined_blast_species_genus_results.csv",index_col=None)

    result_table_nt['database'] = 'ncbi16s'
    result_table_silva['database'] = 'silva'
    result_table_rdp['database'] = 'rdp'

    result_table = pd.concat([result_table_nt, result_table_silva,result_table_rdp])

    result_table["species"] = result_table["species"].apply(lambda x: "" if x=="a" else x)
    result_table = result_table.sort_values(['query_seq_id','bitscore'],ascending=[True,False])


    result_table['percent_identity'] = result_table['percent_identity'].apply(lambda x: round(x,3))
    result_table['percent_coverage'] = result_table['percent_coverage'].apply(lambda x: round(x,3))


    #write out report in html
    result_table = result_table.drop_duplicates(subset=['query_seq_id','subject_accession','species','genus','percent_identity','percent_coverage','bitscore'], keep = 'first')
    result_table = result_table.fillna('')
    fil = result_table['species'].str.contains('uncultured')
    result_table = result_table[~fil]


    qseq = result_table['query_seq_id'].drop_duplicates()


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
    DBNOTE=f"<p>Silva database db name: { silva_meta['dbname'] }, db version: { silva_meta['version']}, date: { silva_meta['date'] };\n ncbi 16s database db name: { ncbi_meta['dbname'] }, db version:{ ncbi_meta['version'] }, date:{ ncbi_meta['date'] };\n rdp database downloaded : Jan 20 2023</p>"
    
    TABLE = '''
            <h3 class = "first">{}</h3>
            <table>
                <tbody>
                    <tr class="header">
                        <th>subject_accession</th>
                        <th>species</th>
                        <th>genus</th>
                        <th>query_length</th>
                        <th>alignment_length</th>
                        <th>num_mismatches</th>
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
                        <td id="{}_show" align="center" colspan="6">Displaying 20/300 matches. <a href="#{}_extra" onclick="toggle('{}_extra'); toggle('{}_show'); toggle('{}_hide');">Show the remaining results.</a></td>
                        <td id="{}_hide" align="center" colspan="6" style="display:none"><a href="#{}" onclick="toggle('{}_extra'); toggle('{}_show'); toggle('{}_hide');">Hide the last 280 results.</a></td>
                    </tr>
                </tbody>
            </table>

    '''

    FOOT = '''
        </body>
    </html>
    '''

    ROW = ' ' * 20 + "<tr><td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%.3f</td><td>%.3f</td><td>%s</td></tr>"

    Func = open("output/report.html","w")
    Func.write(HEAD)
    Func.write(DBNOTE)

    for q in qseq:
        ptable = result_table[result_table['query_seq_id'] == q]
        
        print(q)
        
        row_list = []
        if len(ptable) < 20:
            for i in range(1,len(ptable)):
            
                instr = ROW % (ptable.iloc[i,2], ptable.iloc[i,19], ptable.iloc[i,20],ptable.iloc[i,4],ptable.iloc[i,10],ptable.iloc[i,13], ptable.iloc[i,16], round(ptable.iloc[i,12],3), round(ptable.iloc[i,11],3),ptable.iloc[i,21])
                row_list.append(instr)
            strTable = TABLE.format(q,'\n'.join(row_list),q,q,q,q,q,q,q,q,q,q,q,q,q)
            Func.write(strTable)
        else:

            for i in range(1,20):
                #print(ptable.iloc[i,12],3)
                instr = ROW % (ptable.iloc[i,2], ptable.iloc[i,19], ptable.iloc[i,20],ptable.iloc[i,4],ptable.iloc[i,10],ptable.iloc[i,13], ptable.iloc[i,16], round(ptable.iloc[i,12],3), round(ptable.iloc[i,11],3),ptable.iloc[i,21])
                row_list.append(instr)

            hiden_row_list = []
            for i in range(21,min(len(ptable),300)):
                instr = ROW % (ptable.iloc[i,2], ptable.iloc[i,19], ptable.iloc[i,20],ptable.iloc[i,4],ptable.iloc[i,10],ptable.iloc[i,13], ptable.iloc[i,16], round(ptable.iloc[i,12],3), round(ptable.iloc[i,11],3),ptable.iloc[i,21])
                hiden_row_list.append(instr)
            strTable = TABLE.format(q,'\n'.join(row_list),q,'\n'.join(hiden_row_list),q,q,q,q,q,q,q,q,q,q,q)
            Func.write(strTable)

    Func.write(FOOT)
    Func.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--silvadbmeta')
    parser.add_argument('-n', '--ncbidbmeta')
    args = parser.parse_args()
    main(args)
