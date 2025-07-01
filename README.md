# Smart File Tool

A simple but powerful Python CLI tool to help you clean up folders by:

- 📁 Organizing files by type (extension) or modification date.
- 🧹 Detecting and removing duplicate files based on name, size, or checksum (SHA256).

## Features

- **Organize files** into subfolders by:
  - File type/extension (e.g., `.jpg`, `.pdf`)
  - File modification date (e.g., `2025-07`)
- **Detect duplicate files** using:
  - Filename & size
  - SHA256 checksum
- **Options to:**
  - Move, copy, or delete duplicates
  - Skip hidden/system files
  - Dry-run mode (no actual changes)

## Requirements

- Python 3.x
- Works on Windows, macOS, and Linux

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Organize a folder:

```bash
python smartfiletool.py --organize /path/to/folder --by type
python smartfiletool.py --organize /path/to/folder --by date
```

Find duplicates:

```bash
python smartfiletool.py --dedupe /path/to/folder --method checksum
python smartfiletool.py --dedupe /path/to/folder --method name-size
```

Combine both:

```bash
python smartfiletool.py --organize /path/to/folder --by type --dedupe /path/to/folder
```


## Options

- `--organize FOLDER` : Folder to organize
- `--by [type|date]` : Organize by file type or modification date
- `--dedupe FOLDER` : Folder to deduplicate
- `--method [name-size|checksum]` : Duplicate detection method
- `--action [delete|move|copy]` : Action for duplicates (default: delete)
- `--skip-hidden` : Skip hidden/system files
- `--dry-run` : Dry run (no changes)

---

**Enjoy a cleaner, smarter folder!**

---

GitHub: [https://github.com/eteb](https://github.com/eteb)
