#!/usr/bin/env python3
"""
This script reads the PERTURBO workflow information from the ../docs/workflow.yml file and 
generates the interactive html page.
To run the script a user should first install Graphviz and then pygraphviz.
Installation for Mac:
brew install graphviz
pip install --install-option="--include-path=/usr/local/include/" --install-option="--library-path=/usr/local/lib/" pygraphviz

<Alternative for Mac>:
brew install graphviz
brew info graphviz
export GRAPHVIZ_DIR="/usr/local/Cellar/graphviz/<VERSION>"
pip install pygraphviz --global-option=build_ext --global-option="-I$GRAPHVIZ_DIR/include" --global-option="-L$GRAPHVIZ_DIR/lib"

To generate the Interactive Workflow webpage:
1. run the script
./interactive_workflow.py

2. copy the .html page to the site repository
cp mydoc_interactive_workflow.html ~/github/perturbo-code.github.io/pages/mydoc

3. copy the diagram to the site repository
cp graph.svg ~/github/perturbo-code.github.io/images

"""

import os, re, sys, datetime
import pygraphviz as pgv

from htmltools import print_inputs_to_html

from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


############################################################################################
def create_graph_dict(data_dict):
    """
    Create a graph Python dictionary of dictionaries from the workflow YAML file
    """
    graph_dict = {}
    interactive_nodes = []
    non_interactive_nodes = []
    for calc_mode in data_dict.keys():
        dd = data_dict[calc_mode]

        # Find all parents
        d_tmp = {}
        if "parents" in dd.keys():
            for par in dd["parents"]:
                d_tmp[par] = None

        if "non-interactive" in dd.keys():
            if dd["non-interactive"] == True:
                non_interactive_nodes.append(calc_mode)
            else:
                interactive_nodes.append(calc_mode)
        else:
            interactive_nodes.append(calc_mode)

        graph_dict[calc_mode] = d_tmp

    return graph_dict, interactive_nodes, non_interactive_nodes


############################################################################################


#
# Load the files description files
#
workflow_filename = "files_description.yml"

with open(workflow_filename, "r") as stream:
    files_desc_dict = load(stream, Loader=Loader)

#
# Load the workflow.yml file
#
workflow_filename = "workflow.yml"

with open(workflow_filename, "r") as stream:
    workflow_dict = load(stream, Loader=Loader)


graph_dict, interactive_nodes, non_interactive_nodes = create_graph_dict(workflow_dict)

print("Interactive nodes:", interactive_nodes)
print("Non-interactive nodes: ", non_interactive_nodes)

A = pgv.AGraph(graph_dict, strict=False, directed=True).reverse()


A.node_attr["shape"] = "rectangle"
# A.edge_attr['color']='red'

# Make non-interactive nodes elliptical
for node in non_interactive_nodes:
    n = A.get_node(node)
    n.attr["shape"] = "ellipse"
    # n.attr['color']='gray'

# Make the connections between the optional parents
for calc_mode in workflow_dict.keys():
    if "optional parents" in workflow_dict[calc_mode].keys():
        optional_parents = workflow_dict[calc_mode]["optional parents"]
        for opt_parent in optional_parents:
            # constraint=false will not change the hierarchy for the nodes
            A.add_edge(opt_parent, calc_mode, style="dashed", constraint="false")

# parameters for the separation between nodes: pad="0.5", nodesep="1", ranksep="2"
A.graph_attr["nodesep"] = 0.5

A.graph_attr["rankdir"] = "LR"

# A.graph_attr['size'] = "120,30"

# A.graph_attr.update(size="6,6")

# dpi = 150
# A.graph_attr['dpi'] = dpi

# Possible layouts:
# neato, dot, twopi, circo, fdp, nop, wc, acyclic, gvpr, gvcolor, ccomps, sccmap, tred, sfdp, unflatten
A.layout(prog="dot")

# A.graph_attr.update(landscape='true',ranksep='0.1')

rect_list = []
for n in A.iternodes():
    w = float(n.attr["width"])  # * dpi
    h = float(n.attr["height"])  # * dpi
    x, y = list(map(float, n.attr["pos"].split(",")))
    x1 = x - w / 2
    x2 = x + w / 2
    y1 = y - h / 2
    y2 = y + h / 2
    rect_list.append([x, y, w, h])
    # print(n.attr['pos'], n.attr['width'], n.attr['height'])

# A.draw(path='graph.png')

graph_filename = "graph.svg"
A.draw(path=graph_filename)
A.draw(path="graph.png")

#
# Parse the svg file to get coordinates of rectangles, get the coordinates from 'pos' is complicated
# because of complicated units.
#

polygone_dict = {}

with open(graph_filename, "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        # if 'width' in line:
        #   image_width = int(line.split('width=')[1].split()[0].strip('"pt'))
        #   image_height = int(line.split('height=')[1].split()[0].strip('"pt'))
        if "viewBox" in line:
            image_width, image_height = list(
                map(float, line.split("viewBox=")[1].replace('"', "").split()[2:4])
            )
        if "translate" in line:
            x_offset, y_offset = list(
                map(float, re.sub(r'[()">]', "", line.split("translate")[1]).split())
            )
            y_offset = image_height - y_offset

        # line example: <!-- dynamics&#45;run -->
        if (
            "<!--" in line
            and line.split()[1].replace("&#45;", "-") in interactive_nodes
        ):
            node = line.split()[1].replace("&#45;", "-")
            # line example: <polygon fill="none" stroke="black" points="378.99,-36 286.99,-36 286.99,0 378.99,0 378.99,-36"/>
            poly_line = lines[i + 3]
            pairs = poly_line.split("points=")[1].strip('"/>').split()[:-1]
            pairs_list = [tuple(map(float, p.split(","))) for p in pairs]
            polygone_dict[node] = pairs_list

corner_dict = {}

plot_x = 12
plot_y = plot_x / image_width * image_height

fig, ax = plt.subplots(1, figsize=(plot_x, plot_y))

scale = 1.2


#
# Create an html file
#
id_prefix = "hide_input_block"

html_filename = "mydoc_interactive_workflow.html"
html = open(html_filename, "w")

html.write("---\n")
html.write("title: Interactive Workflow of Perturbo\n")
html.write("sidebar: mydoc_sidebar\n")
html.write("last_updated: {}\n".format(datetime.date.today().strftime("%B %d, %Y")))
html.write("permalink: {}\n".format(html_filename))
html.write("folder: mydoc\n")
html.write(
    "summary: PERTURBO package provides computation of different material properties, such as interpolated band structure or phonon dispersion, carrier mobility, imaginary part of e-ph self-energy, etc. Different types of calculations are called calculation modes. Generation of the <em>prefix_epr.h5</em> file that contains the e-ph elements in Wannier basis is done using the <code>qe2pert.x</code> executable. All the rest of the calculation modes are performed with <code>perturbo.x</code>. Each calculation mode requires a different set of input files and provides different outputs. \n"
)
html.write("toc: false\n")
html.write("---\n")
html.write(
    "<!-- This file was generated by the python script: {} \n To do any modifications, please, modify the script directly. -->\n\n".format(
        os.path.basename(__file__)
    )
)

html.write("<html>\n")
html.write("<head>\n\n")

html.write("<!-- Style -->")
html.write('<link rel="stylesheet" href="css/my_style.css">\n\n')

html.write("<!-- Add maphilight plugin -->\n")
html.write(
    '<script type="text/javascript" src="js/jquery.maphilight.min.js"></script>\n'
)
html.write("\n")
html.write("<!-- Activate maphilight plugin -->\n")
html.write('<script type="text/javascript">$(function() {\n')
html.write("        $('.map').maphilight();\n")
html.write("    });\n")
html.write("</script>\n\n")

html.write(
    "<!-- Script to trigger show/hide blocks when a calculation mode is selected -->\n"
)
html.write("<script>\n")
html.write("$(document).ready(function(){\n")
html.write('$(".calc_mode_block").on("click", function(e){\n')
html.write("   e.preventDefault();\n")
html.write("\n")
html.write("   /* get the id of the clicked block */\n")
html.write("   elem_id = this.id\n")
html.write("\n")
html.write("   ShowBlockInteractive(elem_id)\n")
html.write("\n")
html.write("   });\n")
html.write("});\n")
html.write("</script>\n\n")

html.write(
    "<!-- For maphighlight redefine post-content img, otherwise, the map boxes would be shifted down-->\n"
)
html.write("<style>\n")
html.write(".post-content img {\n")
html.write("    margin: 0px 0px 0px 0px;\n")
html.write("    width: auto;\n")
html.write("    height: auto;\n")
html.write("    max-width: 100%;\n")
html.write("    max-height: 100%;\n")
html.write("}\n")
html.write("</style>\n\n")

html.write("</head>\n\n")


html.write("<body>\n\n")

#
# Header text of the page
#
html.write(
    "<p>To get the calculation mode requirements, outputs, and the input file, click on a calculation mode name in the graph below or select the calculation mode from the list (recommended for mobile devices): \n\n"
)
html.write(
    '<select id="CalcModeSelect" onchange="ShowBlockInteractive(this.options[this.selectedIndex].value)">\n'
)
html.write('  <option value="">Select...</option>\n')

for calc_mode in interactive_nodes:
    html.write('  <option value="' + calc_mode + '">' + calc_mode + "</option>\n")

html.write("</select>\n")
html.write("</p>\n")

html.write("<br>\n" * 2)
html.write(
    '<img src="images/graph.svg" class="map" style="width:{}px;height:{}px" alt="Workflow" usemap="#workflow" />\n\n'.format(
        image_width, image_height
    )
)

html.write('<map name="workflow">\n')

#
# Write the polygones coordinates for the HTML image map
#
for node, p in polygone_dict.items():
    left_bottom = p[1]
    right_top = p[3]
    xmin = left_bottom[0] + x_offset
    xmax = right_top[0] + x_offset

    # ymin = -left_bottom[1] + y_offset
    # ymax = -right_top[1]   + y_offset

    ymin = left_bottom[1] - y_offset + image_height
    ymax = right_top[1] - y_offset + image_height

    corner_dict[node] = "{},{},{},{}".format(xmin, ymin, xmax, ymax)

    html.write(
        '  <area class="calc_mode_block" id={0:<15} shape="rect" coords={1:<30} alt={0:<15} href="">\n'.format(
            '"' + node + '"', '"' + corner_dict[node] + '"'
        )
    )

    # debug
    # w = xmax - xmin
    # h = ymax - ymin
    # rect = Rectangle((xmin,ymin),w,h)
    # ax.add_patch(rect)

html.write("</map>\n\n")

html.write("<br>\n" * 3)

html.write("\n<!-- ===Computes div blocks=== -->\n\n")
for node in interactive_nodes:
    # Title
    html.write('<div id="hide_title_{0}" style="display:none;">\n'.format(node))
    html.write(
        '<p style="font-size:30px; text-align:center;"> Calculation mode: <code>{0}</code></p>\n\n'.format(
            node
        )
    )
    html.write("</div>\n\n")

    computes = workflow_dict[node]["computes"]

    tutorial_link = workflow_dict[node]["tutorial link"]
    tutorial_link = f' <a href="{tutorial_link}">See in tutorial.</a>'

    # Replace $$...$$ with <script type="math/tex">...</script> with Python re
    computes = re.sub(
        r"\$\$(.+?)\$\$", r'<script type="math/tex">\1</script>', computes
    )

    computes = computes + tutorial_link

    html.write("<!--{}-->\n".format(node))
    html.write(
        '<div id="hide_computes_block_{}" markdown="span" class="alert alert-success" style="display:none" role="alert"><i class="fa fa-server fa"></i> <b> Computes:&nbsp;</b>'.format(
            node
        )
    )
    html.write(computes)
    html.write("</div>\n\n")


html.write("<br>\n")

#
# === Require and Output ===
#

html.write("\n<!-- ===Require and Output div blocks=== -->\n\n")
for node in interactive_nodes:
    html.write("<!--{}-->\n".format(node))

    html.write(
        '<div id="hide_req_img_out_block_{}" class="req_img_out_wrapper" style="display:none">\n\n'.format(
            node
        )
    )

    #
    # Requirements
    #
    html.write("  <!-- Requirements block -->\n")
    html.write('  <div class="left_require">\n')  # Start require block
    html.write(
        '    <p style="font-size:140%; text-decoration: underline">Required Files:</p>\n'
    )
    html.write(
        '    <p style="font-size:80%;text-align:center; margin-top:4%">(click on a filename to get its description)</p>\n'
    )
    html.write(
        '    <ul style="list-style-type:none;padding-left: 0">\n'.format(node)
    )  # Start list

    file_req_list = workflow_dict[node]["requirements"] + ["input file"]

    if "optional files" in workflow_dict[node].keys():
        file_opt_list = workflow_dict[node]["optional files"]
    else:
        file_opt_list = []

    for i, file_req in enumerate(file_req_list):
        html.write(
            '    <li><div style="cursor:pointer" onclick="ShowFileDesc(this.id,\'left\')" id="{0}">\n'.format(
                file_req
            )
        )
        html.write(
            '    <img src=images/icons/{}.svg style="width:8%" >\n'.format(
                files_desc_dict[file_req]["type"]
            )
        )
        html.write("&nbsp;&nbsp;{0:<30}\n".format(file_req))
        html.write("    </div></li>\n")
        # if i < len(workflow_dict[node]['requirements'])-1:
        #   html.write('<hr class="dashed_line">\n')
        html.write("\n")
        if i < len(file_req_list) - 1 or len(file_opt_list) > 0:
            html.write('<hr class="dashed_line">\n')

    for i, file_opt in enumerate(file_opt_list):
        html.write(
            '    <li><div style="cursor:pointer" onclick="ShowFileDesc(this.id,\'left\')" id="{0}">\n'.format(
                file_opt
            )
        )
        html.write(
            '    <img src=images/icons/{}.svg style="width:8%" >\n'.format(
                files_desc_dict[file_opt]["type"]
            )
        )
        html.write("&nbsp;&nbsp;{0:<30} <i>(optional)</i>\n".format(file_opt))
        html.write("    </div></li>\n")
        # if i < len(workflow_dict[node]['requirements'])-1:
        #   html.write('<hr class="dashed_line">\n')
        html.write("\n")
        if i < len(file_opt_list) - 1:
            html.write('<hr class="dashed_line">\n')

    html.write("    </ul>\n")  # End list
    html.write("  </div>\n\n")  # End require block

    #
    # PERTURBO hourglass
    #
    html.write("  <!-- Image block -->\n")
    html.write('  <div class="center_image">\n')  # Start image block
    html.write(
        '     <img src="images/PERTURBO_hourglass_arrows.svg" alt="PERTURBO" style="display:block; width:100%; margin-left:auto; margin-right:auto" />\n'
    )
    html.write("  </div>\n\n")  # End image block

    #
    # Output files
    #
    html.write("  <!-- Output files block -->\n")
    html.write('  <div class="right_outputs">\n')  # Start output block
    html.write(
        '    <p style="font-size:140%; text-decoration: underline">Output Files:</p>\n'
    )
    html.write(
        '    <p style="font-size:80%;text-align:center; margin-top:4%">(click on a filename to get its description)</p>\n'
    )
    html.write(
        '    <ul style="list-style-type:none;padding-left: 0">\n'.format(node)
    )  # Start list

    for i, file_out in enumerate(workflow_dict[node]["outputs"]):
        html.write(
            '    <li><div style="cursor:pointer" onclick="ShowFileDesc(this.id,\'right\')" id="{0}">\n'.format(
                file_out
            )
        )
        html.write(
            '    <img src=images/icons/{}.svg style="width:8%" >\n'.format(
                files_desc_dict[file_out]["type"]
            )
        )

        if (
            "deprecated" in files_desc_dict[file_out].keys()
            and files_desc_dict[file_out]["deprecated"]
        ):
            html.write(
                '&nbsp;&nbsp;<p style="display:inline;color:#5e5d5d">{0:<30} (deprecated)</p>\n'.format(
                    file_out
                )
            )

        else:
            html.write("&nbsp;&nbsp;{0:<30}\n".format(file_out))

        html.write("    </div></li>\n")

        if i < len(workflow_dict[node]["outputs"]) - 1:
            html.write('<hr class="dashed_line">\n')

    html.write("    </ul>\n")  # End list
    html.write("  </div>\n\n")  # End output block

    html.write("</div>\n\n")  # End Require and Output div block


#
# === Files description ===
#
html.write("<br>\n")

html.write("\n<!-- ===Files description div blocks=== -->\n\n")

html.write(
    '<div id="hide_file_desc_block" class="req_img_out_wrapper" style="display:none;margin-top:0%">\n\n'.format(
        node
    )
)  # Start hide_file_desc_block


#
# Required files
#
html.write("  <!-- Required files description block -->\n")
html.write('<div class="container_desc">\n')  # Start container (place holder)
for file_req in files_desc_dict.keys():
    html.write(
        '  <div class="left_require_file" id="hide_descblock_left_{}" style="display:none">\n'.format(
            file_req
        )
    )  # Start desc block

    html.write(
        '  <div style="display:flex; align-items: center;">'
    )  # Start align block

    html.write(
        '  <img src=images/icons/{}.svg style="width:10%" >\n'.format(
            files_desc_dict[file_req]["type"]
        )
    )

    desc = files_desc_dict[file_req]["description"]
    # Replace $$...$$ with <script type="math/tex">...</script> with Python re
    desc = re.sub(r"\$\$(.+?)\$\$", r'<script type="math/tex">\1</script>', desc)

    html.write('<div style="margin-left: 15px;">\n')  # Start file fields block

    if files_desc_dict[file_req]["type"] == "directory":
        html.write("    <p><i>Folder: </i> <b>{}</b></p>\n".format(file_req))
    else:
        html.write("    <p><i>File: </i> <b>{}</b></p>\n".format(file_req))

    file_type = files_desc_dict[file_req]["type"]

    if file_type == "text":
        file_type = "ASCII text file"
    elif file_type == "HDF5":
        file_type = "HDF5 data file"

    html.write("    <p><i>Type: </i> {}</p>\n".format(file_type))

    if "obtained from" in files_desc_dict[file_req].keys():
        calc_mode_from = files_desc_dict[file_req]["obtained from"]
        if calc_mode_from in interactive_nodes:
            html.write(
                '    <p><i>Obtained from: </i> <code style="cursor:pointer" onclick="ShowBlockInteractive(\'{0}\')">{0}</b></code>\n'.format(
                    files_desc_dict[file_req]["obtained from"]
                )
            )
        else:
            html.write(
                "    <p><i>Obtained from: </i> <code>{0}</b></code>\n".format(
                    files_desc_dict[file_req]["obtained from"]
                )
            )

    html.write('    <div class="left_require_file_desc">\n')
    html.write('    <p style="text-align:justify">{}</p>\n'.format(desc))
    if "format example" in files_desc_dict[file_req].keys():
        example_link = files_desc_dict[file_req]["format example"]

        if (
            "deprecated" in files_desc_dict[file_req].keys()
            and files_desc_dict[file_req]["deprecated"]
        ):
            html_part, name_part = example_link.split("#")

            example_link = f"{html_part}?expand=true#{name_part}"

        html.write(
            '<a href="{}" target="_blank">File format example.</a>'.format(example_link)
        )
    html.write("    </div>\n")

    html.write("</div>\n")

    html.write("  </div>\n\n")  # End align block

    html.write("  </div>\n\n")  # End desc block

html.write("</div>\n\n")  # End container (place holder)

#
# Up arrow
#
# html.write('  <!-- Image block -->\n')
# html.write('  <div class="center_image">\n') # Start image block
# html.write('     <img src="images/PERTURBO_hourglass.svg" alt="PERTURBO" style="display:block; width:40%; margin-left:auto; margin-right:auto" />\n')
# html.write('  </div>\n\n') # End image block

html.write("  <!-- Center block -->\n")
html.write('  <div class="container_center">\n')  # Start image block
html.write("  </div>\n\n")  # End image block


#
# Output files
#
html.write("  <!-- Output files description block -->\n")
html.write('<div class="container_desc">\n')  # Start container (place holder)
# ====================
for file_req in files_desc_dict.keys():
    html.write(
        '  <div class="right_outputs_file" id="hide_descblock_right_{}" style="display:none">\n'.format(
            file_req
        )
    )  # Start desc block

    html.write(
        '  <div style="display:flex; align-items: center;">'
    )  # Start align block

    html.write(
        '  <img src=images/icons/{}.svg style="width:10%" >\n'.format(
            files_desc_dict[file_req]["type"]
        )
    )

    desc = files_desc_dict[file_req]["description"]
    # Replace $$...$$ with <script type="math/tex">...</script> with Python re
    desc = re.sub(r"\$\$(.+?)\$\$", r'<script type="math/tex">\1</script>', desc)

    html.write('<div style="margin-left: 15px;">\n')  # Start file fields block

    if files_desc_dict[file_req]["type"] == "directory":
        html.write("    <p><i>Folder: </i> <b>{}</b></p>\n".format(file_req))
    else:
        html.write("    <p><i>File: </i> <b>{}</b></p>\n".format(file_req))

    file_type = files_desc_dict[file_req]["type"]

    if file_type == "text":
        file_type = "ASCII text file"
    elif file_type == "HDF5":
        file_type = "HDF5 data file"

    html.write("    <p><i>Type: </i> {}</p>\n".format(file_type))

    # No obtained from block for output files

    html.write('    <div class="right_require_file_desc">\n')
    html.write('    <p style="text-align:justify">{}</p>\n'.format(desc))
    if "format example" in files_desc_dict[file_req].keys():
        example_link = files_desc_dict[file_req]["format example"]

        if (
            "deprecated" in files_desc_dict[file_req].keys()
            and files_desc_dict[file_req]["deprecated"]
        ):
            html_part, name_part = example_link.split("#")

            example_link = f"{html_part}?expand=true#{name_part}"

        html.write(
            '<a href="{}" target="_blank">File format example.</a>'.format(example_link)
        )
    html.write("    </div>\n")

    html.write("</div>\n")

    html.write("  </div>\n\n")  # End align block

    html.write("  </div>\n\n")  # End desc block
# ====================

html.write("</div>\n\n")  # End container (place holder)

html.write('<br style="clear: left;" />\n')

html.write("</div>\n\n".format(node))  # End hide_file_desc_block

#
# =======================================================================================
#


html.write("\n<!-- ===Input file div blocks=== -->\n\n")
html.write("<br>\n")
print_inputs_to_html(html, id_prefix, interactive_nodes)

html.write("</body>\n\n")
html.write("</html>\n")

# debug
# ax.set_xlim(0,image_width)
# ax.set_ylim(0,image_height)
# plt.savefig('rectangles.svg')
# plt.show()
