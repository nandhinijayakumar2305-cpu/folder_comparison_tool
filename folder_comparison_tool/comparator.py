import os
import hashlib
from pathlib import Path


def get_file_hash(filepath):
    """SHA-256 hash for a file"""
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None


def scan_folder(folder_path):
    """Scan folder recursively, return dict of {relative_path: full_path}"""
    files = {}
    folder = Path(folder_path)
    for file in folder.rglob("*"):
        if file.is_file():
            relative = str(file.relative_to(folder))
            files[relative] = str(file)
    return files


def compare_folders(folder1, folder2):
    """Main comparison function"""
    files1 = scan_folder(folder1)
    files2 = scan_folder(folder2)

    set1 = set(files1.keys())
    set2 = set(files2.keys())

    # New files (in folder2 but not folder1)
    new_files = sorted(set2 - set1)

    # Deleted files (in folder1 but not folder2)
    deleted_files = sorted(set1 - set2)

    # Common files — check if modified
    common_files = set1 & set2
    modified_files = []
    unchanged_files = []

    for file in sorted(common_files):
        hash1 = get_file_hash(files1[file])
        hash2 = get_file_hash(files2[file])
        if hash1 != hash2:
            modified_files.append(file)
        else:
            unchanged_files.append(file)

    # Duplicate / renamed file detection
    # Build hash→filename map for folder1
    hash_to_file1 = {}
    for rel, full in files1.items():
        h = get_file_hash(full)
        if h:
            hash_to_file1[h] = rel

    renamed_files = []
    for rel2, full2 in files2.items():
        if rel2 in new_files:  # only check new files
            h2 = get_file_hash(full2)
            if h2 and h2 in hash_to_file1:
                renamed_files.append({
                    "original": hash_to_file1[h2],
                    "renamed_to": rel2
                })

    return {
        "new": new_files,
        "deleted": deleted_files,
        "modified": modified_files,
        "unchanged": unchanged_files,
        "renamed": renamed_files,
        "total_folder1": len(files1),
        "total_folder2": len(files2),
    }