#!/usr/bin/env python
#!/usr/bin/env python
import glob
import inspect
import os
import getpass
import sys
import signal
from collections import defaultdict, OrderedDict

import keyring

from i3pystatus import Module, SettingsBase
from i3pystatus.core import ClassFinder


def signal_handler(signal, frame):
    sys.exit(0)


def get_int_in_range(prompt, _range):
    while True:
        try:
            answer = input(prompt)
        except EOFError:
            print()
            sys.exit(0)
        try:
            n = int(answer.strip())
            if n in _range:
                return n
            else:
                print("Value out of range!")
        except ValueError:
            print("Invalid input!")

modules = [os.path.basename(m.replace('.py', ''))
           for m in glob.glob(os.path.join(os.path.dirname(__file__), "i3pystatus", "*.py"))
           if not os.path.basename(m).startswith('_')]


def enumerate_choices(choices):
    lines = []
    for index, choice in enumerate(choices, start=1):
        lines.append(" %d - %s\n" % (index, choice))
    return "".join(lines)


protected_settings = SettingsBase._SettingsBase__PROTECTED_SETTINGS
class_finder = ClassFinder(Module)
credential_modules = defaultdict(dict)
for module_name in modules:
    try:
        module = class_finder.get_module(module_name)
        clazz = class_finder.get_class(module)
        members = [m[0] for m in inspect.getmembers(clazz) if not m[0].startswith('_')]
        if any([hasattr(clazz, setting) for setting in protected_settings]):
            credential_modules[clazz.__name__]['credentials'] = list(set(protected_settings) & set(members))
            credential_modules[clazz.__name__]['key'] = "%s.%s" % (clazz.__module__, clazz.__name__)
        elif hasattr(clazz, 'required'):
            protected = []
            required = getattr(clazz, 'required')
            for setting in protected_settings:
                if setting in required:
                    protected.append(setting)
            if protected:
                credential_modules[clazz.__name__]['credentials'] = protected
                credential_modules[clazz.__name__]['key'] = "%s.%s" % (clazz.__module__, clazz.__name__)

    except ImportError:
        continue


def main():
    signal.signal(signal.SIGINT, signal_handler)

    print("""%s - part of i3pystatus
This allows you to edit keyring-protected settings of
i3pystatus modules, which are stored globally (independent
of your i3pystatus configuration) in your keyring.
""" % os.path.baename(sys.argv[0]))

    choices = list(credential_modules.keys())
    prompt = "Choose a module to edit:\n"
    prompt += enumerate_choices(choices)
    prompt += "> "

    index = get_int_in_range(prompt, range(1, len(choices) + 1))
    module_name = choices[index - 1]
    module = credential_modules[module_name]

    prompt = "Choose setting of %s to edit:\n" % module_name
    prompt += enumerate_choices(module["credentials"])
    prompt += "> "

    choices = module['credentials']
    index = get_int_in_range(prompt, range(1, len(choices) + 1))
    setting = choices[index - 1]

    answer = getpass.getpass("Enter value for %s:\n> " % setting)
    answer2 = getpass.getpass("Re-enter value\n> ")
    if answer == answer2:
        key = "%s.%s" % (module['key'], setting)
        keyring.set_password(key, getpass.getuser(), answer)
        print("%s set!" % setting)
    else:
        print("Values don't match - nothing set.")

if __name__ == "__main__":
    main()