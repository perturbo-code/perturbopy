#!/usr/bin/env python3
"""
Tools for the HTML output
"""

import os
import re
import datetime

from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def get_mandatory_optional(param, input_data, executable):
    if param in ["prefix", "calc_mode"]:
        return "<nobr><b>Mandatory for all calculation types.</b></nobr>"
    elif param in ["output_yaml", "yaml_fname"]:
        return "<nobr>Optional for all calculation types.</nobr>"
    else:
        # loop over the calculation types
        mand_list = []
        opt_list = []
        for calc_mode in input_data.keys():
            if param in input_data[calc_mode]["mandatory"].keys():
                mand_list.append(calc_mode)
            if "optional" in input_data[calc_mode].keys():
                if param in input_data[calc_mode]["optional"].keys():
                    opt_list.append(calc_mode)

        text = ""
        prefix = ""
        if executable == "perturbo":
            calc_mode_link = "<a href=#calc_mode>calc_mode</a>"
            prefix = "&nbsp;" + calc_mode_link + ":"

        if mand_list:
            text = text + "<nobr><i>Mandatory&nbsp;for" + prefix + "</i>" + "&nbsp;" * 2
            for i, tt in enumerate(mand_list):
                text = text + "<code>" + tt + "</code>"
                if i < len(mand_list) - 1:
                    text = text + ",&nbsp;"
                if i == 6:
                    text = text + "</nobr><br><nobr>"
            text = text + "</nobr>\n"

        if opt_list:
            text = text + "<nobr><i>Optional&nbsp;for" + prefix + "</i>" + "&nbsp;" * 2
            for i, tt in enumerate(opt_list):
                text = text + "<code>" + tt + "</code>"
                if i < len(opt_list) - 1:
                    text = text + ",&nbsp;"
                if i == 6:
                    text = text + "</nobr><br><nobr>"
            text = text + "</nobr>\n"

        return text


def write_parameter_info(fout, key, value, color, family_desc, input_data, executable):
    """
    write the information about a parameter
    """
    # For the link
    fout.write("<a name=" + key + "></a>\n")

    # The parameter box starts here
    fout.write(
        '<div class="input_param" style="--background: '
        + lightendarken(color, -87.0)
        + "; --border: "
        + lightendarken(color, 30.0)
        + '">\n'
    )
    fout.write(
        '<div class="family_watermark" style="--color: '
        + lightendarken(color, 10.0)
        + '"><i>'
        + family_desc.upper()
        + "</i></div>\n"
    )
    fout.write('<font size="4"><b>' + key + "</b></font>  \n  ")

    fout.write("<br>" * 2 + "\n")
    fout.write("<i>Variable type: </i>" + value["type"] + "<br>\n")

    if "default" in value.keys():
        fout.write("<i>Default value: </i>" + print_value(value["default"]) + "<br>\n")

    if "typical" in value.keys() and key != "prefix":
        fout.write("<i>Typical value: </i>" + print_value(value["typical"]) + "<br>\n")

    if "dimensions" in value.keys():
        fout.write("<i>Dimensions: </i>" + print_value(value["dimensions"]) + "<br>\n")

    if "units" in value.keys():
        fout.write("<i>Units: </i>" + print_value(value["units"]) + "<br>\n")

    if "options" in value.keys():
        options = value["options"]
        fout.write("<i>Options:</i><br>\n")
        for opt_key, opt_value in options.items():
            fout.write('<div class="options_key">\n')
            fout.write(print_value(opt_key) + "\n")
            fout.write("</div>\n")

            fout.write('<div class="options_value">\n')
            fout.write(str(opt_value))
            fout.write("</div>\n")

            fout.write('<div class="clearfix"></div>\n')

    fout.write("<br>" + "\n")
    fout.write(value["description"])

    if key == "calc_mode":
        fout.write(
            ' To see the typical input files for different calculation modes, <a href="mydoc_generate_input.html#select_button">click here</a>.'
        )

    fout.write("<br>" * 2)

    # Mandatory/Optional box
    fout.write(
        '<button type="button" class="collapsible" style="--background: #999999; --backgr_active: #FFFFFF; --strip-color:'
        + lightendarken(color, 10.0)
        + '">'
        + "&#9660;" * 1
        + "&nbsp;" * 10
        + "Mandatory/Optional"
        + "&nbsp;" * 10
        + "&#9660;" * 1
        + "</button>"
    )
    fout.write(
        '<div class="content" style="--strip-color: '
        + lightendarken(color, 10.0)
        + '">'
    )
    mand_opt_text = get_mandatory_optional(key, input_data, executable)
    fout.write(mand_opt_text)
    fout.write("</div>")
    # End of mandatory/Optional box

    # End of box
    fout.write("</div>\n")
    fout.write("<br>\n")


def lightendarken(color_hsl, percentage):
    h0 = color_hsl[0]
    s0 = color_hsl[1]
    l0 = color_hsl[2]

    p = percentage / 100.0

    if p <= 0.0:
        s = s0 * (1 + p)
        l = l0 - p * (100 - l0)
    else:
        s = s0 + p * (100 - s0)
        l = l0 * (1 - p)

    return "hsl(" + str(h0) + "," + str(s) + "%," + str(l) + "%)"


def print_value(value):
    if type(value) is bool:
        if value is True:
            return "<code>" + ".true." + "</code>"
        else:
            return "<code>" + ".false." + "</code>"
    else:
        return "<code>" + str(value) + "</code>"


def write_header(fout, fout_name, title):
    """
    Print the markdown-style header
    """
    fout.write("---" + "\n")
    fout.write("title: " + title + "\n")
    fout.write("sidebar: mydoc_sidebar" + "\n")
    fout.write("last_updated: " + datetime.date.today().strftime("%B %d, %Y") + "\n")
    fout.write("permalink: " + os.path.basename(fout_name) + "\n")
    fout.write("folder: mydoc" + "\n")
    fout.write("toc: false" + "\n")
    fout.write("---" + "\n")
    fout.write(
        "<!-- This file was generated by the python script: "
        + os.path.basename(__file__)
        + "\n"
        + "To do some modifications, please, modify the script directly. -->"
        + "\n" * 2
    )


def create_html_table(yaml_dict, input_data, html_path, fout_name, title, executable):
    fout = open(html_path + fout_name, "w")

    # input_param is a python dictionary read from the yaml file
    # it contains all the necessary information about the input parameters
    with open(yaml_dict, "r") as stream:
        input_param = load(stream, Loader=Loader)

    write_header(fout, fout_name, title)

    fout.write("<html>\n")
    fout.write("<head>\n")
    # include the css styles file
    fout.write("</head>\n")
    fout.write("<body>\n")
    fout.write("\n")
    fout.write('<table style="width=600" align="left">\n')
    fout.write('<col width="150">\n')
    fout.write('<col width="100">\n')
    fout.write('<col width="350">\n')
    fout.write("\n")

    family_list = []
    for key, value in input_param.items():
        if value["type"] == "family" and value["type"] not in family_list:
            family_list.append(key)

    #
    # loop over families
    #
    # List all the variables that belong to this family
    for family in family_list:
        if len(family_list) > 1:
            fout.write("<tr>\n")
            fout.write(
                '<td colspan="3"><font size="4"><center>'
                + input_param[family]["description"]
                + "</center></font></td>\n"
            )
            fout.write("</tr>\n")
            fout.write("\n")

        fout.write("<tr>\n")
        fout.write("<th>Name</th>\n")
        fout.write("<th>Type</th>\n")
        fout.write("<th>Description</th>\n")
        fout.write("</tr>\n")
        fout.write("\n")

        for key, value in input_param.items():
            if "family" in value.keys() and value["family"] == family:
                fout.write("\n")

                fout.write("<tr>\n")

                fout.write("<td>\n")
                fout.write("<a name=" + key + "></a>\n")
                fout.write("<code>" + key + "</code>\n")
                fout.write("</td>\n")

                fout.write("<td>" + value["type"] + "</td>\n")

                fout.write("<td>\n")
                fout.write(value["description"] + "</br>")
                if "default" in value.keys():
                    fout.write(
                        "<p><i>Default:</i> " + print_value(value["default"]) + "</p>"
                    )
                if "typical" in value.keys() and key != "calc_mode":
                    fout.write(
                        "<p><i>Typical:</i> " + print_value(value["typical"]) + "</p>"
                    )
                if "dimenstions" in value.keys():
                    fout.write(
                        "<p><i>Dimenstions:</i> "
                        + print_value(value["dimenstions"])
                        + "</p>"
                    )
                if "options" in value.keys():
                    fout.write(
                        "<p><i>Options:</i> "
                        + str(list(map(print_value, list(value["options"].keys()))))
                        + "</p>"
                    )
                fout.write("</td>\n")

                fout.write("</tr>\n")

    fout.write("</table>\n")
    fout.write("</body>\n")
    fout.write("</html>\n")
    fout.close()


def create_html_file(yaml_dict, input_data, html_path, fout_name, title, executable):
    fout = open(html_path + fout_name, "w")

    # input_param is a python dictionary read from the yaml file
    # it contains all the necessary information about the input parameters
    with open(yaml_dict, "r") as stream:
        input_param = load(stream, Loader=Loader)

    write_header(fout, fout_name, title)

    fout.write("<html>\n")
    fout.write("<head>\n")
    # include the css styles file
    fout.write('<link rel="stylesheet" href="css/my_style.css">')
    fout.write("</head>\n")
    fout.write("<body>\n")

    #
    # List the fimilies
    #
    # Get the list of all families in the given yaml dictionary
    family_list = []
    color_list = []
    for key, value in input_param.items():
        if value["type"] == "family" and value["type"] not in family_list:
            family_list.append(key)
            color_list.append(value["color_hsl"])

    #
    # FIRST loop over families
    #
    # List all the variables that belong to this family
    for family in family_list:
        color = input_param[family]["color_hsl"]
        fout.write(
            "<h3><a href=#"
            + family
            + ' style="color:Navy; text-decoration: none; border-bottom: 3px solid '
            + lightendarken(color, 0)
            + ';"'
            + ">"
            + input_param[family]["description"]
            + "</a></h3>\n<p>\n"
        )

        fout.write("| ")
        for key, value in input_param.items():
            if "family" in value.keys() and value["family"] == family:
                fout.write("<a href=#" + key + ">" + key + "</a> | " + "\n")

    #
    # SECOND loop over families
    #
    #
    # Write the detailed description of each famility
    #
    fout.write("<br><hr>\n")

    for family in family_list:
        color = input_param[family]["color_hsl"]
        family_desc = input_param[family]["description"]

        if len(family_list) > 1:
            fout.write(
                ' <span style="display:inline-block;background:'
                + lightendarken(color, 0.0)
                + ';width:100%"><font size="5"><a style="color:Navy"; name='
                + family
                + ">&nbsp"
                + input_param[family]["description"]
                + "</a></font></span>\n<br>\n<br>\n"
            )

        for key, value in input_param.items():
            if "family" in value.keys() and value["family"] == family:
                write_parameter_info(
                    fout, key, value, color, family_desc, input_data, executable
                )

        fout.write("<br>" * 2)

    fout.write("</body>\n")
    fout.write("</html>\n")
    fout.close()


def print_inputs_to_html(fout, id_prefix, calc_mode_list):
    """launch the generate_input.py script for all calc modes and print the output in a HTML file"""
    for calc_mode in calc_mode_list:
        os.system("input_generation -c " + calc_mode + " -i " + "tmp.in > /dev/null")

        fout.write(
            '<div id="' + id_prefix + "_" + calc_mode + '" style="display:none">\n'
        )

        fout.write(
            '<p style="font-size:140%; text-decoration: underline">Input File:\n'
        )
        fout.write(
            '<button id="copy_button" style="float: right;" onclick="CopyToClipboard_from_id(\'{}\')" title="Click to copy input file to clipboard" ><i class="fa fa-copy"></i></button>\n'.format(
                calc_mode
            )
        )
        fout.write("</p>\n")
        fout.write(
            '<p style="font-size:80%;text-align:left; margin-top:-1%">(click on a parameter to get its description)</p>'
        )
        fout.write(
            '<div id="input_text_{}" style="margin-top:-1.8%">\n'.format(calc_mode)
        )

        fout.write("{% highlight fortran %}\n")
        # fout.write('<div class="my_code_box">\n')

        if calc_mode == "qe2pert":
            lpath = "l_qe2pert_"
        else:
            lpath = "l_pert_"

        # write all the tmp.in into examples.html
        for line in open("tmp.in", "r"):
            # fout.write(line+'</br>\n')
            if "Date" in line:
                continue

            # Replace param with l_pert_param_end1_calc_mode_end2
            # Then, this "code" line will be interpreted using a javascript to create a link to a parameter
            if "=" in line:
                param = line.split("=")[0].strip("!").strip()

                # when applied, transfrom param(1) to param
                param = re.sub("\(.*\)", "", param)
                line = re.sub(
                    param, lpath + param + "_end1_" + param + "_end2", line, 1
                )

            fout.write(line)

        fout.write("{% endhighlight %}\n")
        fout.write("</div>\n")

        # fout.write('</div>'+'\n')

        fout.write("</div>" + "\n" * 2)
    os.system("rm tmp.in")
    # fout.write('</body>\n')
    # fout.write('</html>\n')


def print_select_button_header(fout_name, yaml_dict):
    """
    Print the header of the select button for the input examples HTML page
    """

    with open(
        "../../src/perturbopy/generate_input/input_parameters_perturbo.yml", "r"
    ) as stream:
        param_data_perturbo = load(stream, Loader=Loader)

    # For the code blocks, <pre> </pre> could be also a solution.

    fex = open(fout_name, "w")

    list_calc_mode = ["qe2pert"] + list(
        param_data_perturbo["calc_mode"]["options"].keys()
    )

    # create the drop down box
    fex.write("<hr>\n")
    fex.write('<a name="select_button"></a>\n')
    fex.write(
        "<p>To get a <em>typical</em> input file without running the script, select the calculation type here: "
    )
    fex.write('<select id="CalcModeSelect" onchange="DropDownFunction()">\n')
    fex.write('  <option value="">Select...</option>\n')
    for calc_mode in list_calc_mode:
        fex.write('  <option value="' + calc_mode + '">' + calc_mode + "</option>\n")
    fex.write("</select>\n")
    # copy to clipboard button
    # fex.write('<button id="copy_button" style="display: none; float: right;" onclick="CopyToClipboard_from_id()" title="Click to copy input file to clipboard" class="hid_button"><i class="fa fa-copy fa-lg"></i></button>\n')
    fex.write("</p>\n")

    # fex.write('</br>'*2+'\n'*2)

    id_prefix = "modeblock"
    print_inputs_to_html(fex, id_prefix, list_calc_mode)
