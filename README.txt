==============================================================================
    ______  ______      __  __          ___                            
   /\__  _\/\  _  \    /\ \/\ \        /\_ \                           
   \/_/\ \/\ \ \L\ \   \ \ \_\ \     __\//\ \    _____      __   _ __  
      \ \ \ \ \  __ \   \ \  _  \  /'__`\\ \ \  /\ '__`\  /'__`\/\`'__\
       \ \ \ \ \ \/\ \   \ \ \ \ \/\  __/ \_\ \_\ \ \L\ \/\  __/\ \ \/ 
        \ \_\ \ \_\ \_\   \ \_\ \_\ \____\/\____\\ \ ,__/\ \____\\ \_\ 
         \/_/  \/_/\/_/    \/_/\/_/\/____/\/____/ \ \ \/  \/____/ \/_/ 
                                                   \ \_\               
                                                    \/_/               

==============================================================================
Contact Information
==============================================================================

              Development Lead: John Tramm <john.tramm@gmail.com>

==============================================================================
What is TA Helper?
==============================================================================

This is a short program used for managing student submissions,
auto-grading them, and automatically emailing out grades/comments.
It relies heavily on Gmail and Google Docs, so you will definitely
need a gmail account.

==============================================================================
How Do I Use TA Helper
==============================================================================

Download----------------------------------------------------------------------

	git clone git://github.com/jtramm/TA_Helper.git

WorkFlow----------------------------------------------------------------------

	The general workflow for grading an assignment, using the aid of
	TA Helper, should generally follow the flow laid out in the menu
    of TA Helper:

	===========================================
	================ TA HELPER ================
	===========================================
				 Class: MyClass
					Homework: 1
	===========================================
	Options:
	  1 - Generate Directories & grade.txt Files
	  2 - Download Student Submissions From Gmail
	  3 - Email Submisssion Confirmation Notes to All Students
	  4 - Decompress Student Submission Files (.zip, .tar, .tar.gz, .tgz)
	  5 - Compile Student Submissions
	  6 - Grade Student Submissions
	  7 - Accumulate Central Grade List
	  8 - Email grade.txt Files to Students
	  9 - Upload Grades to Google Docs
	  10 - Quit
	Choose Task:

	Explanation:

	Upon running, you will be asked for your gmail credentials. If you
	want, these can be stored in a Base64 encrypted file (credentials.dat)
	to expedite running the code in future uses.

	1 - Generates a directory structure to hold student submissions and
	    grading files. All students will get a unique directory in the
		form of their email addresses, inside of which a template grade.txt
		will be added containing the grading rubric for the assignment
		as well as their names/emails and title information, etc.

	2 - Downloads all attachments from a gmail folder of your choice.
		Attachments are placed in the folders corresponding to each
		student's email. If an email address is not recognized, you will
		be asked to assign the email to a known student, or discard it.
		Additional email addresses can be added to students via the
		Google drive class spreadsheet. Simply add it to their email field,
		using a single space as the delimeter between addressese.
		
		This function will also keep track of submissions and write them
		out in the subs.txt file.

	3 - Emails submission status notes to students. This function uses the
		subs.txt file for all it's info. It will use the addresses and statuses
		in there. Students who have already been emailed once with this function
		will not be notified again. Students that have not submitted anything
		will continue to receive emails from this function until they turn
		something in.

	4 - Decompresses student submissions, and pull all source files to the top
		of their directories. Students usually love having crazy nested file
		structures, so this normalizes things so that all source files are at
		the top level. 

	5 - Compiles all student submissions. Any warnings or errors during 
		compilation will be added to the student's grade.txt file.
		Note - currently, if students have stuff in folders named "p1", "p2",
		you may lose any readme's in said folders. 

	6 - Runs the auto-grader on student submissions, and writes the results
		to each student's grade.txt file. You can run it on all
		or some of the students. It is a bad idea to auto-grade the same student
		twice, as the auto-grader doesn't wipe out its comments from the first
		pass, so things will get messy.

		The auto-grader works by comparing output from submssions against
		the reference implementation programs. If students have ignored
		requirements, and their codes don't return or are waiting input
		that isn't coming, they are killed after 3 seconds.

		The basic grading scheme is as follows:

		> If a student passes all tests, they receive a full score,
		  and a random positive comment from the "congrats.txt" file.

		> If a student fails 1 test, they receive 3/4 credit (rounded
		  down to an integer).
		
		> If a student fails more than 1 test, the receive half credit
		  for the problem. 
		
		> If a student turns nothing in, they get no credit.

		Beyond that, the grader is encouraged to ammend and alter grades
		if errors are made by the auto-grader. Strict formatting rules
		are applied by the auto-grader, so errors are likely common, but
		it should be easy to spot these as all results are printed to the
		grade.txt files.

	7 - Accumulates a centralized grade.txt file to look over. Basically
		just scans the grade.txt files and pulls out the total scores.

	8 - Emails all students their grade.txt files. You will have the option
		of emailing all or some of the students interactively. Note that
		running this function multiple times will email students again - 
		the code doesn't know if people have already been alerted or not.

	9 - Uploades grades to the google docs spreadsheet. Can be run as many
		times and will just overwrite the contents there. 

Configuration-----------------------------------------------------------------


	***Note*** that this program only works with Gmail.
	Configuration for other servers should be fairly trivial,
	but I'll leave that to you.

	***Note*** If you want to unzip rar files, please install
	unrar on your machine. (can be done on macs with macports)

	The main thrust here will be defining your assignment in
	the problems.dat file. See the included sample file for the
	format. The other configuration that is necessary is at the
	top of TA_Helper.py:

	################################ Configuration  #########################
	num_students = 37 
	spreadsheet_name = 'CSPP51040 Grades'
	column_name = 'HW1'
	#########################################################################

	All the above values are used to determine a number of
	things, but mostly for communicating with the google docs
	spreadsheet. I.e., the spreadsheet_name is the name of your
	spreadsheet on google drive, and column_name is the name
	of the column for this assignment (i.e., HW1, EXAM1, etc).
	The num_students is required to know how many lines of the
	spreadsheet to read. column_name is also used for some of the
	printouts/emails sent to students.

