import sys
import os
import copy


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
            func_found = False
            prev_line_3 = ''
            prev_line_2 = ''
            prev_line_1 = ''

            for line in lib.readlines():
                line_idx = line.find('Rte_')
                if (line_idx != -1):
                    # Rte function name occupies the entire row/line
                    rte_func = line[line_idx:].replace('\n', '')
                    if (rte_func in func_names):
                        func_found = True
                        func_decl.append(rte_func)
                        temp_func_names.remove(rte_func)


                    # If some other info is in the row/line, search func_names in line
                    else:
                        for item in temp_func_names:
                            if (item in line[line_idx:]):
                                func_found = True
                                func_decl.append(item)
                                temp_func_names.remove(item)
                                break
    
                prev_line_3 = prev_line_2
                prev_line_2 = prev_line_1
                prev_line_1 = line


        # print(temp_func_names)
        return func_decl
    

    def __parse_single_row(self, func_names, pl_3, pl_2, pl_1, cur_l):
        pass


    def __parse_multiple_row(self, func_names, pl_3, pl_2, pl_1, cur_l):
        pass


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
    print(len(func_names))
    funcs = mock.parse_rte(func_names, sys.argv[2])
    print(len(funcs))
    # mock.gen_template('c', funcs, sys.argv[4])