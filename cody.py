import os
import logging
from collections import defaultdict
import click
from rich import print, inspect
from rich.console import Console
from rich.logging import RichHandler


nested_dict = None
nested_dict = lambda: defaultdict(nested_dict)  # type: ignore # noqa E731

console = Console()


def find_files(root, file_ext):
    spec_files = []
    for top, dirs, files in os.walk(root):
        for dir in dirs:
            #Ignore any hidden folders
            if dir.startswith('.'):
                dirs.remove(dir)
        for f in files:
            filename, ext = os.path.splitext(f)
            if ext == file_ext:
                spec_files.append(os.path.join(top, f))
    
    return spec_files

def extract_config(root, file_ext):
    cfg_files = find_files(root, file_ext)

    if cfg_files is None:
        return None

    cfg_combined = nested_dict()

    for cf in cfg_files:
        local_cfg = nested_dict()
        with open(cf, "rb") as file:
            exec(compile(file.read(), cf, "exec"), {}, {"cfg": local_cfg})

        cfg_combined[cf] = local_cfg

    return cfg_combined


def compilable_files(cfg):
    c_files = []
    asm_files = []

    for k, v in cfg.items():
        full_path = os.path.realpath(k)
        print(full_path)
        if len(v) > 0:
            lcl_src_c = v["src"]["c"]
            lcl_src_asm = v["src"]["asm"]
            if lcl_src_c is not None:
                for src_c in lcl_src_c:
                    c_files.append(os.path.dirname(full_path)+"/"+src_c)

            if lcl_src_asm is not None:
                for src_asm in lcl_src_asm:
                    asm_files.append(os.path.dirname(full_path)+"/"+src_asm)

    return {"src_c":c_files, "src_asm":asm_files}


def flags_gcc(cfg):
    c_files = []
    asm_files = []

    for k, v in cfg.items():
        if len(v) > 0:
            lcl_src_c = v["src"]["c"]
            lcl_src_asm = v["src"]["asm"]
            if lcl_src_c is not None:
                for src_c in lcl_src_c:
                    c_files.append(os.path.dirname(k)+"/"+src_c)

            if lcl_src_asm is not None:
                for src_asm in lcl_src_asm:
                    asm_files.append(os.path.dirname(k)+"/"+src_asm)

    return {"src_c":c_files, "src_asm":asm_files}


@click.group()
def cli():
    pass


@cli.command()
@click.argument("root", type=click.Path(exists=True), nargs=1)
@click.argument("out", type=click.Path(exists=False), nargs=1)
def makefile(root, out):
    if not os.path.isdir(root):
        console.print("ROOT must be a directory", style="bold red")
        return

    cfg_dict = extract_config(root, ".cdy")
    if cfg_dict is None:
        console.print("No cfg files found", style="bold red")
        return
    
    print("-D-***************  cfg['parameters'] **********")
    for k, v in cfg_dict.items():
        print(f" param {k} = {v}")
        print()
        if len(v) > 0:
            lcl_src_c = v["src"]
            if lcl_src_c is not None:
                print(lcl_src_c)

    print("-D-*********************************************")

    inc_c = []
    c_n_asm_files = compilable_files(cfg_dict)

    with open(out, "w+") as f:
        f.write("CC\t\t:= gcc\n")
        f.write("PRJ\t\t:= {}\n".format("test.elf"))
        f.write("\n{}\t\t:= {}\n".format("INC_C", " -I".join(inc_c)))
        f.write("\n{}\t\t:= {}\n".format("SRC_C", " ".join(c_n_asm_files["src_c"])))
        f.write("\n{}\t\t:= {}\n\n\n\n".format("OBJS", "$(SRC_C:.c=.o)"))

        f.write(".c.o:\n\t$(CC) -c ${CFLAGS} ${INC_C} $< -o $@")

        f.write("\n\nall: $(OBJS)\n\t $(CC) ${LDFLAGS} ${INC_LIB} -o $(PRJ) ${OBJS} ${LIBS}")
        f.write("\nclean:\n\t rm -rf $(PRJ) $(OBJS)")


def main():
    cli()


if __name__ == "__main__":
    main()