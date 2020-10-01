import sys
import os
import xml.etree.ElementTree as ET 


class Coding:
    cur_dir = os.path.dirname(sys.argv[0])

    def __init__(self, coding_file):
        self.coding_file = coding_file

    # Parse Cafex .xml 
    # Return an array of dictionaries of type:
    # dict = {name: 'coding_param_name', defval: ['24']}  - decimal value  or
    # dict = {name: 'coding_param_name', defval: ['5A', '7B', '60']}  - hex array value
    def parseCafex(self):
        tree = ET.parse(self.coding_file)
        root = tree.getroot()

        params_all = []
        for rt in root[0]:
            if 'conditionalFunction' in rt.tag:
                param = {'name': '', 'defval': []}
                defval_found = False
                defval_isarray = False
                cmmt_val = 0

                for cf in rt:
                    if 'name' in cf.tag:
                        param['name'] = cf.text.strip()
                    if 'comment' in cf.tag:
                        cmmt_val = cf.text.split('defaultValue: ')[1].split('[')[0].strip()
                        if ';' in cmmt_val: defval_isarray = True
                    if 'defaultValue' in cf.tag:
                        defval_found = True
                        param['defval'].append(cf.text.strip())

                if not defval_found: 
                    param['defval'].append(cmmt_val)
                    if defval_isarray:
                        hex_array = cmmt_val.split(';')
                        param['defval'] = hex_array
                else:
                    if defval_isarray:
                        n = 2
                        hex_array = [(param['defval'][0][i:i+n]) for i in range(0, len(param['defval'][0]), n)]
                        param['defval'] = hex_array
                
                if param['name']:
                    params_all.append(param)


        return params_all


##############################################################################################
# Parse cafd coding .xml to get default values 
# - arg 1: coding.xml file path
##############################################################################################
if __name__ == "__main__":
    coding = Coding(sys.argv[1])
    print (coding.parseCafex())