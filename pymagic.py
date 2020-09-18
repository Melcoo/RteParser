import sys
import os
import copy
import re
from Cheetah.Template import Template

FUNC_TEMPL = 'Rte_'


class RteMock:
    cur_dir = os.path.dirname(sys.argv[0])

    def __init__(self, compiler_header):
        self.compiler_header = compiler_header
        self.__compiler_types = []

        self.__parse_compiler_macros()


    def __parse_compiler_macros(self):
        with open(self.compiler_header, "r") as head:
            for line in head.readlines():
                # Search for lines which contain '#define' and '('
                if ('#define' in line) and ('(' in line):
                    # Get str between '#define' and '('
                    self.__compiler_types.append(re.search(r'#define (.*?)\(', line).group(1))

        # Remove any duplicates
        self.__compiler_types = list(set(self.__compiler_types))


    # Return an array with all read/write functions names
    def parse_lib(self, file):
        func_names = []
        with open(file, "r") as lib:
            for line in lib.readlines():
                line_idx = line.find(FUNC_TEMPL)
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
    # Return: dict for one func with below format
    def __parse_multiple_row(self, func_row, func_name):
        func_decl = {}
        # {
        # 	"retval": "FUNC...",
        # 	"name": "Rte_Read...",
        # 	"params": {
        # 		"decl": "(VAR (uint8, RTE_APPL_DATA) Data)",
        # 		"vals": [
        # 			{
        # 				"type": "VAR (uint8, RTE_APPL_DATA)",
        # 				"name": "Data"
        # 			},
        # 							{
        # 				"type": "P2VAR (AngularSpeedRightObject2, AUTOMATIC, RTE_APPL_DATA)",
        # 				"name": "Data"
        # 			}
        # 		]
        # 	}
        # }

        func_row = func_row.replace('\n', '')
        # Function Return type
        func_decl['retval'] = 'FUNC(' + re.search(r'FUNC\((.*?)\)', func_row).group(1) + ')'
        # Function Name
        func_decl['name'] = func_name
        func_row = func_row.split(func_name, 1)[1]
        # Function parameters
        func_decl['params'] = {}
        if ('{' in func_row):
            func_decl['params']['decl'] = '(' + re.search(r'\((.*?)\{', func_row).group(1)
        else:
            func_decl['params']['decl'] = func_row.rstrip()
        func_decl['params']['vals'] = self.__parse_params_val(func_decl['params']['decl'])

        return func_decl

    # Extract from params row - Eg: (P2VAR (Rte_ModeType_Coding_DataMode, AUTOMATIC, RTE_APPL_DATA) previousmode, P2VAR (Rte_ModeType_Coding_DataMode, AUTOMATIC, RTE_APPL_DATA) nextmode) - param types and param names
    # Return: array of dicts with  keys: 'type', 'name'
    def __parse_params_val(self, param_row):
        params = []
        macro_idx = []

        # Remove parantheses and white spaces first
        param_row = param_row.lstrip('(').lstrip().rstrip(')')
    
        for macro in self.__compiler_types:
            matches = re.finditer(macro, param_row)
            matches_idx = [match.start() for match in matches]
            if matches_idx:
                for idx in matches_idx:
                    macro_idx.append({
                        'macro': macro,
                        'idx': idx
                    })

        # Make sure the distance between matches is at least 8 - this way we don't confuse VAR with CONSTP2VAR/P2VAR/FUNC_P2VAR
        macro_idx = sorted(macro_idx, key = lambda i: i['idx'])      
        for i, idx in enumerate(macro_idx):
            if (i > 0) and (macro_idx[i]['idx'] < (macro_idx[i-1]['idx'] + 8)):
                macro_idx.pop(i)
        # macro_idx should look like this: [{'macro': 'P2VAR', 'idx': 0}, {'macro': 'P2VAR', 'idx': 77}]
        
        # Get type and name for params
        if len(macro_idx) == 1:
            # Only one param in this function declaration
            params.append({
                'type': param_row[:(param_row.rfind(')')+1)],
                'name': param_row.rsplit(')', 1)[1].strip()
            })
        
        elif len(macro_idx) > 1:  
            # Multiple params: sepparate them and then get the type and name
            for i, idx in enumerate(macro_idx):
                if i == (len(macro_idx) - 1):
                    param = param_row[macro_idx[i]['idx']:].rstrip(' ')
                else:
                    param = param_row[macro_idx[i]['idx']:macro_idx[i+1]['idx']].rstrip(' ').rstrip(',')

                params.append({
                    'type': param[:(param.rfind(')')+1)],
                    'name': param.rsplit(')', 1)[1].strip()
                })       

        return params


    def gen_template(self, funcs, templ_files, out_files): 
        for i, templ in enumerate(templ_files):
            with open(templ, 'r') as f:
                t = Template(f.read())
                t.funcs_decl = funcs
                with open(out_files[i], 'w') as f:
                    f.write(str(t))



##############################################################################################
# Extract c function declarations from lib exports and rte files
# - arg 1: "Compiler.h" path
# - arg 2: "Rte.c" path
# - arg 3: lib file (text) path
# - arg 4: "Rte.c" template file path
# - arg 5: "Rte.c" generated file path
# - arg 6: "Rte.h" template file path
# - arg 7: "Rte.h" generated file path
##############################################################################################
if __name__ == "__main__":
    mock = RteMock(sys.argv[1])
    func_names = mock.parse_lib(sys.argv[3])
    funcs = mock.parse_rte(func_names, sys.argv[2])
    mock.gen_template(funcs, [sys.argv[4], sys.argv[6]], [sys.argv[5], sys.argv[7]])

    for i, f in enumerate(funcs): print('{}: {}'.format(i, f))