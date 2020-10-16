import os
from typing import Any
from typing import Dict
from typing import Optional
from typing import cast
from collections import defaultdict


nested_dict = lambda: defaultdict(nested_dict)  # type: ignore # noqa E731

cfg = cast(Dict[str, Any], nested_dict())
cfg["name"] = "uart"
cfg["apbversion"] = 4


def find_spec_files(top):
    spec_files = []
    for top, dirs, files in os.walk('./'):
        for dir in dirs:
            if dir.startswith('.'):
                dirs.remove(dir)
        for f in files:
            filename, ext = os.path.splitext(f)
            if ext == ".cody":
                spec_files.append(os.path.join(top, f))
    
    return spec_files


def main():
    globals = {}
    locals = {}
    spec_files = find_spec_files('.')

    if globals is None:
        globals = {}
    if locals is None:
        locals = {}


    for sf in spec_files:
        print(sf)
        globals.update({"__file__": sf, "__name__": "__main__"})
        globals.update({"nested_dict": nested_dict})
        locals.update({"nested_dict": nested_dict})

        with open(sf, "rb") as file:
            exec(compile(file.read(), sf, "exec"), globals, locals)

        print("-------------------------------------")
        print(globals)
        print("#####################################")
        print(locals)
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(locals["tpl_ahb_master_address_phase_signals"])


if __name__ == "__main__":
    main()