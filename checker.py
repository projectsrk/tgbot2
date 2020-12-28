from os import listdir

TextFileList = []
PathInput = "accounts/"

# Count the number of different files you have!
for filename in listdir(PathInput):
    if filename.endswith(".json"): 
        TextFileList.append(filename)

for i in TextFileList:
    file = open(PathInput + i, 'r')
    content = file.readlines()
    file.close()

for i in content:
    if i.find("@") == 0:
        print(i)