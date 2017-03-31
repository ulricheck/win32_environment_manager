import mock
import time
from os import pathsep

MOCK_ENVIRONMENT = {
    "USER": {
        "Environment": {
            "PATH": pathsep.join(["one", "two", "three"]),
        },
    },
    "SYSTEM": {
        "Environment": {
            "PATH": pathsep.join(["one", "two", "three"]),
        },
    },
}


def env_keys(user=True):
    if user:
        root = "USER"
        subkey = 'Environment'
    else:
        root = "SYSTEM"
        subkey = 'Environment'
    return root, subkey


def get_key(name, user=True):
    root, subkey = env_keys(user)
    key = MOCK_ENVIRONMENT[root][subkey]
    time.sleep(0.2)
    return key[name]


def set_key(name, value):
    key = MOCK_ENVIRONMENT["USER"]['Environment']
    key[name] = value
    time.sleep(0.2)


def delete_key(name, user=True):
    key = MOCK_ENVIRONMENT["USER"]['Environment']
    del key[name]
    time.sleep(0.2)


def enum_keys(user=True):
    key = MOCK_ENVIRONMENT["USER"]['Environment']
    time.sleep(0.2)
    return key


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
    for value in values:
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
