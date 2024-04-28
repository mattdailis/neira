import json

import os
from bs4 import BeautifulSoup
from associationList import getNodes


def pairsToDot(graph, orders, links=None):
    nodes = getNodes(orders)
    dot = "digraph "+graphName(graph)+" {"
    for node in nodes:
        if links is not None and node in links:
            dot += nodeName(node) + ' [URL="'+links[node]+'.html"];'
        else:
            dot += nodeName(node) + ';'
            
    edges = []
    for edge in orders:
        margin = edge.margin
        marginStr = str(margin)
        if marginStr == 'None':
            marginStr = '_'
            margin = 1
        elif edge.adjusted_margin is not None:
            marginStr += " (" + str(edge.adjusted_margin) + ")"
        colorStr = ""
        if edge.red:
            colorStr = ', color="red"'
        edge = nodeName(edge.first) + " -> " + nodeName(edge.second) + '[label=\"' + marginStr + '\n' + edge.date.strftime("%m/%d") + '\", weight=\"' + str(100 - int(margin))+ '\"'+colorStr+', tooltip="'+reduceWhitespace(edge.tooltip.replace('"', ''))+'", URL="'+edge.url+'", random="random"]'
        edges.append(edge)
    dot += '; \n'.join(edges)
    dot += "}"
    return dot.encode('utf-8').decode()

def reduceWhitespace(string):
    string = string.replace("\r", "")
    while "  " in string:
        string = string.replace("  ", " ")
    while "\n\n" in string:
        string = string.replace("\n\n", "\n")
    return string

def graphName(name):
    return nodeName(name).lstrip('0123456789.- ')
    #return nodeName(name).lstrip('0123456789.- ')

def nodeName(name):
    return "".join(filter(str.isalnum, str(name).replace("_", "zzz"))).replace("zzz", "_")

def genJs(filename, name, dotString):
    target = open(filename, 'a')
    #target.truncate()
    target.write('var viz = new Viz();')
    target.write(f"""
    viz.renderSVGElement({json.dumps(dotString)})
    .then(function(element) {{
      document.body.appendChild(element);
    }})
    .catch(error => {{
      // Create a new Viz instance (@see Caveats page for more info)
      viz = new Viz();
    
      // Possibly display the error
      console.error(error);
    }});
    """)
    # '(' + json.dumps(dotString) + ', { format: "png-image-element" });')
    #target.write('var image = Viz(' + json.dumps(dotString) + ', { format: "png-image-element" });')
    target.write('\n')
    target.write('var label = document.createElement("b");\n')
    target.write('label.innerHTML = "'+ name +'";\n')
    # target.write('document.body.innerHTML += ("<br /><b>'+name+'<b><br />")\n')
    target.write('document.body.appendChild(label);\n')
    target.write('var linebreak = document.createElement("br");\n')
    target.write('document.body.appendChild(linebreak);\n')
    target.write('document.body.appendChild(image);\n')
    target.write('var linebreak = document.createElement("br");\n')
    target.write('document.body.appendChild(linebreak);\n')
    target.write('var linebreak = document.createElement("br");\n')
    target.write('document.body.appendChild(linebreak);\n')
    target.write('var linebreak = document.createElement("br");\n')
    target.write('document.body.appendChild(linebreak);\n')
    target.close()

def genDot(filename, dotString):
    target = open(filename, 'w+')
    target.write(dotString)
    target.close()

def genPdf(src, dst):
    print("src", src)
    print("dst", dst)
    #os.system("graphviz\\release\\bin\\dot.exe -Tpdf " + src + " -o " + dst)

def genHtml(name, graph):
    print("generating", name)
    #os.system("graphviz\\release\\bin\\dot.exe -Tcmapx -ohtml\\map\\"+name+".map -Tgif -ohtml\\gif\\"+name+".gif gv\\"+name+".gv")

    #os.system("dot -T gif -O ../bin/"+name+".dot")
    #os.system("dot -T svg -O ../bin/"+name+".dot")
    os.system('dot -Tcmapx -O ./dot/'+name+'.dot -Tgif -O ./dot/'+name+'.dot')


    # modal = open("html\\css\\modal.html", "r")
    # modalStr = modal.read()
    # modal.close()

    target = open("./dot/"+name+".html", 'w+')
    map = open("./dot/"+name+".dot.cmapx", "r")
    mapTag = map.read()
    map.close()
    mapTag = modMap(mapTag, name)
    target.write('<html><head>')
    target.write('<meta charset="utf-8">')
    target.write('<meta http-equiv="X-UA-Compatible" content="IE=edge">')
    target.write('<meta name="viewport" content="width=device-width, initial-scale=1">')
    target.write('<title>'+name+'</title>')
    # Bootstrap
    target.write('<link href="css/bootstrap.min.css" rel="stylesheet">')
    target.write('<link href="css/gui.css" rel="stylesheet">')
    target.write('</head>')
    target.write('<body>')
    target.write('<a href="../index.html">Back to index</a>')
    if name != graph:
        target.write('<br />')
        target.write('<a href="'+graph+'.html">Back to '+graph+'</a>')
    target.write('<IMG SRC="./'+ graphName(name) +'.dot.gif" USEMAP="#'+graphName(name)+'" />')
    # target.write('<IMG SRC="../../bin/'+ graphName(name) +'.dot.gif" />')
    if mapTag is not None:
        target.write(mapTag)
    # target.write(modalStr)
    target.write('<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.2.2/jquery.min.js"></script>')
    target.write('<script src="js/jquery.maphilight.js"></script>')
    target.write('<script src="js/bootstrap.min.js"></script>')
    target.write('</body></html>')
    target.close()

def modMap(map, name):
    soup = BeautifulSoup(map, features="html.parser")
    if not soup:
        return
    if not soup.map:
        return
    soup.map['id'] = name
    soup.map['name'] = name
    for area in soup.map.children:
        if area.name == 'area':
            pass
            #area['href'] = "#"
            #area['onclick'] = "alert('"+area['title'].replace('\n', '\\n')+"'); stopPropagation()"
    return soup.prettify().encode('utf-8').decode()

def viz(name, url, orders):
    # genJs("gui.js", name, pairsToDot(name, orders))
    links = {}
    nodes = getNodes(orders)
    for node in nodes:
        links[node] = nodeName(name)+nodeName(node)
    genDot("./dot/"+graphName(url)+".dot", pairsToDot(name, orders, links=links))
    genHtml(graphName(url), name)
    #genPdf("gv/"+nodeName(name)+".gv", "pdf/"+nodeName(name)+".pdf")
