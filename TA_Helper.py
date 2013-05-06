#/bin/python
import os
import smtplib  

################################ Configuration  ################################
fromaddr = 'your_gmail_address'
password = 'your_password'
classname = "CSPP51087"
HW = 3
problems = ["1(a) - pp_ser.c", "1(b) - reoder.c", "1(c) - io.c", "2 - Advection"]
points   = [30, 20, 20, 30]
################################################################################

# Read in class.txt class list
lines = [line.strip() for line in open('class.txt')]
emails = []
names = []

for line in lines:
	words = line.split()
	name = ""
	for word in words:
		if word.find('@') != -1:
			emails.append(word)
		else:
			name = name + ' ' + word
	names.append(name)

students = zip(names, emails)

print "==========================================="
print "================ TA HELPER ================"
print "==========================================="
print "             Class: "+classname
print "                Homework: "+str(HW)
print "==========================================="

# Central program loop
while( 1 ):
	print "Options:"
	print "  1 - Generate Directories & grade.txt Files"
	print "  2 - Accumulate Central Grade List"
	print "  3 - Email grade.txt Files to Students"
	print "  4 - Quit"
	choice = raw_input("Choose Task: ")
	
	if( choice == '4' ):
		print "Exiting!"
		exit()

	if( choice == '1' ):
		#Generate grade files
		for name, email in students:
			if not os.path.exists(email):
				os.makedirs(email)
			fp = open(email+"/grade.txt", 'w')
			for i in range(1,70):
				fp.write("#")
			fp.write("\n")
			fp.write("Grade:  / "+str(sum(points))+"\n")
			fp.write("Student: "+name+"\n")
			fp.write("Email: "+email+"\n")
			fp.write("Class: "+classname+"\n")
			fp.write("Homework: "+str(HW)+"\n")
			for i in range(1,70):
				fp.write("#")
			fp.write("\n")

			for problem, point in zip(problems, points):
				fp.write("Problem "+problem+"    Grade: ")
				fp.write(" / "+str(point)+"\n")
				fp.write("\n\n\n")
				for i in range(1,70):
					fp.write("#")
				fp.write("\n")	
			fp.close
		print "Directories & grade.txt Files succesfully written!\n"
		
	if( choice == '2' ):
		# Write Grade List
		grades = []
		for name, email in students:
			if os.path.exists(email):
				lines = [line.strip() for line in open(email+"/grade.txt",'r')]
				for line in lines:
					if line.find("Grade:") == 0:
						grades.append(name+"\t\t"+line.lstrip("Grade:"))
			else:
				print "ERROR! Student: "+email+" Not Found!\n"
				exit()

		fp = open("HW"+str(HW)+"_grades.txt", "w")
		for grade in grades:
			fp.write(grade+"\n")
		fp.close
		print "Central grade list (HW"+str(HW)+"_grades.txt) created!\n"

	if( choice == '3' ):
		# Read in scripts
		scripts = []
		for name, email in students:
			if os.path.exists(email):
				fp = open(email+"/grade.txt",'r')
				script = "Subject: "+classname+" HW"+str(HW)+" Grade\n"
				script = script + "To: "+email+"\n"
				scripts.append(script+fp.read())

		# Check that names / emails / scripts are in sync
		i = 0
		for name,email in students:
			ok = 0
			lines = scripts[i].splitlines()
			for line in lines:
				if line.find("Student:") != -1 and line.find(name) != -1:
					ok = ok + 1
				if line.find("Email:") != -1 and line.find(email) != -1:
					ok = ok + 1
			if ok != 2:
				print name+" ("+email+") is NOT synced!"
				exit()
			i = i + 1

		# Email Out Grades
		username = fromaddr
		server = smtplib.SMTP('smtp.gmail.com:587')  
		server.starttls()  
		server.login(username,password)
		i = 0  
		for name, email in students:
			approval = raw_input("Send Grade to "+name+"? (y/n): ")
			if approval == 'y':
				server.sendmail(fromaddr, email, scripts[i])  
				print name+"'s script has been sent to "+email
			else:
				print "Skipping "+name+"..."
			i = i + 1
		server.quit()  
		
		print "All requested Emails have been sent!\n"
