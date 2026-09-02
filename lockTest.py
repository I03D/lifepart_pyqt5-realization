import os, subprocess, ctypes
import ctypes.wintypes as w

def test():
    if os.name == 'posix':
        process = 'i3lock'
        ps_output = subprocess.check_output(['ps', '-ef']).decode('utf-8')
        return process in ps_output

    elif os.name == 'nt':
        DESKTOP_READOBJECTS = 0x0001
        UOI_NAME = 2

        user32 = ctypes.WinDLL('user32')

        user32.OpenInputDesktop.restype = ctypes.c_void_p
        user32.OpenInputDesktop.argtypes = [w.DWORD, w.BOOL, w.DWORD]

        user32.GetUserObjectInformationW.restype = w.BOOL
        user32.GetUserObjectInformationW.argtypes = [ctypes.c_void_p, w.UINT, ctypes.c_void_p, w.DWORD, ctypes.POINTER(w.DWORD)]

        user32.CloseDesktop.argtypes = [ctypes.c_void_p]

        hDesktop = user32.OpenInputDesktop(0, False, DESKTOP_READOBJECTS)
        if not hDesktop:
            # OpenInputDesktop вернул NULL: активен десктоп Winlogon,
            # но доступ к нему есть только у SYSTEM.
            # Запасной вариант — проверить процесс LogonUI.exe,
            # который запущен, пока экран заблокирован (Win+L).
            try:
                output = subprocess.check_output(
                    ['tasklist', '/FI', 'IMAGENAME eq LogonUI.exe', '/NH'],
                    stderr=subprocess.DEVNULL,
                ).decode('utf-8', errors='ignore')
                return 'LogonUI.exe' in output
            except Exception:
                return False

        buf = ctypes.create_unicode_buffer(256)
        size = w.DWORD()

        result = user32.GetUserObjectInformationW(
            hDesktop, UOI_NAME, buf, ctypes.sizeof(buf), ctypes.byref(size)
        )
        user32.CloseDesktop(hDesktop)

        if result:
            return buf.value == 'Winlogon'

        return False

    return False

