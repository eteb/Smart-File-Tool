import argparse
import os
import shutil
import hashlib
from datetime import datetime
from collections import defaultdict
from tqdm import tqdm

# ---------------------------
# Utility Functions
# ---------------------------

def is_hidden(filepath):
    """Check if a file is hidden (cross-platform)."""
    name = os.path.basename(filepath)
    return name.startswith('.') or (os.name == 'nt' and has_hidden_attribute(filepath))

def has_hidden_attribute(filepath):
    """Check hidden attribute on Windows."""
    try:
        import ctypes
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(filepath))
        return attrs != -1 and (attrs & 2)
    except Exception:
        return False

def get_files(folder, skip_hidden=True):
    """Yield all file paths in a folder, optionally skipping hidden files."""
    for root, _, files in os.walk(folder):
        for filename in files:
            path = os.path.join(root, filename)
            if skip_hidden and is_hidden(path):
                continue
            yield path

# ---------------------------
# Organize Functions
# ---------------------------

def organize_by_type(folder, dry_run=False, skip_hidden=True):
    """Organize files into subfolders by file extension."""
    for path in get_files(folder, skip_hidden):
        ext = os.path.splitext(path)[1][1:] or 'no_ext'
        target_dir = os.path.join(folder, ext)
        os.makedirs(target_dir, exist_ok=True)
        target = os.path.join(target_dir, os.path.basename(path))
        if path == target:
            continue
        print(f"{'[DRY RUN] ' if dry_run else ''}Move {path} -> {target}")
        if not dry_run:
            shutil.move(path, target)

def organize_by_date(folder, dry_run=False, skip_hidden=True):
    """Organize files into subfolders by modification date (YYYY-MM)."""
    for path in get_files(folder, skip_hidden):
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        subfolder = mtime.strftime('%Y-%m')
        target_dir = os.path.join(folder, subfolder)
        os.makedirs(target_dir, exist_ok=True)
        target = os.path.join(target_dir, os.path.basename(path))
        if path == target:
            continue
        print(f"{'[DRY RUN] ' if dry_run else ''}Move {path} -> {target}")
        if not dry_run:
            shutil.move(path, target)

# ---------------------------
# Duplicate Detection Functions
# ---------------------------

def sha256sum(filename, blocksize=65536):
    """Calculate SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(blocksize), b''):
            h.update(chunk)
    return h.hexdigest()

def find_duplicates(folder, method='checksum', skip_hidden=True):
    """
    Find duplicate files in a folder.
    method: 'checksum' or 'name-size'
    Returns: list of lists of duplicate file paths.
    """
    files = list(get_files(folder, skip_hidden))
    dups = defaultdict(list)
    if method == 'name-size':
        for f in files:
            key = (os.path.basename(f), os.path.getsize(f))
            dups[key].append(f)
    elif method == 'checksum':
        for f in tqdm(files, desc="Hashing files"):
            try:
                key = sha256sum(f)
                dups[key].append(f)
            except Exception:
                continue
    else:
        raise ValueError("Unknown method")
    return [group for group in dups.values() if len(group) > 1]

def handle_duplicates(dups, action='delete', dry_run=False):
    """
    Handle duplicate files.
    action: 'delete', 'move', or 'copy'
    """
    for group in dups:
        keep = group[0]
        for dup in group[1:]:
            if action == 'delete':
                print(f"{'[DRY RUN] ' if dry_run else ''}Delete {dup}")
                if not dry_run:
                    os.remove(dup)
            elif action == 'move':
                target = keep + '.DUPLICATE'
                print(f"{'[DRY RUN] ' if dry_run else ''}Move {dup} -> {target}")
                if not dry_run:
                    shutil.move(dup, target)
            elif action == 'copy':
                target = keep + '.DUPLICATE'
                print(f"{'[DRY RUN] ' if dry_run else ''}Copy {dup} -> {target}")
                if not dry_run:
                    shutil.copy2(dup, target)

# ---------------------------
# Main CLI
# ---------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Smart File Tool: Organize and deduplicate folders."
    )
    parser.add_argument('--organize', type=str, help="Folder to organize")
    parser.add_argument('--by', choices=['type', 'date'], help="Organize by file type or modification date")
    parser.add_argument('--dedupe', type=str, help="Folder to deduplicate")
    parser.add_argument('--method', choices=['name-size', 'checksum'], default='checksum', help="Duplicate detection method")
    parser.add_argument('--action', choices=['delete', 'move', 'copy'], default='delete', help="Action for duplicates")
    parser.add_argument('--skip-hidden', action='store_true', help="Skip hidden/system files")
    parser.add_argument('--dry-run', action='store_true', help="Dry run (no changes)")
    args = parser.parse_args()

    if args.organize:
        if args.by == 'type':
            organize_by_type(args.organize, dry_run=args.dry_run, skip_hidden=args.skip_hidden)
        elif args.by == 'date':
            organize_by_date(args.organize, dry_run=args.dry_run, skip_hidden=args.skip_hidden)
        else:
            print("Please specify --by type or --by date with --organize")
    if args.dedupe:
        dups = find_duplicates(args.dedupe, method=args.method, skip_hidden=args.skip_hidden)
        if not dups:
            print("No duplicates found.")
        else:
            handle_duplicates(dups, action=args.action, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
