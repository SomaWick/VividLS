# VividLS - A Colored ls Replacement in Python 3

VividLS is a Python 3 script that mimics and enhances the behavior of the Unix `ls` command by adding color and icon support. The output is organized into neat columns in non‑long mode, or a detailed long format that features individually colored permission bits, user, group, and timestamp fields.

## Features

- **Colored Permissions:** Each permission character (`r`, `w`, `x`, `-`) is individually colored.
- **File Icons:** Uses [Nerd Font](https://www.nerdfonts.com/) icons to visually represent directories, symlinks, executables, and regular files.
- **Long Format Output:** With the `-l` option, displays detailed file information with custom-colored fields.
- **Column Layout:** Non‑long mode output is neatly organized into columns.
- **Customizable:** Easily adjust colors and icons by modifying the script.

## Requirements

- Python 3
- [colorama](https://pypi.org/project/colorama/) (Install with `pip install colorama`)

## Installation

1. **Download the Script:**

   Clone the repository or copy the `vividls.py` script to a directory of your choice.

2. **Make It Executable:**

   ```bash
   chmod +x vividls.py
   ```

## Usage

  Run the script with the desired options:

   ```bash
   ./vividls.py [directory] [options]
   ```

## Options

   - `-a, --all`    Include hidden files.
   - `-l, --long`    Use long listing format.
   - `-d, --dirs`    Show directories only.
   - `-f, --files`    Show files only.

### Examples:

  - List the current directory with icons and colors:
    ```bash
    ./vividls.py
    ```

  - List all files (including hidden) in long format:
    ```
    ./vividls.py -a -l
    ```

## Alias Setup

To make it easier to use VividLS as your default `ls` command, add an alias to your shell configuration file (e.g., `~/.bashrc` or `~/.zshrc`):
```bash
alias ls='/path/to/vividls.py'
```

Replace `/path/to/vividls.py` with the actual path to your script. After updating your shell configuration file, reload it:

```bash
source ~/.bashrc  # or source ~/.zshrc
```

Now, simply typing `ls` in your terminal will invoke VividLS.


## License

This project is licensed under the MIT License.
