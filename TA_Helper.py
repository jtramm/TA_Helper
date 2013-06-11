#!/usr/bin/python
import os
import smtplib  
import imaplib
import email
import time
import getpass
import base64
from subprocess import call
from subprocess import check_call

################################ Configuration  ################################
classname = "CSPP51087"
HW = 4
problems = ["1 - Mandelbrot Redux", "2 - Hashing Histogram", "3 - Advection Battle", "4 - Extra Credit Hybrid"]
points   = [30, 35, 35, 0]
################################################################################

# Gets and Stores User Credentials
def get_credentials():
	found = 1
	try:
		with open('credentials.dat'): pass
	except IOError:
		print "credentials.dat file not found"
		found = 0
	if found == 0:
		user_email_address = raw_input("Gmail Address: ")
		password = getpass.getpass()
		save = raw_input("Credentials gathered. Would you like to encode & save them? (y/n): ")
		if save == "y":
			cred = open('credentials.dat', 'w')
			cred.write(base64.b64encode(user_email_address))
			cred.write('\n')
			cred.write(base64.b64encode(password))
			cred.close()
	if found == 1:
		cred = open('credentials.dat', 'r')
		user_email_address = base64.b64decode(cred.readline())
		password = base64.b64decode(cred.readline())
	user = [user_email_address, password]
	return user

# Decompresses submissions
def unzip_submissions():
	for root, dirs, files in os.walk("."): 
		for f in files: 
			obj = os.path.abspath(os.path.join(root, f)) 
			(dirname, filename) = os.path.split(obj)
			message = "Decompressing "+f
			if f.endswith(".zip"):
				print message
				cmd = 'unzip -u -d '+dirname+' '+obj+' > /dev/null'
				call(cmd, shell=True)
			elif f.endswith(".tar.gz"):
				print message
				call(['tar','-xzf',obj, '-C', dirname])
			elif f.endswith(".tar"):
				print message
				call(['tar','-xf',obj, '-C', dirname])
	return

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
	print "  3 - Decompress Student Submission Files (.zip, .tar,"
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
def download_emails( students ):
	
	# Get gmail credentials
	user = get_credentials()
	user_email_address = user[0]
	password = user[1]

	mail = imaplib.IMAP4_SSL('imap.gmail.com')
	mail.login(user_email_address, password)
	
	# read in and parse your mail folders	
	raw_folders = mail.list()[1]
	folders = []	
	for line in raw_folders:
		tags = line.split('\"')
		folder = tags[len(tags)-2]
		folder = folder.strip('\"')
		folders.append(folder)
	
	# Get user selection for mail folder
	print "Your Mail Folders:"
	ix = 0
	for folder in folders:
		print"  "+str(ix)+". "+folder
		ix += 1
	choice = raw_input("Please select folder to download: ")

	mail.select(folders[int(choice)]) # connect to inbox.

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
			time.sleep(5)

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

# Email grade.txt files to students
def email_grades(students):
	# Get Gmail account credentials
	user = get_credentials()
	user_email_address = user[0]
	password = user[1]

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
	
	# Give user option to send emails to everyone
	yes = raw_input("Send grades to ALL students? (y/n): ")
	if yes == 'y':
		really = raw_input("Are you SURE? (y/n): ")
		if really == 'y':
			i = 0  
			for name, email in students:
				server.sendmail(user_email_address, email, scripts[i])  
				print name+"'s script has been sent to "+email
				i = i + 1
			server.quit()  
			return
		else:
			print "OK, not doing anything"
			server.quit()  
			return
	else:
		print "Ok, let's send grades to SOME students then..."
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
	elif choice == 2 : download_emails( students )
	elif choice == 3 : unzip_submissions()
	elif choice == 4 : generate_grade_list( students )
	elif choice == 5 : email_grades( students  )
	else :
		print "Exiting!"
		exit()
