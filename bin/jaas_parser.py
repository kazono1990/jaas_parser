#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import sys


def usage():
    print ('Usage: python %s <PATH_TO_JAAS_FILE>' % os.path.basename(__file__))
    sys.exit(1)

def getConf(jaas_conf_path):
    checkFile(jaas_conf_path)
    formatted_body = reformat(jaas_conf_path)
    mode = 'out'
    confs = {}
    entry_name = ''
    entry_body = {}
    for line in formatted_body:
        stripped = line.strip()
        if (len(stripped) > 0):
            if (mode == 'out'):
                if (stripped.endswith('{')):
                    entry_name = re.sub('\s+{', '', stripped)
                    mode = 'in'
                    entry_body = {}
            else:
                if (stripped == '};'):
                    if (entry_name != ''):
                        confs[entry_name] = entry_body
                        entry_name = ''
                        mode = 'out'
                    else:
                        raise Exception('Can not find entry name for closing bracket:' + stripped)
                else:
                    (module_name, setting) = getModuleSetting(stripped)
                    entry_body[module_name] = setting
    return confs


def checkFile(filePath):
    if not (os.path.exists(filePath)):
        raise Exception('File is not there:' + filePath)

    if not os.access(filePath, os.R_OK):
        raise Exception('File is not readable:' + filePath)


def reformat(filePath):
    file = open(filePath, 'r')
    body = file.read()
    file.close()
    remove_line_comment = re.sub('//.*\n', '', body)
    delete_return = re.sub('\n', ' ', remove_line_comment)
    remove_block_comment = re.sub('(/\*.*\*/)?', '', delete_return)
    add_return_after_bracket = re.sub('{', '{\n', remove_block_comment)
    add_return_after_semicolon = re.sub(';', ';\n', add_return_after_bracket)
    return add_return_after_semicolon.split('\n')


def getModuleSetting(str):
    if not (str.endswith(';')):
        raise Exception('Setting for module must end with semicolon:' + str)
    else:
        module = ''
        flag = ''
        setting = {}
        options = {}
        type = 'module'
        space_replaced = re.sub('\"(.*?)\"', replaceSpace, str)
        splitBySpace = space_replaced.split(' ')
        for clause in splitBySpace:
            stripped = (re.sub('__SPACE__', ' ', clause)).strip(';')
            if (len(stripped) > 0):
                if (type == 'module'):
                    module = stripped
                    type = 'flag'
                elif (type == 'flag'):
                    flag = stripped
                    type = 'options'
                else:
                    firstEqual = stripped.find('=')
                    if (firstEqual > 0 and firstEqual < len(stripped)-1):
                        optionKey = stripped[0:firstEqual]
                        optionValue = stripped[firstEqual+1:len(stripped)]
                        if optionValue.startswith('"') and optionValue.endswith('"'):
                            optionValue = optionValue[1:-1]
                        options[optionKey.strip()] = optionValue
                    else:
                        raise Exception('Description for option need to be "xxx=yyy": ' + stripped)
        setting['module'] = module
        setting['flag'] = flag
        setting['options'] = options
        return (module ,setting)


def replaceSpace(matchobj):
    return re.sub('\s', '__SPACE__', matchobj.group(0))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()

    path_to_jaas = sys.argv[1]
    print getConf(path_to_jaas)
