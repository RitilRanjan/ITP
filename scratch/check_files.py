import os

accidental_files = ['Created', 'Defined', 'Error', 'fold', 'intro', 'neg-']
for f in accidental_files:
    if os.path.exists(f):
        print(f"{f}: size {os.path.getsize(f)}, is_file {os.path.isfile(f)}")
