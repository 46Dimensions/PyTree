import argparse
import stat
import time
import os

START = time.perf_counter()

parser = argparse.ArgumentParser()
parser.add_argument("directory", type=str, help="Path to be used by TreeList (treels)")
parser.add_argument("-o", "--output", type=str, help="Output file path", default=None)
parser.add_argument("-r", "--recursive", action="store_true", help="Search subdirectories")
parser.add_argument("-a", "--all", action="store_true", help="Show files starting with .")

args = parser.parse_args()
start_dir = args.directory
output_file = args.output
recursive = args.recursive
use_colours = output_file is None

dirs_searched = 0
skipped = 0
files_found = 0
dirs_found = 0

# Setup of directory tree characters
BRANCH = "├──"
FINAL_BRANCH = "└──"
VERTICAL_LINE = "│"
HORIZONTAL_LINE = "─"

# ANSI color codes (similar to ls)
class Colours:
    if use_colours:
        RESET = "\033[0m"        # Reset the colours
        BLUE = "\033[1;94m"      # Directories
        GREEN = "\033[92m"       # Executables
        CYAN = "\033[96m"        # Symlinks
        RED = "\033[1;91m"       # Archives
        YELLOW = "\033[93m"      # Special files
        MAGENTA = "\033[1;95m"   # Images
        WHITE = ""               # Default - works in white-background terminals
    else:
        # No colours if colours are disabled
        RESET = ""
        BLUE = ""
        GREEN = ""
        CYAN = ""
        RED = ""
        YELLOW = ""
        MAGENTA = ""
        WHITE = ""

def get_color_for_path(path: str) -> str:
    """Determine color based on file type."""
    if not use_colours:
        return ""
    
    try:
        if os.path.islink(path):
            # Check if symlink is broken
            if os.path.exists(path):
                return Colours.CYAN  # Valid symlink
            else:
                return Colours.RED   # Broken symlink
        elif os.path.isdir(path):
            return Colours.BLUE     # Directory
        else:
            # Check if executable
            st = os.stat(path)
            if st.st_mode & stat.S_IXUSR:
                return Colours.GREEN  # Executable
            # Check file extension for archives/images
            ext = os.path.splitext(path)[1].lower()
            if ext in ['.zip', '.tar', '.gz', '.bz2', '.rar', '.7z']:
                return Colours.RED    # Archive
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
                return Colours.MAGENTA  # Image
            else:
                return Colours.WHITE  # Regular file
    except Exception:
        return Colours.WHITE if use_colours else ""

def add_dir(dir: str, tree: dict|None = None, return_dirs: bool = False) -> tuple[dict, list]|dict:
    global dirs_searched, skipped, files_found, dirs_found
    if tree is None:
        tree = {}

    try:
        entries = os.scandir(dir)
    except Exception:
        # Skip this directory if we can't read it
        skipped += 1
        return tree, [] if return_dirs else []

    files = []
    dirs = []

    for entry in entries:
        try:
            if entry.is_file(follow_symlinks=False):
                files.append(entry.path)
                files_found += 1
            elif entry.is_dir(follow_symlinks=False):
                dirs.append(entry.path)
                dirs_found += 1
        except Exception:
            # Skip items we can't access
            skipped += 1
            continue

    tree[dir] = files
    for d in dirs:
        tree[d] = []


    if return_dirs:
        return tree, dirs
    else:
        return tree

def add_all_dirs(start_dir: str, tree: dict|None = None) -> dict:
    global dirs_searched
    if tree is None:
        tree = {}
    dirs = [start_dir]
    processed_count = 0
    while dirs:
        new_dirs = []
        for dir in dirs:
            tree, subdirs = add_dir(dir, tree, return_dirs=True)
            new_dirs.extend(subdirs)
            processed_count += 1
        dirs = new_dirs
    
    dirs_searched = processed_count
    return tree

if recursive:
    tree = add_all_dirs(start_dir)
else:
    tree = add_dir(start_dir, return_dirs=False)
    dirs_searched += 1

def dict_to_list(tree: dict) -> list[str]:
    paths = []

    for dir_path, files in tree.items():
        paths.append(dir_path)

        for file in files:
            paths.append(file)

    return paths

def format_tree(paths: list[str]) -> str:
    paths = sorted(paths)
    
    # Find the common root (the starting directory)
    root = paths[0] if paths else ""
    
    tree = {}

    for path in paths:
        if path == root:
            # Root entry
            tree[root] = {}
        else:
            # Remove the root prefix to get relative path
            relative_path = path[len(root):].lstrip('/')
            if not relative_path:
                continue
                
            parts = relative_path.split('/')
            current = tree.setdefault(root, {})
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            # Add leaf
            if parts:
                current[parts[-1]] = {}

    def build_lines(node: dict, prefix: str = "", is_last: bool = True, parent_path: str = ""):
        lines = []
        items = sorted(node.items())
        for i, (name, children) in enumerate(items):
            is_last_item = i == (len(items) - 1)
            connector = FINAL_BRANCH if is_last_item else BRANCH
            
            # Build full path for color determination
            full_path = os.path.join(parent_path, name)
            color = get_color_for_path(full_path)
            colored_name = f"{color}{name}{Colours.RESET}"
            
            lines.append(prefix + connector + colored_name)

            extension = "    " if is_last_item else "│   "
            lines.extend(build_lines(children, prefix + extension, is_last_item, full_path))
        
        return lines
    
    lines = []
    # Add root without connector
    for root_path, children in tree.items():
        color = get_color_for_path(root_path)
        colored_root = f"{color}{root_path}{Colours.RESET}"
        lines.append(colored_root)
        
        children = dict(children)
        sorted_children = sorted(children.items())
        for idx, (name, subtree) in enumerate(sorted_children):
            is_last = idx == (len(sorted_children) - 1)
            full_path = os.path.join(root_path, name)
            color = get_color_for_path(full_path)
            colored_name = f"{color}{name}{Colours.RESET}"
            
            connector = FINAL_BRANCH if is_last else BRANCH
            lines.append("   " + connector + colored_name)
            extension = "       " if is_last else "│      "
            lines.extend(build_lines(subtree, "   " + extension, is_last, full_path))
    
    return "\n".join(lines)

def print_summary():
    global skipped, dirs_searched, files_found, dirs_found
    print("")
    total_time = time.perf_counter() - START
    print(f"Searched {dirs_searched} directories in {total_time:.5f} seconds.")
    if skipped > 0:
        print(f"Skipped {skipped} files & directories ({dirs_searched / (dirs_searched + skipped) * 100:.2f}% success rate).")
    print(f"Found {files_found} files and {dirs_found} directories.")

tree_list = dict_to_list(tree) # type: ignore
formatted_tree = format_tree(tree_list)

if output_file:
    with open(output_file, 'w') as f:
        f.seek(0)
        f.truncate()
        f.write(formatted_tree)
    print(f"View output in {output_file}.")
else:
    print(formatted_tree)

print_summary()