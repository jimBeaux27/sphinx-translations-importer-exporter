import os
import os.path

input = open("./Filipino Localization - Raw Data.txt", "r")

inputContents = input.read()
#print(inputContents)

fileDelimiter = "----------"

fileData = inputContents.split(fileDelimiter)
fileNameDelimiter = "~~"
errorList = []

for file in fileData:
	filePath = file.split(fileNameDelimiter)[1].replace("en.lproj","fil.lproj")
	try:
		print("filePath: " + filePath)
		fileContents = file.split(fileNameDelimiter)[2]
		f = open(filePath, "w")
		#print(f.read())
		f.write(fileContents)
		f.close()
	except:
		print("Error trying to get into: " + filePath)
		errorList.append(filePath)

print("errorList: ")
print(errorList)