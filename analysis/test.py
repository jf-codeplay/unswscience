import re
name = "Fan Jiaxin)"

name = re.sub("[^a-zA-Z]+", "", name)
print(name)