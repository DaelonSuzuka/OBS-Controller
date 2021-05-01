#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import json
from six.moves.urllib.request import urlopen
from collections import OrderedDict
from pathlib import Path

import_url = "https://raw.githubusercontent.com/Palakis/obs-websocket/4.x-current/docs/generated/comments.json"  # noqa: E501


def clean_var(string):
    """
    Converts a string to a suitable variable name by removing not allowed
    characters.
    """
    string = string.replace('-', '_').replace('[]', '')
    return string


def generate_classes():
    """Generates the necessary classes."""
    print("Downloading {} for last API version.".format(import_url))
    data = json.loads(urlopen(import_url).read().decode('utf-8'), object_pairs_hook=OrderedDict)
    print("Download OK. Generating python files...")

    classname = {
        'requests': 'BaseRequest',
        'events': 'BaseEvent',
    }

    for event in ['requests', 'events']:
        if event not in data:
            raise Exception("Missing {} in data.".format(event))
        with open(Path(__file__).parent / '{}.py'.format(event), 'w') as f:

            f.write(f"from .base_classes import {classname[event]}\n")
            f.write("\n\n")

            for sec in data[event]:
                if data[event][sec]['name'] == 'SetMute':
                    print(data[event][sec])

                continue
                for i in data[event][sec]:
                    f.write(f"class {i['name']}({classname[event]}):\n")
                    
                    f.write("    \"\"\"{}\n\n".format(i['description']))

                    arguments_default = []
                    arguments = []
                    try:
                        if len(i['params']) > 0:
                            f.write("    :Arguments:\n")
                            for a in i['params']:
                                a['name'] = a['name'].replace("[]", ".*")
                                f.write("       *{}*\n".format(clean_var(a['name'])))
                                f.write("            type: {}\n".format(a['type']))
                                f.write("            {}\n".format(a['description']))
                                name = a['name'].split(".")[0]
                                if name in arguments or name in arguments_default:
                                    continue
                                if 'optional' in a['type']:
                                    arguments_default.append(name)
                                else:
                                    arguments.append(name)
                    except KeyError:
                        pass

                    returns = []
                    try:
                        if len(i['returns']) > 0:
                            f.write("    :Returns:\n")
                            for r in i['returns']:
                                r['name'] = r['name'].replace("[]", ".*")
                                f.write("       *{}*\n".format(clean_var(r['name'])))
                                f.write("            type: {}\n".format(r['type']))
                                f.write("            {}\n".format(r['description']))
                                name = r['name'].split(".")[0]
                                if name in returns:
                                    continue
                                returns.append(name)
                    except KeyError:
                        pass

                    f.write("    \"\"\"\n\n")
                    f.write("    def __init__({}):\n".format(
                        ", ".join(
                            ["self"]
                            + [clean_var(a) for a in arguments]
                            + [clean_var(a) + "=None" for a in arguments_default]
                        )
                    ))
                    f.write("        Base{}.__init__(self)\n".format(event))
                    f.write("        self.name = '{}'\n".format(i['name']))
                    for r in returns:
                        f.write("        self.datain['{}'] = None\n".format(r))
                    for a in arguments:
                        f.write("        self.dataout['{}'] = {}\n".format(a, clean_var(a)))
                    for a in arguments_default:
                        f.write("        self.dataout['{}'] = {}\n".format(a, clean_var(a)))
                    f.write("\n")
                    for r in returns:
                        cc = "".join(x[0].upper() + x[1:] for x in r.split('-'))
                        f.write("    def get{}(self):\n".format(clean_var(cc)))
                        f.write("        return self.datain['{}']\n".format(r))
                        f.write("\n")
                    f.write("\n")

    print("API classes have been generated.")


if __name__ == '__main__':
    generate_classes()