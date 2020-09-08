import sys
import os
import copy
import re
from Cheetah.Template import Template

FUNC_TEMPL = 'Rte_'



class RteMock:
    cur_dir = os.path.dirname(sys.argv[0])

    def __init__(self, template):
        self.template = template


    # Return an array with all read/write functions names
    def parse_lib(self, file):
        func_names = []
        with open(file, "r") as lib:
            for line in lib.readlines():
                line_idx = line.find('Rte_')
                if (line_idx != -1):
                    func_names.append(line[line_idx:].replace('\n', ''))
 
        return func_names


    # Return an array of dictionaries containing all functions and parameters 
    def parse_rte(self, func_names, rte_file):
        # A function in Rte.c should look like this:
        #
        #   FUNC(Std_ReturnType, RTE_CODE)
        #   Rte_Read_SwcLaMaster_LceSte_LowBeamOn
        #   (P2VAR (UInt1, AUTOMATIC, RTE_APPL_DATA)Data)
        #   {  // Some code   }
        #
        # Or like this:
        # 
        #   FUNC(Std_ReturnType, RTE_CODE) Rte_Call_ctaaCtrlPxl_ppCodingData0_GetEXT_SWITCH_GROUP_3_POWER_RIGHT(
        #   P2VAR(uint8, AUTOMATIC, RTE_APPL_DATA) Value)
        #   {  // Some code   }
        #
        #
        # Once "Rte_" row was found:
        #   - check previous row contains "FUNC("
        #   - check next row contains "(" and ")"
        #   - check that row after next contains "{"
        #   - create a single row from all 3 rows
        #   - get the return type found between "FUNC(" and ","
        #   - get the param list between first "(" and last ")" - string just as it is
        # 
        func_decl = []
        temp_func_names = copy.deepcopy(func_names)

        with open(rte_file, "r") as lib:
            # Keep previous 3 lines
            pline3 = ''
            pline2 = ''
            pline1 = ''
            func_found = False

            # Parse Rte.c line by line
            for line0 in lib.readlines():
                if (line0 == '\n'): continue
                rte_idx = pline2.find(FUNC_TEMPL)
                if (rte_idx != -1):
                    # Rte function name occupies the entire row/line
                    rte_func = pline2[rte_idx:].replace('\n', '')
                    if (rte_func in func_names):
                        func_decl.append(self.__parse_multiple_row(pline3 + pline2 + pline1 + line0, rte_func))
                        temp_func_names.remove(rte_func)
                        func_found = True

                    # If some other info is in the row/line, search func_names in line
                    else:
                        for item in temp_func_names:
                            if (item in pline2[rte_idx:]):
                                func_decl.append(self.__parse_multiple_row(pline3 + pline2 + pline1 + line0, item))
                                temp_func_names.remove(item)
                                func_found = True
                                break
                        

                pline3 = pline2
                pline2 = pline1
                pline1 = line0
                func_found = False

        return func_decl

    # Parse string containg func ret type, name, params and return a pretty split array (ex: [FUNC(Std_ReturnType, RTE_CODE), Func_Name, (P2CONST(Type, AUTOMATIC, RTE_APPL_DATA) Data)]) 
    def __parse_multiple_row(self, func_row, func_name):
        func_decl = []

        func_row = func_row.replace('\n', '')
        # Function Return type
        func_decl.append('FUNC(' + re.search(r'FUNC\((.*?)\)', func_row).group(1) + ')')
        # Function Name
        func_decl.append(func_name)
        func_row = func_row.split(func_name, 1)[1]
        # Function parameters
        if ('{' in func_row):
            func_decl.append('(' + re.search(r'\((.*?)\{', func_row).group(1))
        else:
            func_decl.append(func_row.rstrip())

        return func_decl

    def __print_lines(self, pl3, pl2, pl1, cur_l):
        print("3: " + pl3)
        print("2: " + pl2)
        print("1: " + pl1)
        print("0: " + cur_l + "\n")

    def gen_template(self, funcs, output):
        pass


##############################################################################################
# Extract c function declarations from lib exports and rte files
# - arg 1: lib file (text) path
# - arg 2: rte.c file path
# - arg 3: rte include folder path
# - arg 4: results file path
##############################################################################################
if __name__ == "__main__":
    mock = RteMock('c')
    func_names = mock.parse_lib(sys.argv[1])
    funcs = mock.parse_rte(func_names, sys.argv[2])
    # mock.gen_template('c', funcs, sys.argv[4])

    for i, f in enumerate(funcs): print('{}: {}'.format(i, f))