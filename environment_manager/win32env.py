from os import system, environ, pathsep
import win32con
from win32gui import SendMessage
from _winreg import (
    CloseKey, OpenKey, QueryValueEx, SetValueEx, DeleteValue, QueryInfoKey, EnumValue,
    HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE,
    KEY_ALL_ACCESS, KEY_READ, REG_EXPAND_SZ, REG_SZ
)


def env_keys(user=True):
    if user:
        root = HKEY_CURRENT_USER
        subkey = 'Environment'
    else:
        root = HKEY_LOCAL_MACHINE
        subkey = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
    return root, subkey


def get_key(name, user=True):
    root, subkey = env_keys(user)
    key = OpenKey(root, subkey, 0, KEY_READ)
    try:
        value, _ = QueryValueEx(key, name)
    except WindowsError:
        return ''
    return value


def set_key(name, value):
    key = OpenKey(HKEY_CURRENT_USER, 'Environment', 0, KEY_ALL_ACCESS)
    SetValueEx(key, name, 0, REG_EXPAND_SZ, value)
    CloseKey(key)
    SendMessage(
        win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')


def delete_key(name, user=True):
    key = OpenKey(HKEY_CURRENT_USER, 'Environment', 0, KEY_ALL_ACCESS)
    DeleteValue(key, name)
    CloseKey(key)
    SendMessage(
        win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')


def enum_keys(user=True):
    key = OpenKey(HKEY_CURRENT_USER, 'Environment', 0, KEY_ALL_ACCESS)
    _, n, _ = QueryInfoKey(key)
    values = {}
    for i in range(n):
        k, v, _ = EnumValue(key, i)
        values[k] = v
    return values


def remove(paths, value):
    while value in paths:
        paths.remove(value)


def unique(paths):
    unique = []
    for value in paths:
        if value not in unique:
            unique.append(value)
    return unique


def prepend_value(name, values):
    paths = get_key(name).split(pathsep)
    for value in reversed(values):
        remove(paths, '')
        paths = unique(paths)
        remove(paths, value)
        paths.insert(0, value)
    set_key(name, pathsep.join(paths))


def append_value(name, values):
    paths = get_key(name).split(pathsep)
    remove(paths, '')
    for value in values:
        paths = unique(paths)
        remove(paths, value)
        paths.append(value)
    set_key(name, pathsep.join(paths))


def remove_value(name, values):
    paths = get_key(name).split(pathsep)
    remove(paths, '')
    for value in values:
        paths = unique(paths)
        remove(paths, value)
    set_key(name, pathsep.join(paths))


def update_value(name, prepend_values=[], append_values=[], remove_values=[]):
    paths = get_key(name).split(pathsep)
    remove(paths, '')
    paths = unique(paths)

    #remove
    for value in remove_values:
        paths = unique(paths)
        remove(paths, value)
    #append
    for value in append_values:
        paths = unique(paths)
        remove(paths, value)
        paths.append(value)
    #prepend
    for value in prepend_values:
        remove(paths, value)
        paths.insert(0, value)

    set_key(name, pathsep.join(paths))
