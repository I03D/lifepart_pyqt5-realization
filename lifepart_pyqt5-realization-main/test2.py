import os

if os.name == 'posix':
    import subprocess
    process = 'lifepart'

    ps_output = subprocess.check_output(['ps', '-ef'])
    ps_lines = ps_output.decode('utf-8').split('\n')

    for line in ps_lines:
        if process in line:
            print('running!!')
            break
    else:
        print('not running!')
elif os.name == 'nt':
    import psutil
    process = 'lifepart.exe'
    pid = False

    for proc in psutil.process_iter():
        if process in proc.name().lower():
            pid = True
            break
        if pid:
            print('found!!')
        else:
            print('not found!')

