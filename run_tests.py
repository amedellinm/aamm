import aamm.file_system as fs

for folder in fs.search("aamm"):
    for file in fs.files(folder):
        print(file)
