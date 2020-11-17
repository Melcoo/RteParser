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
    def parseCafex(self, car_line, miss_val_file = 'UNDEFINED_PARAMS.txt'):
        tree = ET.parse(self.coding_file)
        root = tree.getroot()

        nocarline_params = []
        if car_line == '':
            nocarline_params.append('Missing car line!')
        else:
            nocarline_params.append('Missing values from ' + car_line)


        params_all = []
        for rt in root[0]:
            if 'conditionalFunction' in rt.tag:
                param = {'name': '', 'defval': []}
                defval_found = False
                defval_isarray = False
                carline_found = False
                carline_defval = 0
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
                    if 'conditionalValue' in cf.tag:
                        for cv in cf:
                            if 'value' in cv.tag:
                                carline_defval = cv.text.strip()
                            if 'conditions' in cv.tag:
                                for tc in cv:
                                    if car_line in tc[0].text and tc[1].text and 'true' in tc[1].text:
                                        carline_found = True
                            if carline_found:
                                break

                if carline_found:
                    param['defval'] = carline_defval
                    if defval_isarray:
                            n = 2
                            hex_array = [(param['defval'][i:i+n]) for i in range(0, len(param['defval']), n)]
                            param['defval'] = hex_array            
                else:
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


                if not carline_found:
                    nocarline_params.append(param['name'])
                if param['name']:
                    params_all.append(param)

        miss_val_file = self.coding_file.strip('.xml') + '_' + car_line + '_UNDEFINED_PARAMS.txt'
        with open(miss_val_file, "w") as file:
            file.write(str(nocarline_params))

        return params_all


##############################################################################################
# Parse cafd coding .xml to get default values 
# - arg 1: coding.xml file path
# - arg 2: car line(ex: 'G070')
##############################################################################################
if __name__ == "__main__":
    coding = Coding(sys.argv[1])
    coding.parseCafex(sys.argv[2])