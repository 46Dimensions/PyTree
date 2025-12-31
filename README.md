# PyTree

A Python version of the `tree` command.
Shows the files in the current directory in a tree-like format.

## How to use

In the directory where `main.py` is stored, run:

``` shell
python main.py [flags] [directory]
```

where

- `[directory]` is the path to the directory which you want to list and `[flags]` is one or none of the flags below.
- `[flags]` is any of the flags listed below. `[flags]` is optional.

### Flags

In addition to `[directory]`, these flags can be used:

- `-r` or `--recursive`: Shows files in subdirectories
- `-h` or `--help`: Shows a help page
- `-o [filename]` or `--output [filename]`: Writes the tree to the file `[filename]`

### Listing the current directory
To list the current directory, set `[directory]` to `.`
