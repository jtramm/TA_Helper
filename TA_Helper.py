#!/usr/bin/python
import os
import sys
import smtplib  
import imaplib
import email
import time
import getpass
import base64
import fileinput
import random
import subprocess
import threading
#from subprocess import call
#from subprocess import check_call
#from subprocess import check_output
#from subprocess import CalledProcessError

################################ Configuration  ################################
num_students = 37 
spreadsheet_name = 'CSPP51040 Grades'
column_name = 'HW1'
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

# Email grade.txt files to students
def email_submission_status():
	# Get Gmail account credentials
	user = get_credentials()
	user_email_address = user[0]
	password = user[1]

	# Generate Emails
	i = 0
	notes = []
	lines = [line.strip() for line in open('subs.txt')]
	for line in lines:
		tokens = line.split()
		email = [s for s in tokens if "@" in s][0]
		if "RECEIVED" in tokens:
			message = "I have received your homework submission.\n"
		else:
			message = "I have not received your homework submission yet. If you have emailed it to me already, please contact me immediately so we can figure out where it went.\n"

		script = "Subject: "+assignment[0]+" "+column_name+" Submission Status\n"
		script = script + "To: "+email+"\n\n"
		script = script + message
		notes.append([email, script])
	
	# Email Out Grades
	username = user_email_address
	server = smtplib.SMTP('smtp.gmail.com:587')  
	server.starttls()  
	server.login(username,password)
	
	# Give user option to send emails to everyone
	yes = raw_input("Send submission notifications to ALL students? (y/n): ")
	if yes == 'y':
		really = raw_input("Are you SURE? (y/n): ")
		if really == 'y':
			for note in notes:
				server.sendmail(user_email_address, note[0], note[1])  
				print "Submission notification sent to: "+note[0]
			server.quit()  
			return
		else:
			print "OK, not doing anything"
			server.quit()  
			return
	
	server.quit()  
	print "All requested Emails have been sent!\n"
	return


def add_note_to_grade(addr, note, problem):		
	update = []
	if os.path.exists(addr+'/grade.txt'):
		lines = [line.strip() for line in open(addr+'/grade.txt','r')]
		was_grade = 0
		for line in lines:
			update.append(line)
			if line.startswith('Problem '+str(problem)+":"):
				update.append('\n'+note+'\n')
	f = open(addr+"/grade.txt", 'w')
	for line in update:
		f.write(line+'\n')
	f.close()

class Command(object):
	output = ''
	def __init__(self, cmd):
		self.cmd = cmd
		self.process = None

	def run(self, timeout):
		def target():
			#print 'Thread started'
			self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
			#output = self.process.stdout.read()
			self.output = self.process.communicate()[0]
			#print 'Thread finished'

		thread = threading.Thread(target=target)
		thread.start()

		thread.join(timeout)
		if thread.is_alive():
			print 'Terminating process'
			self.process.terminate()
			thread.join()
			return '(Your code never returned anything)'

		return self.output


# Auto-Grade
# Need to have some allowance for differences in whitespace I think....
def auto_grade():
	confirm = raw_input("Execute Auto-Grade (y/n)? ")
	if confirm != 'y':
		return
	all_students = raw_input("Grade all Students, or just some (all/some)? ")
	if all_students != 'all' and all_students != 'some':
		return
	nproblems = assignment[3]
	problems = assignment[4]
	congrats = [line.strip() for line in open('congrats.txt','r')]
	for name, email in students:
		if all_students == 'some':
			grade_student = raw_input("Grade student: "+name+"? (y/n): ")
			if grade_student != 'y':
				print "Skipping student: "+name
				continue
		print "Grading student: "+name
		results = []
		grades = []
		for problem in problems:
			grade = problem['value']
			if os.path.exists(email[0]+'/'+problem['fname']):
				notes = []
				for test in problem['tests']:
					try:
						# This needs to timeout somehow...
						run_call = email[0]+'/'+test
						command = Command(run_call)
						submittal = command.run(timeout=3)
						#submittal = check_output([email[0]+'/'+test], shell=True)
					except subprocess.CalledProcessError as e:
						submittal = e.output
					try:
						reference = subprocess.check_output(['./'+test], shell=True)
					except subprocess.CalledProcessError as e:
						reference = e.output
					if cmp(submittal.replace(' ',''),reference.replace(' ','') )!= 0:
						notes.append("Test: "+test)
						notes.append("Test Failed.")
						notes.append("Your Code Produced: ")
						notes.append(submittal)
						notes.append("Solution Produced: ")
						notes.append(reference)
						if grade == problem['value']:
							grade = (3* problem['value']) / 4
						elif grade == (3* problem['value']) / 4:
							grade = problem['value'] / 2
					else:
						notes.append("Test: "+test)
						notes.append("Test Passed!\n")
				results.append(notes)
			else:
				results.append(["Not Submitted"])
				grade = 0
			
			grades.append(grade)
		
		update = []
		a = 0
		if os.path.exists(email[0]+'/grade.txt'):
			lines = [line.strip() for line in open(email[0]+'/grade.txt','r')]
			was_grade = 0
			for line in lines:
				is_grade = 0
				if line.startswith("Grade:"):
					tokens = line.split('/')
					tokens.insert(1,' /')
					tokens.insert(1,str(sum(grades)))
					tokens = ''.join(tokens)
					update.append(tokens)
					is_grade = 1
				for i in range(1, nproblems+1):
					if line.startswith('Problem '+str(i)+":"):
						tokens = line.split('/')
						tokens.insert(1,' /')
						tokens.insert(1,str(grades[i-1]))
						tokens = ''.join(tokens)
						update.append(tokens)
						is_grade = 1
						was_grade = 1
				if is_grade == 0:
					update.append(line)
					if was_grade == 1:
						for note in results[a]:
							update.append(note)
						if grades[a] == problems[a]['value']:
							update.append( '\n'+random.choice(congrats)+'\n' )
						a += 1
					was_grade = 0
		f = open(email[0]+"/grade.txt", 'w')
		for line in update:
			f.write(line+'\n')
		f.close()

# Compiles All Student Code
def compile_subs():
	grades = []
	nproblems = assignment[3]
	problems = assignment[4]
	for name, email in students:
		if os.path.exists(email[0]):
			print "compiling submission from: "+name
			i = 1
			for p in problems:
				if os.path.exists(email[0]+'/'+p['fname']):
					if os.path.exists(email[0]+'/p'+str(i)):
						if not os.path.exists(email[0]+'/old_files'):
							subprocess.call(['mkdir', email[0]+'/old_files'])
						subprocess.call(['mv', email[0]+'/p'+str(i), email[0]+'/old_files'])
					try:
						compilation = subprocess.check_output(['gcc','-Wall','-ansi', '-pedantic', '-o', email[0]+'/p'+str(i), email[0]+'/'+p['fname']], stderr=subprocess.STDOUT)
					except subprocess.CalledProcessError as e:
						compilation = e.output
					if compilation != '':
						compilation = 'There were errors and warnings during compilation:\n'+compilation
						add_note_to_grade(email[0], compilation, i)
					i += 1
				#else:
					#print "No "+p['fname']+" found for student "+email[0]
	return

# Get Assignment Details from input File
def get_assignment():

	if not os.path.exists('problems.dat'):
		print "You need to define the problems for this assignment in the problems.dat file"
		exit(0)

	lines = [line.strip() for line in open("problems.dat",'r')]

	n = 0 #line number

	classname = lines[n].split('=')
	classname = classname[1].split()[0]
	n += 1

	# Assignment Type
	assignment = lines[n].split('=')
	assignment = assignment[1].split()[0]
	n += 1

	# Assignment Number
	anumber = lines[n].split('=')
	anumber = anumber[1].split()[0]
	n += 1

	# Number of Problems
	nproblems = lines[n].split('=')
	nproblems = int(nproblems[1].split()[0])
	n += 1

	# Loop over Problems
	problems = []
	for i in range(1, nproblems+1):
		n += 1
		
		# Problem Name
		name = lines[n].split('=')
		name = name[1].strip()
		n += 1
		 
		# Problem File Name
		fname = lines[n].split('=')
		fname = fname[1].split()[0]
		n += 1

		# Problem Credit Value
		value = lines[n].split('=')
		value = int(value[1].split()[0])
		n += 1
		
		# Credit Type (regular or extra)
		credit = lines[n].split('=')
		credit = credit[1].split()[0]
		n += 1

		# Number of tests
		ntests = lines[n].split('=')
		ntests = int(ntests[1].split()[0])
		n += 1

		# Loop over Tests
		tests = []
		for j in range(1, ntests+1):
			n += 1
			test = lines[n].strip()
			n += 1
			tests.append(test)
		
		# Add all data to problem
		problem = {'name' : name, 'fname' : fname, 'value' : value, 'credit' : credit, 'ntests' : ntests, 'tests' : tests}

		problems.append(problem)

	# print problems
	#for p in problems:
	#	print p['name']
	#	print p['fname']
	#	print p['value']
	#	print p['credit']
	#	print p['ntests']
	#	for t in p['tests']:
	#		print t
	
	full_assignment = classname, assignment, anumber, nproblems, problems 

	return full_assignment

	
# Uploads grades to google docs spreadsheet
def upload_grades():
	try: import gspread
	except ImportError:
		print "Install gpsread library (on github @ https://github.com/burnash/gspread)"
		print "Note - library is super easy to install!"
		return
	
	user = get_credentials()
	gc = gspread.login(user[0],user[1])
	spreadsheet = gc.open(spreadsheet_name)
	worksheet = spreadsheet.get_worksheet(0)
	
	grades = []
	for name, email in students:
		if os.path.exists(email[0]):
			lines = [line.strip() for line in open(email[0]+"/grade.txt",'r')]
			for line in lines:
				if line.find("Grade:") == 0:
					grade = line.lstrip("Grade:")
					words = grade.rsplit('/');
					grades.append(words[0])
		else:
			print "ERROR! Student: "+email[0]+" Not Found!\n"
			print "grades not uploaded..."
			return
	
	col = worksheet.find(column_name)
	i = 2
	for g in grades:
		worksheet.update_cell(i,col.col, g)
		i += 1

	print "Grades have been uploaded to spreadsheet: "+spreadsheet_name

	return

# Gets the class list from google spreadsheet
def get_students_from_gmail( ):

	# This portion downloads from the spreadsheet
	try: import gspread
	except ImportError:
		print "Install gpsread library (on github @ https://github.com/burnash/gspread)"
		print "Note - library is super easy to install!"
		return

	user = get_credentials()
	
	# Login with your Google account
	gc = gspread.login(user[0],user[1])

	# Spreadsheets can be opened by their title in Google Docs
	spreadsheet = gc.open(spreadsheet_name)

	# Select worksheet by index
	worksheet = spreadsheet.get_worksheet(0)

	# Update cell with your form value
	#worksheet.update_cell(1, 2, 'woot!')

	ncells = 'A2:A' + str(num_students+1)
	cell_list = worksheet.range(ncells)
	names = []
	for cell in cell_list:
		names.append(cell.value)
	
	ncells = 'B2:B' + str(num_students+1)	
	cell_list = worksheet.range(ncells)
	emails = []
	for cell in cell_list:
		emails.append(cell.value)
	
	tokenized_emails = []
	for email in emails:
		tokenized_emails.append(email.split(' '))	
	
	students = zip(names, tokenized_emails)

	return students


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
				subprocess.call(cmd, shell=True)
			elif f.endswith(".tar.gz") or f.endswith(".tgz"):
				print message
				subprocess.call(['tar','-xzf',obj, '-C', dirname])
			elif f.endswith(".tar"):
				print message
				subprocess.call(['tar','-xf',obj, '-C', dirname])
			elif f.endswith(".rar"):
				print message
				subprocess.call(['unrar','e',obj,dirname])
	
	# Summon All submission to top level student directories
	for name, email in students:
		dir_to_flatten = email[0] 
		for dirpath, dirnames, filenames in os.walk(dir_to_flatten):
			for filename in filenames:
				if filename.endswith(".c"):
					try:
						os.rename(os.path.join(dirpath, filename), os.path.join(dir_to_flatten, filename))
					except OSError:
						print ("Could not move %s " % os.join(dirpath, filename))

	return

# Read in class.txt class list
# Not really used anymore. Now students are DL'd from gmail spreadsheet
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

# IMPROVED Generates directory structure and grade.txt files
def generate_directories():

	classname = assignment[0]
	atype = assignment[1]
	anumber = assignment[2]
	nproblems = assignment[3]
	problems = assignment[4]

	points = 0
	for p in problems:
		if p['credit'] == 'regular':
			points += p['value']


	for name, email in students:
		if not os.path.exists(email[0]):
			os.makedirs(email[0])
		fp = open(email[0]+"/grade.txt", 'w')
		for i in range(1,70):
			fp.write("#")
		fp.write("\n")
		fp.write("Grade:  / "+str(points)+"\n")
		fp.write("Student: "+name+"\n")
		fp.write("Email: "+email[0]+"\n")
		fp.write("Class: "+classname+"\n")
		fp.write(atype+': '+str(anumber)+"\n")
		for i in range(1,70):
			fp.write("#")
		fp.write("\n")
		
		i = 1
		for problem in problems:
			fp.write("Problem "+str(i)+": "+problem['name']+"    Grade:  / "+str(problem['value'])+"\n")
			i += 1
			fp.write("\n\n\n")
			for j in range(1,70):
				fp.write("#")
			fp.write("\n")	
		fp.close
	print "Directories & grade.txt Files succesfully written!\n"
	return

#Download emails
def download_emails():
	
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

			# New checks against students
			found = 0
			for s_name, s_email in students:
				for s_email_token in s_email:
					if student == s_email_token:
						found = 1
						student = s_email[0]

			if found == 0:
			# Original checks against dir structure
			#if not os.path.exists(student):
				print student+" not found. Select student to assign to: "
				it = 0
				for name, addr in students:
					print str(it)+". "+name+" <"+' '.join(addr)+">"
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
					student = students[int(choice)][1][0]
					submitted[int(choice)] = 1
					# Now we need to write back to the gmail file.... YIKES!
					# For now, we can just manually add these in....
					#add_student_email(student)
			else:
				ita = 0
				for name, addr in students:
					if addr[0] == student:
						submitted[ita] = 1
					ita = ita + 1

			path = student + '/'+ filename

			fp = open(path, 'wb')
			fp.write(part.get_payload(decode=1))
			fp.close
			print student+"'s submission received"
			#time.sleep(5)

	# write out the subs.txt file to keep track of missing submissions
	ita = 0
	for name, addr in students:
		subs.write(name.ljust(30)+" "+addr[0].ljust(30)+" ")
		if submitted[ita] == 1:
			subs.write(" RECEIVED")
		ita = ita + 1
		subs.write("\n")
	
	subs.close
	
	return

# Creates a centralized grades list (grade.txt)
def generate_grade_list():
	grades = []
	for name, email in students:
		if os.path.exists(email[0]):
			lines = [line.strip() for line in open(email[0]+"/grade.txt",'r')]
			for line in lines:
				if line.find("Grade:") == 0:
					grades.append(name.ljust(25)+" "+line.lstrip("Grade:"))
		else:
			print "ERROR! Student: "+email[0]+" Not Found!\n"
			exit()

	fp = open(column_name+"_grades.txt", "w")
	for grade in grades:
		fp.write(grade+"\n")
	fp.close
	print "Central grade list ("+column_name+"_grades.txt) created!\n"

	return

# Email grade.txt files to students
def email_grades():
	# Get Gmail account credentials
	user = get_credentials()
	user_email_address = user[0]
	password = user[1]

	# Read in scripts
	scripts = []
	for name, email in students:
		if os.path.exists(email[0]):
			fp = open(email[0]+"/grade.txt",'r')
			script = "Subject: "+assignment[0]+" "+column_name+" Grade\n"
			script = script + "To: "+email[0]+"\n"
			scripts.append(script+fp.read())

	# Check that names / emails / scripts are in sync
	i = 0
	for name,email in students:
		ok = 0
		lines = scripts[i].splitlines()
		for line in lines:
			if line.find("Student:") != -1 and line.find(name) != -1:
				ok = ok + 1
			if line.find("Email:") != -1 and line.find(email[0]) != -1:
				ok = ok + 1
		if ok != 2:
			print name+" ("+email[0]+") is NOT synced!"
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
				server.sendmail(user_email_address, email[0], scripts[i])  
				print name+"'s script has been sent to "+email[0]
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
				server.sendmail(user_email_address, email[0], scripts[i])  
				print name+"'s script has been sent to "+email[0]
			else:
				print "Skipping "+name+"..."
			i = i + 1
	server.quit()  
	
	print "All requested Emails have been sent!\n"

	return

def print_header():
	classname = assignment[0]
	atype =  assignment[1]
	anum = assignment[2]
	print "==========================================="
	print "================ TA HELPER ================"
	print "==========================================="
	print "             Class: "+classname
	print "                "+atype+": "+str(anum)
	print "==========================================="
	return

def get_task_choice():
	print "Options:"
	print "  1 - Generate Directories & grade.txt Files"
	print "  2 - Download Student Submissions From Gmail"
	print "  3 - Email Submisssion Confirmation Notes to All Students"
	print "  4 - Decompress Student Submission Files (.zip, .tar, .tar.gz, .tgz)"
	print "  5 - Compile Student Submissions"
	print "  6 - Grade Student Submissions"
	print "  7 - Accumulate Central Grade List"
	print "  8 - Email grade.txt Files to Students"
	print "  9 - Upload Grades to Google Docs"
	print "  10 - Quit"
	while(1):
		choice = raw_input("Choose Task: ")
		try:
			i = int(choice)
		except ValueError:
			print "Invalid Choice. Please enter an integer."
		else:
			return i

# Central program loop
students = get_students_from_gmail()
assignment = get_assignment()
print_header( )
while( 1 ):

	choice = get_task_choice()
		
	if choice == 1   : generate_directories( )
	elif choice == 2 : download_emails( )
	elif choice == 3 : email_submission_status()
	elif choice == 4 : unzip_submissions()
	elif choice == 5 : compile_subs( ) 
	elif choice == 6 : auto_grade()
	elif choice == 7 : generate_grade_list( )
	elif choice == 8 : email_grades( )
	elif choice == 9 : upload_grades( )
	else :
		print "Exiting!"
		exit()
