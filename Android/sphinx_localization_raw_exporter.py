import os
import os.path

#output = open("tagalog_to_translate_final.txt", "a")


for dirpath, dirnames, filenames in os.walk("/Users/jamescarucci/Documents/GitLab/sphinx-kotlin/sphinx/screens-detail/scanner/scanner/src"):
	#print('dirpath: ' + dirpath)
	#print('dirnames: ')
	#print(dirnames)
	print('filenames: ')
	print(filenames)
	for filename in [f for f in filenames if f.endswith("strings.xml")]:
		print('filename:')
		print(filename)
		newPath = os.path.join(dirpath, filename)
		#print(newPath)
		if("en.lproj" in newPath or True):
			print(newPath)
			#output.write("\n\n" + "~~" + newPath + "~~" + "\n\n")
			f = open(newPath, "r")
			fileContents = f.read()
			print(fileContents)
			#output.write(fileContents)
			print("-"*10)
			#output.write("-"*10)

#output.close()

