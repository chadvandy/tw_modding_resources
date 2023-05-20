import sys
from collections import defaultdict
from pathlib import Path
from typing import cast

import bs4



if len(sys.argv) < 2:
    print('Not enough arguments: HTML File path expected (UI callbacks documentation)')
    exit(1)

if len(sys.argv) > 2:
    print(f'too much arguments ({len(sys.argv)}). Only one expected: UI callbacks documentation HTML file')
    exit(1)

doc_path = Path(sys.argv[1])


if doc_path.suffix != '.html':
    print('Invalid file path (HTML file expected)')
    exit(1)

if not doc_path.exists():
    print('File not found')
    exit(1)



DOC_NAME = 'UI Callback Documentation'

HTML_FILE_NAME = doc_path.with_stem(DOC_NAME.lower().replace(' ', '_')).name

OUT_HTML_PATH = Path(HTML_FILE_NAME)
OUT_CSS_PATH  = OUT_HTML_PATH.with_suffix('.css')

CSS_FILE_NAME = OUT_CSS_PATH.name




with open(doc_path) as fp:
    parsed_file = bs4.BeautifulSoup(fp, 'html.parser', preserve_whitespace_tags=set(('td', 'th', 'h3')))





root = parsed_file.find('table')
assert isinstance(root, bs4.Tag), 'Failed to find root table'




doc_entry_template = """
<a id="{callback}">
    <h3>{callback}</h3>
    {doc}
</a>
"""

index_entry_template = """
<div class="small_link">
    <a href="#{callback}">{callback}</a>
</div>
"""

area_index_template = """
<details>
    <summary>{area}</summary>
    {index}
</details>
"""



doc_entries = {}
callbacks_grouped_by_area = defaultdict(list)


for i, row in enumerate(root.find_all('tr', recursive=False), start=1):
    row = cast(bs4.Tag, row)

    assert isinstance(row.th, bs4.Tag),                                                     f'<tr> #{i} | type(row.th)="{type(row.th)}" (!="bs4.Tag")\n\n{row.th}'
    assert isinstance(row.td, bs4.Tag),                                                     f'<tr> #{i} | type(row.td)="{type(row.td)}" (!="bs4.Tag")\n\n{row.td}'
    assert isinstance(row.td.table, bs4.Tag),                                               f'<tr> #{i} | type(row.td.table)="{type(row.td.table)}" (!="bs4.Tag")\n\n{row.td.table}'

    callback_name = row.th.get_text()
    info_table    = row.td.table
    area          = info_table.find('th', string='area').find_next_sibling('td').get_text()

    _callback_name_from_table = row.find('th', string='name').find_next_sibling('td').get_text()

    assert area and callback_name,                                                          f'<tr> #{i} | Required field[s] not found:\narea="{area}"\ncallback_name="{callback_name}"'
    assert callback_name == _callback_name_from_table,                                      f'<tr> #{i} | Callback name from row header and from table doesnt match:\nfrom th: "{callback_name}"\nfrom table: "{_callback_name_from_table}"'
    assert callback_name not in doc_entries,                                                f'<tr> #{i} | Duplicated callback documentation entry: "{callback_name}"'

    callbacks_grouped_by_area[area].append(callback_name)
    doc_entries[callback_name] = doc_entry_template.format(callback=callback_name, doc=info_table.prettify(formatter='html5'))


areas_ordered = sorted(callbacks_grouped_by_area.keys())
callbacks_ordered = sorted(doc_entries.keys())


docs = '\n<hr>\n'.join(doc_entries[callback] for callback in callbacks_ordered)
alphabet_index = '\n'.join(index_entry_template.format(callback=callback) for callback in callbacks_ordered)


area_indexes = {}
for area in areas_ordered:
    area_alphabet_index = '\n'.join(
        index_entry_template.format(callback=callback)
        for callback in sorted(callbacks_grouped_by_area[area])
    )
    area_indexes[area] = area_index_template.format(area=area, index=area_alphabet_index)

area_indexes_combined = '\n'.join(area_indexes.values())



css = """
@import url(https://fonts.googleapis.com/css?family=Alef);

body
{
  font-family: Alef;
  height:100%
}

/* headers */
h1 
{
  color: black;
  text-align: left;
  font-weight: bold;
}

h2 
{
  color: black;
  text-align: left;
}

h3 
{
  margin-top: 2em;
  color: #636363;
  text-align: left;
}

h4 
{
  color: black;
  text-align: left;
}


/* table stuff */
table 
{ 
  border-collapse: collapse; 
} 

td, th
{ 
  border: 1px solid #b4b4b4; 
  text-align: left; 
  padding: 8px; 
} 

td:nth-child(1)
{
  font-weight: bold;
}

tr:nth-child(even) 
{ 
  background-color: #e7e7e7; 
}

hr
{
  width:50%; 
  text-align:left;
  margin-left:0.5em;
  margin-top: 2.5em;
}


#main 
{
  height: 100%;
  position: relative;
  margin-left: 370px;
  z-index: 0;
  overflow-x: scroll;
}


/*
=============================================================================================
                                            sidebar
============================================================================================= 
*/


#sidebar {
  height: 100%;
  width: 360px;
  position: fixed;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  padding-right: 1px;
  top: 0;
  left: 0;
  background: #d4d4d4;
  box-shadow: 0 0 2px 0px #c9c9c9;
}

#title {
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3;
  background: #fff;
  box-shadow: 0 0 1px 0 black;
}

#title > h2 {
    margin: 0;
}


#index-holder {
  height: 100%;
  display: flex;
  padding-top: 1px;
}



/*
=============================================================================================
                                     sidebar: index-tabs
============================================================================================= 
*/


#index-tabs {
  width: 40px;
  display: flex;
  flex-direction: column;
}

#index-tabs > button {
  height: 150px;
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  margin-bottom: 1px;
  border: 0;
  background: #dcdcdc;
  box-shadow: 0 0 1px 0 #000000;
  font-weight: bold;
  letter-spacing: 2px;
}

#index-tabs > button[active] {
  background-color: white;
}


#index-tabs > button:not([active]):hover {
  background-color: #ebeaea;;
}


#index-tabs > button > span {
  display: inline-block;
  transform: rotate(-90deg);
}


/*
=============================================================================================
                                       sidebar: index
============================================================================================= 
*/


#index-wrapper
{
  height: 100%;
  width: 100%;
  position: relative;
  margin-left: 1px;
  overflow-x: hidden;
  overflow-y: scroll;
  background: white;
}


.index {
  height: max-content;
  display: none;
  position: absolute;
  padding-top: 8px;
  overflow-y: visible;
 }

.index[active] {
  display: block;
}


/* mouse over link */
.index a:hover {
  background-color: #e7e7e7;
  color: #000000;
}


/* links */
.index a
{
  padding: 6px 8px 6px 16px;
  text-decoration: none;
  font-size: 1.2em;
  color: #2c2c2c;
  display: block;
  border: none;
  background: none;
  width:100%;
  text-align: left;
  cursor: pointer;
  outline: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  position: relative;
  width: 280px;
  height: max-content;
  font-size: 12px;
}


.index a:hover
{
text-overflow: clip;
    white-space: normal;
    word-break: keep-all;
}


.small_link
{
  height: 30px;
  overflow: hidden;
}

.index a:hover + .tooltip 
{
  visibility: hidden;
  transition: opacity 0.5s ease;
  opacity: 1;
}

.tooltip 
{
  width: max-content;
  visibility: hidden;
  background-color: rgb(223, 219, 219);
  padding: 5px;
  box-shadow: 0 0 50px 0 rgba(0,0,0,0.3);
  opacity: 0;
  transition: opacity 0.5s ease;
  font-size: 12px;

  position: absolute;
  left: 200px;
  z-index: 99;
}


/*
=============================================================================================
                                            other
============================================================================================= 
*/



/* scroll bars */
/* Firefox scrollbar */
*{
  scrollbar-width: thin;
  scrollbar-color: rgb(255, 255, 255) rgb(197, 197, 197);
  z-index: 0;
 }
  
/* Chrome/Edge/Safari scroll bar */
*::-webkit-scrollbar 
{
  width: 12px;
  z-index: 0;
}

*::-webkit-scrollbar-track 
{
  z-index: 0;
}

*::-webkit-scrollbar-thumb 
{
  background-color: rgb(197, 197, 197);
  border-radius: 20px;
  z-index: 0;
}

details > summary {
  list-style: none;
}

details > summary::-webkit-details-marker {
  display: none;
}

summary {
  height: 30px;
  overflow: hidden;
  margin: 5px 0px -5px 15px;
  font-weight: 500;
}

summary:after {
    content: "+"
}

details[open] summary:after {
  content: "-";
}
"""

# tabs at the beginning of the lines are added to make the result look better in the final html file
script = """
const tabs = document.querySelectorAll('#index-tabs > button')

        function changeActiveIndex(event) {
            if (!event) {
                event = window.event;   // Older versions of IE use 
                                        // a global reference 
                                        // and not an argument.
            };

            var tab = (event.target || event.srcElement);   // DOM uses 'target';
                                                            // older versions of 
                                                            // IE use 'srcElement'
            
            if (tab.nodeName.toLowerCase() === 'span') {
                tab = tab.parentNode
            }

            if (tab.nodeName.toLowerCase() === 'button' && tab.parentNode.id == 'index-tabs' && !tab.hasAttribute('active')) {
                var current_active_tab = document.querySelectorAll('#index-tabs > button[active]')[0];
                if (current_active_tab != null) {
                    current_active_tab.removeAttribute('active')
                    var active_index = document.getElementById(current_active_tab.name)
                    active_index.removeAttribute('active')
                }
                
                tab.setAttribute('active', '');
                document.getElementById(tab.name).setAttribute('active', '');
            }    
        }

        tabs.forEach(
            function (btn) {
                btn.addEventListener('click', changeActiveIndex)
            }
        )
"""




html = f"""
<!-- 
    *** GENERATED BY SCRIPT ***
    Source: "documentation/ui/callback_documentation.html"

    Use this tool to generate a new version if the source has changed:
        "tools/convert_ui_callback_doc/convert.py"
 -->
<!DOCTYPE html>
<html>
    <head>
        <title>TW Docs: {DOC_NAME}</title>
        <link rel="stylesheet" href="{CSS_FILE_NAME}">
    </head>
    <body>
        <div id="sidebar">
            <div id="title">
                <h2>{DOC_NAME}</h2>
            </div>
            <div id="index-holder">
                <div id="index-tabs">
                    <button active type="button" name="alphabet_index">
                        <span> Index </span>
                    </button>
                    <button type="button" name="areas_index">
                        <span> Areas </span>
                    </button>
                </div>
                <div id="index-wrapper">
                    <div active id="alphabet_index" class="index">
                        {alphabet_index}
                    </div>
                    <div id="areas_index" class="index">
                        {area_indexes_combined}
                    </div>
                </div>
            </div>
        </div>
        <div id="main">
            {docs}
        </div>
    </body>
    <script>
        {script}
    </script>
</html>
"""





html = bs4.BeautifulSoup(html, 'html.parser', preserve_whitespace_tags=set(('td', 'th', 'h3', 'h2'))).prettify(formatter=bs4.formatter.HTMLFormatter(indent=4))


OUT_HTML_PATH.write_text(html)
OUT_CSS_PATH.write_text(css)


print(f'Modified version stored here: "{OUT_HTML_PATH}" (assets: "{OUT_CSS_PATH}")')
