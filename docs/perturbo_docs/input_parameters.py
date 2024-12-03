#!/usr/bin/env python3
# This Python script automatically generates the mydoc_param_qe2pert.html
# and mydoc_param_perturbo.html files.

import os
import sys

import htmltools
import f90tools

from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def main():
    # path to the directory where the html file should be placed
    # copy manually the generated .html files to pages/mydoc/ directory of the
    # perturbo site repository

    html_path = "./"

    input_template = "../../src/perturbopy/generate_input/input_template.yml"
    with open(input_template, "r") as stream:
        input_data = load(stream, Loader=Loader)

    #
    # Parameters for qe2pert.x
    #
    # name of the html page
    fout_name = "./mydoc_param_qe2pert.html"
    # name of the yaml file that contains the info about the input parameters
    yaml_dict = "../../src/perturbopy/generate_input/input_parameters_qe2pert.yml"
    # title of the html page
    title = "Quantum Espresso to PERTURBO input parameters"

    print("Generating " + fout_name + " ...")
    htmltools.create_html_file(
        yaml_dict, input_data, html_path, fout_name, title, "qe2pert"
    )

    fout_name = "./mydoc_table_input_parameters_qe2pert.html"
    print("Generating " + fout_name + " ...")
    htmltools.create_html_table(
        yaml_dict, input_data, html_path, fout_name, title, "qe2pert"
    )

    #
    # Parameters for perturbo.x
    #
    fout_name = "./mydoc_param_perturbo.html"
    yaml_dict = "../../src/perturbopy/generate_input/input_parameters_perturbo.yml"
    title = "PERTURBO input parameters"

    print("Generating " + fout_name + " ...")
    htmltools.create_html_file(
        yaml_dict, input_data, html_path, fout_name, title, "perturbo"
    )

    fout_name = "./mydoc_table_input_parameters_perturbo.html"
    print("Generating " + fout_name + " ...")
    htmltools.create_html_table(
        yaml_dict, input_data, html_path, fout_name, title, "perturbo"
    )

    #
    # Generate the f90 files
    #
    print("Generating f90 files ...")

    # For perturo.x: output
    print("param_to_yaml_perturbo.f90")
    input_param_path = (
        "../../src/perturbopy/generate_input/input_parameters_perturbo.yml"
    )
    f90tools.write_param_to_yaml("./", input_param_path, "perturbo")

    print("autogen_param_perturbo.f90")
    # For perturo.x: auto generation of vairable declaration
    f90tools.autogen_declare_init_bcast_inputvariables(
        "./", input_param_path, "perturbo"
    )

    # For qe2pert.x
    print("param_to_yaml_qe2pert.f90")
    input_param_path = (
        "../../src/perturbopy/generate_input/input_parameters_qe2pert.yml"
    )
    f90tools.write_param_to_yaml("./", input_param_path, "qe2pert")

    # For qe2pert.x: auto generation of vairable declaration
    print("autogen_param_qe2pert.f90")
    f90tools.autogen_declare_init_bcast_inputvariables(
        "./", input_param_path, "qe2pert"
    )
    #
    # Input files HTML page generation
    #

    # Move the generated input_examples.html file to _includes directory of the site.
    # mv input_examples.html ~/github/perturbo-code.github.io/_includes

    fout_name = "input_examples.html"
    print("Generating " + fout_name + " ...")
    htmltools.print_select_button_header(fout_name, yaml_dict)


if __name__ == "__main__":
    main()
