import os, time, subprocess

def test():
    print('update test')
    if os.name == 'posix':
        process = 'i3lock'

        ps_output = subprocess.check_output(['ps', '-ef'])
        ps_lines = ps_output.decode('utf-8').split('\n')

        for line in ps_lines:
            if process in line:
                return 1
                break
        else:
            return 0
    elif os.name == 'nt':
        process = 'LogonUI.exe'
        pid = False
        
        tasklist = str(subprocess.check_output('TASKLIST'))
        if process in tasklist:
            return 1
        else:
            return 0
            