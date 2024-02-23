import os, time, subprocess

def test():
    global rslt
    if os.name == 'posix':
        process = 'i3lock'

        ps_output = subprocess.check_output(['ps', '-ef'])
        ps_lines = ps_output.decode('utf-8').split('\n')

        for line in ps_lines:
            if process in line:
                return True
                break
        else:
            return False
    elif os.name == 'nt':
        process = 'LogonUI.exe'
        pid = False
        
        # tasklist = str(subprocess.check_output('TASKLIST', shell=True))
        # tasklist = subprocess.Popen(['TASKLIST'],
        #                             stdout=subprocess.PIPE,
        #                             creationflags=subprocess.CREATE_NO_WINDOW
        #                             ).communicate()[0].decode('latin-1').strip()

        tasklist = str(subprocess.check_output('TASKLIST',shell=True))
        
        if process in tasklist:
            return True
        else:
            return False

