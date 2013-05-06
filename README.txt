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

This is a short program used for managing student submissions and automatically emailing out grades/comments.

==============================================================================
How Do I Use TA Helper
==============================================================================

Create a student roster list in the form of a "class.txt" input file. This
file will contain a list of students, in the form of a name and an email
on each line. For instance:

John Tramm john.tramm@gmail.com
John Doe J.Doe@email.com

Now you will need to configure a few things in the TA_Helper.py file:

################################ Configuration  ################################
fromaddr = 'your_gmail_address'
password = 'your_password'
classname = "CSPP51087"
HW = 3
problems = ["1(a) - pp_ser.c", "1(b) - reoder.c", "1(c) - io.c", "2 - Advection"]
points   = [30, 20, 20, 30]
################################################################################

The problems and points lists should correspond to one another and have the
same number of elements.

Note that this program only works with Gmail. Configuration for other servers
should be fairly trivial, but I'll leave that to you.

Once configured, simply run via the command:

	>$ python TA_Helper.py

This should give you the following menu, and the rest should be fairly self
explanatory: 

===========================================
================ TA HELPER ================
===========================================
             Class: CSPP51087
                Homework: 3
===========================================
Options:
  1 - Generate Directories & grade.txt Files
  2 - Accumulate Central Grade List
  3 - Email grade.txt Files to Students
  4 - Quit
Choose Task:
