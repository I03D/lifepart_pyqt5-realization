import os, time

def test():
    if os.name == 'posix':
        import subprocess
        process = 'i3lock'

        ps_output = subprocess.check_output(['ps', '-ef'])
        ps_lines = ps_output.decode('utf-8').split('\n')

        for line in ps_lines:
            if process in line:
                # print('running!!')
                return 1
                break
        else:
            # print('not running!')
            return 0
    elif os.name == 'nt':
        import psutil
        process = 'windows lock station (find right name)'
        pid = False

        for proc in psutil.process_iter():
            if process in proc.name().lower():
                pid = True
                break
            if pid:
                # print('found!!')
                return 1
            else:
                # print('not found!')
                return 0

