import os
import os.path

output = open("tagalog_to_translate_final.txt", "a")



for dirpath, dirnames, filenames in os.walk("/Users/jamescarucci/Documents/GitLab/sphinx-ios/sphinx/"):
	for filename in [f for f in filenames if f.endswith(".strings")]:
		newPath = os.path.join(dirpath, filename)
		if("en.lproj" in newPath):
			print(newPath)
			output.write("\n\n" + "~~" + newPath + "~~" + "\n\n")
			f = open(newPath, "r")
			fileContents = f.read()
			print(fileContents)
			output.write(fileContents)
			print("-"*10)
			output.write("-"*10)

output.close()

