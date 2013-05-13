#!/usr/bin/python
import os
import smtplib  
import imaplib
import email

################################ Configuration  ################################
user_email_address = 'your_gmail_address'
password = 'your_password'
classname = "CSPP51087"
HW = 3
problems = ["1(a) - pp_ser.c", "1(b) - reoder.c", "1(c) - io.c", "2 - Advection"]
points   = [30, 20, 20, 30]
################################################################################

# Read in class.txt class list
def get_class_list():
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

	return students

def print_header( classname, HW):
	print "==========================================="
	print "================ TA HELPER ================"
	print "==========================================="
	print "             Class: "+classname
	print "                Homework: "+str(HW)
	print "==========================================="
	return

def get_task_choice():
	print "Options:"
	print "  1 - Generate Directories & grade.txt Files"
	print "  2 - Download Student Submissions From Gmail"
	print "  3 - Decompress Student Submission Files"
	print "  4 - Accumulate Central Grade List"
	print "  5 - Email grade.txt Files to Students"
	print "  6 - Quit"
	while(1):
		choice = raw_input("Choose Task: ")
		try:
			i = int(choice)
		except ValueError:
			print "Invalid Choice. Please enter an integer."
		else:
			return i

# Generates directory structure and grade.txt files
def generate_directories(students, problems, points, classname, HW):
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
	return

#Download emails
def download_emails( students, user_email_address, password ):
	mail = imaplib.IMAP4_SSL('imap.gmail.com')
	mail.login(user_email_address, password)
	mail.select(clasname+"/"+str(HW)) # connect to inbox.
	result, data = mail.search(None, "ALL")
	ids = data[0].split() # ids is a space separated string

	# Open an array and file to record submissions centrally
	submitted = [0]*len(students)
	subs = open("subs.txt", 'w')

	for i in ids:

		result, data = mail.fetch(i, "(RFC822)") # fetch the email string
		raw_email = data[0][1] #just the string

		# Parse string into message object
		msg = email.message_from_string(raw_email)
		
		addr = msg.__getitem__('from')
		
		words = addr.split()
		for word in words:
			if word.find('@') != -1:
				student = word
		
		student = student.strip('<>')

		for part in msg.walk():
			#print(part.get_content_type())

			if part.get_content_maintype() == 'multipart':
				continue

			if part.get('Content-Disposition') is None:
				#print("ERROR: Content Type is Weird...")
				continue

			filename = part.get_filename()
			if not(filename):
				print "ERROR - QUitting"
				exit(1)

			if not os.path.exists(student):
				print student+" not found. Select student to assign to: "
				it = 0
				for name, addr in students:
					print str(it)+". "+name+" <"+addr+">"
					it = it + 1
				print str(it)+". Not Listed - quit"
				print str(it+1)+". Not Listed - discard submission"
				choice = raw_input("Choose Student: ")
				
				if choice == str(it):
					print "Exiting..."
					exit(1)
				elif choice == str(it+1):
					print "Skipping..."
					continue
				else:
					student = students[int(choice)][1]
					submitted[int(choice)] = 1
			else:
				ita = 0
				for name, addr in students:
					if addr == student:
						submitted[ita] = 1
					ita = ita + 1

			path = student + '/'+ filename

			fp = open(path, 'wb')
			fp.write(part.get_payload(decode=1))
			fp.close

	# write out the subs.txt file to keep track of missing submissions
	ita = 0
	for name, addr in students:
		subs.write(name+" <"+addr+"> :")
		if submitted[ita] == 1:
			subs.write(" RECEIVED")
		ita = ita + 1
		subs.write("\n")
	
	subs.close
	
	return

# Creates a centralized grades list (grade.txt)
def generate_grade_list(students):
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

	return

def email_grades(students, user_email_address, password):
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
	username = user_email_address
	server = smtplib.SMTP('smtp.gmail.com:587')  
	server.starttls()  
	server.login(username,password)
	i = 0  
	for name, email in students:
		approval = raw_input("Send Grade to "+name+"? (y/n): ")
		if approval == 'y':
			server.sendmail(user_email_address, email, scripts[i])  
			print name+"'s script has been sent to "+email
		else:
			print "Skipping "+name+"..."
		i = i + 1
	server.quit()  
	
	print "All requested Emails have been sent!\n"

	return

# Central program loop
students = get_class_list()
print_header( classname, HW )
while( 1 ):

	choice = get_task_choice()
		
	if choice == 1   :
		generate_directories( students, problems, points, classname, HW )
	elif choice == 2 : download_emails( students, user_email_address, password )
	elif choice == 3 : print "functionality not implemented yet"
	elif choice == 4 : generate_grade_list( students )
	elif choice == 5 : email_grades( students, user_email_address, password )
	else :
		print "Exiting!"
		exit()
