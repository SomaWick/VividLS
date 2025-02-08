#!/usr/bin/env python3
"""
vividls - A Colored ls Replacement in Python3

vividls mimics and enhances the behavior of the Unix `ls` command by adding color and icon support.
It supports both a column-organized view (non‑long mode) and a detailed long listing with individually
colored permission bits, user, group, and timestamp fields.
"""

import os
import sys
import stat
import argparse
import pwd
import grp
import time
import shutil
import math
from colorama import init, Fore, Style

# Initialize colorama for ANSI color codes
init(autoreset=True)

# Colors for individual permission characters.
PERM_COLOR_MAP = {
    'd': Fore.BLUE,          # directory
    'l': Fore.CYAN,          # symlink
    'r': Fore.RED,           # read
    'w': Fore.YELLOW,        # write
    'x': Fore.GREEN,         # execute
    '-': Fore.LIGHTBLACK_EX, # no permission
    'c': Fore.MAGENTA,       # character device
    'b': Fore.MAGENTA,       # block device
    'p': Fore.MAGENTA,       # FIFO/pipe
    's': Fore.MAGENTA        # socket
}

# Colors for other long-format fields:
USER_COLOR  = Fore.LIGHTBLUE_EX    # user name
GROUP_COLOR = Fore.LIGHTGREEN_EX   # group name
TIME_COLOR  = Fore.LIGHTMAGENTA_EX # modification time

def file_mode(mode):
    """
    Return a string representing the file permissions (like ls -l).
    """
    perms = ['-' for _ in range(10)]
    if stat.S_ISDIR(mode):
        perms[0] = 'd'
    elif stat.S_ISLNK(mode):
        perms[0] = 'l'
    elif stat.S_ISCHR(mode):
        perms[0] = 'c'
    elif stat.S_ISBLK(mode):
        perms[0] = 'b'
    elif stat.S_ISFIFO(mode):
        perms[0] = 'p'
    elif stat.S_ISSOCK(mode):
        perms[0] = 's'

    perms[1] = 'r' if mode & stat.S_IRUSR else '-'
    perms[2] = 'w' if mode & stat.S_IWUSR else '-'
    perms[3] = 'x' if mode & stat.S_IXUSR else '-'
    perms[4] = 'r' if mode & stat.S_IRGRP else '-'
    perms[5] = 'w' if mode & stat.S_IWGRP else '-'
    perms[6] = 'x' if mode & stat.S_IXGRP else '-'
    perms[7] = 'r' if mode & stat.S_IROTH else '-'
    perms[8] = 'w' if mode & stat.S_IWOTH else '-'
    perms[9] = 'x' if mode & stat.S_IXOTH else '-'
    return ''.join(perms)

def colored_permissions(mode):
    """
    Return the permissions string with each character colored individually.
    """
    perm_str = file_mode(mode)
    colored = []
    for ch in perm_str:
        color = PERM_COLOR_MAP.get(ch, '')
        colored.append(f"{color}{ch}{Style.RESET_ALL}")
    return ''.join(colored)

def human_readable_size(size):
    """
    Convert a size in bytes to a human-readable format.
    """
    for unit in ['B','K','M','G','T','P']:
        if size < 1024:
            return f"{size}{unit}"
        size //= 1024
    return f"{size}E"

def get_icon_and_color(path, mode):
    """
    Return a tuple (icon, color) based on file type.

    Uses Unicode code points (assumes a Nerd Font is active):
      - Directory:  (U+F115) in blue
      - Symlink:  (U+F0C1) in cyan
      - Executable:  (U+F013) in green
      - Regular file:  (U+F15B) in white
    """
    if stat.S_ISDIR(mode):
        return ("\uf115", Fore.BLUE)
    elif stat.S_ISLNK(mode):
        return ("\uf0c1", Fore.CYAN)
    elif os.access(path, os.X_OK) and not stat.S_ISDIR(mode):
        return ("\uf013", Fore.GREEN)
    else:
        return ("\uf15b", Fore.WHITE)

def print_in_columns(formatted_items, column_gap=2):
    """
    Print the list of formatted items in columns.

    Each item is a tuple (plain, formatted) where 'plain' is the text
    without ANSI codes (for calculating width) and 'formatted' includes color.
    """
    if not formatted_items:
        return
    max_length = max(len(plain) for plain, _ in formatted_items)
    try:
        terminal_width = shutil.get_terminal_size().columns
    except Exception:
        terminal_width = 80
    columns = max(1, terminal_width // (max_length + column_gap))
    rows = math.ceil(len(formatted_items) / columns)
    for row in range(rows):
        for col in range(columns):
            idx = col * rows + row
            if idx < len(formatted_items):
                plain, formatted = formatted_items[idx]
                print(formatted + " " * (max_length - len(plain) + column_gap), end='')
        print()

def list_directory(directory, show_all, long_format, show_dirs_only, show_files_only):
    try:
        entries = os.listdir(directory)
    except Exception as e:
        print(f"Error listing directory {directory}: {e}")
        sys.exit(1)

    if not show_all:
        entries = [e for e in entries if not e.startswith('.')]
    entries.sort()

    if long_format:
        for entry in entries:
            full_path = os.path.join(directory, entry)
            try:
                st = os.lstat(full_path)
            except Exception as e:
                print(f"Error stating {full_path}: {e}")
                continue

            if show_dirs_only and not stat.S_ISDIR(st.st_mode):
                continue
            if show_files_only and stat.S_ISDIR(st.st_mode):
                continue

            # Get colored permissions.
            perms_str = colored_permissions(st.st_mode)
            nlink = st.st_nlink
            try:
                user = pwd.getpwuid(st.st_uid).pw_name
            except KeyError:
                user = st.st_uid
            try:
                group = grp.getgrgid(st.st_gid).gr_name
            except KeyError:
                group = st.st_gid
            size = human_readable_size(st.st_size)
            mtime = time.strftime("%b %d %H:%M", time.localtime(st.st_mtime))

            # Color user, group, and time fields.
            user_str  = f"{USER_COLOR}{user:<8}{Style.RESET_ALL}"
            group_str = f"{GROUP_COLOR}{group:<8}{Style.RESET_ALL}"
            time_str  = f"{TIME_COLOR}{mtime}{Style.RESET_ALL}"

            # Get the icon and its color.
            icon, icon_color = get_icon_and_color(full_path, st.st_mode)
            # Use the same color for both the icon and the file/directory name.
            name_str = f"{icon_color}{entry}{Style.RESET_ALL}"
            print(f"{perms_str} {nlink:3} {user_str} {group_str} {size:8} {time_str} {icon_color}{icon} {name_str}")
    else:
        # Non-long mode: gather items for column layout.
        items = []
        for entry in entries:
            full_path = os.path.join(directory, entry)
            try:
                st = os.lstat(full_path)
            except Exception:
                continue

            if show_dirs_only and not stat.S_ISDIR(st.st_mode):
                continue
            if show_files_only and stat.S_ISDIR(st.st_mode):
                continue

            icon, icon_color = get_icon_and_color(full_path, st.st_mode)
            plain_text = f"{icon} {entry}"
            formatted_text = f"{icon_color}{icon} {entry}{Style.RESET_ALL}"
            items.append((plain_text, formatted_text))
        print_in_columns(items)

def main():
    parser = argparse.ArgumentParser(
        description="vividls - A colored ls replacement in Python3")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to list")
    parser.add_argument("-a", "--all", action="store_true", help="Include hidden files")
    parser.add_argument("-l", "--long", action="store_true", help="Long listing format")
    parser.add_argument("-d", "--dirs", action="store_true", help="Show directories only")
    parser.add_argument("-f", "--files", action="store_true", help="Show files only")
    args = parser.parse_args()

    list_directory(args.directory, args.all, args.long, args.dirs, args.files)

if __name__ == '__main__':
    main()
