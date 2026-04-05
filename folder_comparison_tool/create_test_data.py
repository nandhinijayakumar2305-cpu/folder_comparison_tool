import os

# Folders create
os.makedirs("test_folder1", exist_ok=True)
os.makedirs("test_folder2", exist_ok=True)

# 1. Unchanged file (rendu folderlaiyum same)
with open("test_folder1/readme.txt", "w") as f:
    f.write("This is the readme file. No changes here.")
with open("test_folder2/readme.txt", "w") as f:
    f.write("This is the readme file. No changes here.")

# 2. Modified file (content different)
with open("test_folder1/config.txt", "w") as f:
    f.write("version=1.0\nenv=staging\ndebug=true")
with open("test_folder2/config.txt", "w") as f:
    f.write("version=2.0\nenv=production\ndebug=false")

# 3. Deleted file (only in folder1)
with open("test_folder1/old_script.py", "w") as f:
    f.write("# This file will be deleted in v2")

# 4. New file (only in folder2)
with open("test_folder2/new_feature.py", "w") as f:
    f.write("# New feature added in v2")

# 5. Renamed file (same content, different name)
with open("test_folder1/utils_old.py", "w") as f:
    f.write("def helper(): pass")
with open("test_folder2/utils_new.py", "w") as f:
    f.write("def helper(): pass")

print("✅ Test folders ready!")
print("Folder 1:", os.listdir("test_folder1"))
print("Folder 2:", os.listdir("test_folder2"))