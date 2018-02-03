import json
import os
# dir_root = input("Input root directory: ")
dir_root = 'json_data2'
f = open('total.json', 'w')

print('[', file=f)
for file in os.listdir(dir_root):
    json_file = open(dir_root + '/' + file, 'r')
    temp = json_file.readlines()[1:-1]
    f.writelines(temp)
print(']', file=f)
f.close()