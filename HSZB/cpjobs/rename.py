import os
dir_root = 'json_data2'

for file in os.listdir(dir_root):
    os.rename(dir_root + '/' + file, dir_root + '/' + dir_root + file)