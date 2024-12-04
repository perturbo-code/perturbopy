#!/usr/bin/env python3
"""
Tools to generate the Fortran source code files
"""

import os
import re
import datetime
import collections

from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def fortran_bcast_variable(
    param_name, fout, processid="meta_ionode_id", commid="world_comm"
):
    """
    Print a Fortran `mpi broadcast` statement.

    Parameters
    -----
       param_name: str
          Name of the parameter

       processid: str
          ID of the process which broadcasts the data

       commid:
          ID of the communicator

       fout: output file
          Text file of the f90 source code


    Returns
    -----
       None

    """
    declare_indent = " " * 3
    fout.write((f"{declare_indent}call mp_bcast({param_name},{processid},{commid})\n"))


def fortran_init_variable(param_name, param_type, param_default_value, fout, dim=""):
    """
    Print a Fortran `variable assignment` statement for automatically generating input variables from yaml file.

    Parameters
    -----
       param_name: str
          Name of the parameter

       param_type: str
          Fortran type of the parameter

       param_default_value: formatted
          Default value of the parameter

       fout: output file
          Text file of the f90 source code

       dim:
          Dimension of a vector

       description:
          Description of the variable for doxygen

    Returns
    -----
       None

    Raises
    -----
     ValueError if parameter is unknown

    """

    declare_indent = " " * 3

    param_default_value_assign = param_default_value
    if dim is not None and (not dim == ""):
        # only one-dimensional array are implemented.
        if type(param_default_value) == str and param_default_value[0] == "(":
            if param_type == "logical":
                param_default_value_assign = (
                    param_default_value_assign.replace("(", "")
                    .replace(")", "")
                    .strip()
                    .split(",")
                )
                for iva in range(len(param_default_value)):
                    param_default_value_assign[iva] = fortran_bool(
                        bool(param_default_value[iva])
                    )
                param_default_value_assign = (
                    "[" + ",".join(f"{ii}" for ii in param_default_value) + "]"
                )
            else:
                param_default_value_assign = param_default_value_assign.replace(
                    "(", "["
                ).replace(")", "]")
        elif param_type == "logical":
            param_default_value_assign = fortran_bool(param_default_value_assign)
    else:
        if param_type == "logical":
            param_default_value_assign = fortran_bool(param_default_value_assign)
        elif param_type == "real":
            param_default_value_assign = str(param_default_value_assign) + "_dp"

    fout.write(f"{declare_indent}{param_name} =" f" {param_default_value_assign}\n")


def fortran_declare_variable(
    param_name, param_type, param_attr, param_len, fout, dim="", description=""
):
    """
    Print a Fortran `variable declaration` statement for automatically generating input variables from yaml file.

    Parameters
    -----
       param_name: str
          Name of the parameter

       param_type: str
          Fortran type of the parameter

       param_attr: str
          Fortran attributes for a new variable when declaration

       param_len: Int
          Length of the string for Character datetype

       fout: output file
          Text file of the f90 source code

       dim:
          Dimension of a vector

       description:
          Description of the variable for doxygen

    Returns
    -----
       None

    Raises
    -----
     ValueError if parameter is unknown

    """

    declare_indent = " " * 3

    if param_type == "string":
        declare_type = f"character(len={param_len})"

    elif param_type == "logical":
        declare_type = "logical"

    elif param_type == "integer":
        declare_type = "integer"

    elif param_type == "real":
        declare_type = "real(dp)"

    else:
        raise ValueError(f"Wrong param_type {param_type}")

    if param_attr is not None:
        fout.write(
            f"{declare_indent}{declare_type}"
            f", {param_attr}"
            f" :: {param_name}{dim}"
            f" !< {description}\n"
        )
    else:
        fout.write(
            f"{declare_indent}{declare_type}"
            f" :: {param_name}{dim}"
            f" !< {description}\n"
        )


def fortran_write(param_name, param_type, unit, fout, dim=None, bcast_name=None):
    """
    Print a Fortran `write` statement

    Parameters
    -----
       param_name: str
          Name of the parameter

       param_type: str
          Fortran type of the parameter

       unit: str
          Fortran file unit where the write statement will output

       fout: output file
          Text file of the f90 source code

       dim:
          Dimension of a vector

       bcast_name:
          Name of a variable in the code (if different from param_name)

    Returns
    -----
       None

    Raises
    -----
     ValueError if parameter is unknown

    """

    print_indent = " " * 3
    write_indent = 6
    write_space = 10

    write_value = param_name

    if param_type == "string":
        write_value = f"trim({param_name})"
        write_format = "a"

    elif param_type == "logical":
        write_value = f"python_bool({param_name})"
        write_format = "a"

    elif param_type == "integer":
        write_format = "i10"

    elif param_type == "real":
        write_format = "es23.16"

    else:
        raise ValueError(f"Wrong param_type {param_type}")

    # In the case if the name in the code is different from the name in the
    # input file, just substitue the param_name with bcast_name
    if bcast_name is not None:
        write_value = re.sub(param_name, bcast_name, write_value)

    if dim is not None:
        # only one-dimensional array are implemented.
        # otherwise, int(...) will raise an Error
        dim_int = int(dim.replace("(", "").replace(")", ""))

        vec_format = '"[",'

        vec_format += f'{dim_int}({write_format},","2x)'

        vec_format += ',"]"'

        write_format = vec_format

    fout.write(
        f"{print_indent}write("
        f"{unit},'({write_indent}x, a, {write_space}x, {write_format})')"
        f" '{param_name}:', {write_value}\n"
    )


def print_header(fout):
    """
    Print header, information how to properly modify the file

    Parameters
    -----
       fout : output file
          file where to print the header
    """

    fout.write(
        (
            f"! This file was automatically generated by the"
            f" {os.path.basename(__file__)} Python script\n"
            f"! from the ./utils folder.\n"
            f"! To do any modifications, please modify the"
            f" YAML files in the ./docs folder or the script directly.\n"
            f"! NOTE THAT the modifications will be erased when"
            f" you run the Python script again.\n"
            f'! Date: {datetime.datetime.now().strftime("%B %d, %Y %H:%M")}\n\n'
        )
    )


def fortran_bool(trueornot):
    """
    convert python bool to fortran bool

    Parameters
    -----
       trueornot: str
          logically true or not in Python

    Returns
    -----
       fortran_bool_type: str ['.true.', '.false.']
          logically true or not in Fortran
    """

    if trueornot:
        return ".true."
    elif not trueornot:
        return ".false."
    else:
        raise ValueError(f"Wrong param_type {trueornot}")


def write_param_to_yaml(folder, input_param_path, code_prefix):
    """
    Generate an f90 file to print out all of the input parameters of Perturbo

    Parameters
    -----
       input_param_path: str
          path to a YAML files with the input parameters
       code_prefix: str
          name of the executable (without `.x`). `perturbo` or `qe2pert`
       folder: str
          A folder where the f90 file should be placed

    Returns
    -----
       None
    """

    with open(input_param_path, "r") as stream:
        input_param_dict = load(stream, Loader=Loader)

        # sort
        input_param_dict = collections.OrderedDict(sorted(input_param_dict.items()))

    f90filename = os.path.join(folder, f"param_to_yaml_{code_prefix}.f90")

    unit = "ymlout"

    with open(f90filename, "w") as f90file:
        print_header(f90file)

        f90file.write((f"module {code_prefix}_autogen_output_yaml\n"))
        f90file.write(("   use yaml_utils, only: ymlout, python_bool\n"))
        if code_prefix == "perturbo":
            f90file.write(("   use pert_param\n"))
        elif code_prefix == "qe2pert":
            f90file.write(("   use input_param\n"))
        else:
            raise ValueError(
                f"{code_prefix} can not be recognised and you may need to add an elif branch here!"
            )
        f90file.write(("   implicit none\n"))
        f90file.write(("   private\n\n"))
        f90file.write(("   public :: auto_output_beforeconv_to_yaml\n"))
        f90file.write(("   public :: auto_output_afterconv_to_yaml\n"))

        f90file.write(("\ncontains\n"))
        f90file.write(("subroutine auto_output_afterconv_to_yaml()\n"))
        f90file.write(("   implicit none\n"))

        for param_name, param_dict in input_param_dict.items():
            if param_dict["type"] == "family":
                continue

            if "output" in param_dict.keys() and not param_dict["output"]:
                continue

            # some names used in the code are not the same as the names read
            # from input
            if "bcast_name" in param_dict.keys():
                bcast_name = param_dict["bcast_name"]
            else:
                bcast_name = None

            param_type = param_dict["type"]

            dim = param_dict.get("dimensions", None)

            fortran_write(
                param_name, param_type, unit, f90file, dim=dim, bcast_name=bcast_name
            )

        f90file.write(("\nend subroutine auto_output_afterconv_to_yaml\n\n"))

        # before unit conversion
        f90file.write(
            (
                '! the "before conversion" variabls has not been broadcast to other nodes, so it can just be used in master (io) node.\n'
            )
        )
        f90file.write(("subroutine auto_output_beforeconv_to_yaml()\n"))
        f90file.write(("   implicit none\n"))

        for param_name, param_dict in input_param_dict.items():
            if param_dict["type"] == "family":
                continue

            if "output" in param_dict.keys() and not param_dict["output"]:
                continue

            # here is different with the "after conversion", we just keep the variables on the master node
            # also here use a poor-man trick
            bcast_name = param_name + "_beforeconv"
            # some names used in the code are not the same as the names read
            # from input
            # if 'bcast_name' in param_dict.keys():
            #   bcast_name = param_dict['bcast_name']
            # else:
            #   bcast_name = None

            param_type = param_dict["type"]

            dim = param_dict.get("dimensions", None)

            fortran_write(
                param_name, param_type, unit, f90file, dim=dim, bcast_name=bcast_name
            )

        f90file.write(("\nend subroutine auto_output_beforeconv_to_yaml\n\n"))
        # normal keywords for module
        f90file.write(("end module {code_prefix}_autogen_output_yaml\n"))


def autogen_declare_init_bcast_inputvariables(folder, input_param_path, code_prefix):
    """
    Generate an f90 file to declare all of the input parameters of Perturbo

    Parameters
    -----
       folder: str
          A folder where the f90 file should be placed
       input_param_path: str
          path to a YAML files with the input parameters
       code_prefix: str
          name of the executable (without `.x`). `perturbo` or `qe2pert`

    Returns
    -----
       None
    """

    with open(input_param_path, "r") as stream:
        input_param_dict = load(stream, Loader=Loader)

        # sort
        input_param_dict = collections.OrderedDict(sorted(input_param_dict.items()))

    f90filename = os.path.join(folder, "autogen_param_{code_prefix}.f90")

    with open(f90filename, "w") as f90file:
        print_header(f90file)

        # normal keywords for module
        f90file.write(("module {code_prefix}_autogen_param\n"))
        if code_prefix == "perturbo":
            f90file.write(("   use pert_const, only: dp\n"))
        elif code_prefix == "qe2pert":
            f90file.write(("   use kinds, only: dp\n"))
            f90file.write(("   use io_files, only: prefix\n"))
        else:
            raise ValueError(
                f"{code_prefix} can not be recognised and you may need to add an elif branch here!"
            )
        f90file.write(("   implicit none\n"))

        cnt_param = 0
        for param_name, param_dict in input_param_dict.items():
            if param_dict["type"] == "family":
                continue
            cnt_param += 1  # do not shift this counting line below if-conditional line for "param_source"

            param_source = param_dict.get("source", None)

            if param_source is not None and param_source != f"{code_prefix}":
                continue

            param_type = param_dict["type"]

            param_attr = param_dict.get("attributes", None)

            param_len = param_dict.get("len", None)

            dim = param_dict.get("dimensions", "")

            description = param_dict.get("description", " Not yet")

            fortran_declare_variable(
                param_name,
                param_type,
                param_attr,
                param_len,
                f90file,
                dim=dim,
                description=description,
            )

        f90file.write("\n")

        # before conversion
        for param_name, param_dict in input_param_dict.items():
            if param_dict["type"] == "family":
                continue

            param_type = param_dict["type"]

            param_attr = param_dict.get("attributes", None)

            param_len = param_dict.get("len", None)

            dim = param_dict.get("dimensions", "")

            description = param_dict.get("description", " Not yet")

            param_name += "_beforeconv"
            description += " (before conversion of the unit)"

            fortran_declare_variable(
                param_name,
                param_type,
                param_attr,
                param_len,
                f90file,
                dim=dim,
                description=description,
            )

        # namelist
        f90file.write((f"\n   namelist / {code_prefix} / & \n"))
        cnt = 0
        for param_name, param_dict in input_param_dict.items():
            if param_dict["type"] == "family":
                continue
            cnt += 1
            if cnt < cnt_param:
                f90file.write((f"      {param_name}, & \n"))
            else:
                f90file.write((f"      {param_name}\n"))

        f90file.write(("\ncontains\n"))
        f90file.write(("subroutine autogen_init_input_param()\n"))
        f90file.write(("   implicit none\n"))

        for param_name, param_dict in input_param_dict.items():
            if param_dict["type"] == "family":
                continue

            param_value_default = param_dict.get("default", None)

            if param_value_default is None:
                continue

            param_type = param_dict["type"]

            dim = param_dict.get("dimensions", "")

            fortran_init_variable(
                param_name, param_type, param_value_default, f90file, dim=dim
            )

        f90file.write(("\nend subroutine autogen_init_input_param\n\n"))

        # broadcast from the main process
        f90file.write(("subroutine autogen_bcast_input_param()\n"))

        if code_prefix == "perturbo":
            f90file.write(
                ("   use qe_mpi_mod, only: meta_ionode_id, world_comm, mp_bcast\n")
            )
        elif code_prefix == "qe2pert":
            f90file.write(
                (
                    "   use io_global, only: ionode_id\n"
                    "   use mp_world, only: world_comm\n"
                    "   use mp, only: mp_bcast\n"
                )
            )
        else:
            raise ValueError(
                f"{code_prefix} can not be recognised and you may need to add an elif branch here!"
            )
        f90file.write(("   implicit none\n\n"))

        if code_prefix == "perturbo":
            param_bcast_processid, param_bcast_comm = "meta_ionode_id", "world_comm"
        elif code_prefix == "qe2pert":
            param_bcast_processid, param_bcast_comm = "ionode_id", "world_comm"
        else:
            raise ValueError(
                f"{code_prefix} can not be recognised and you may need to add an elif branch here!"
            )

        for param_name, param_dict in input_param_dict.items():
            if param_dict["type"] == "family":
                continue

            fortran_bcast_variable(
                param_name,
                f90file,
                processid=param_bcast_processid,
                commid=param_bcast_comm,
            )

        f90file.write(("\nend subroutine autogen_bcast_input_param\n\n"))

        # store the data before conversion of the unit.
        f90file.write(("subroutine autogen_input_param_beforeconv()\n"))
        f90file.write(("   implicit none\n"))

        assign_indent = " " * 3
        for param_name, param_dict in input_param_dict.items():
            if param_dict["type"] == "family":
                continue

            f90file.write((f"{assign_indent}{param_name}_beforeconv = {param_name}\n"))

        f90file.write(("\nend subroutine autogen_input_param_beforeconv\n\n"))

        # normal keywords for module
        f90file.write((f"end module {code_prefix}_autogen_param\n"))
