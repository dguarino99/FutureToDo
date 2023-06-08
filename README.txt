# FutureToDo
Python and TextX based DSL (Domain Specific Language) allowing easy use of task management using a calendar based system.

Requirements:
Python v3.6+
textX (https://textx.github.io/textX/3.1/)

What to download:
FutureToDo-Full - includes all necessary files (or you can download the files separately: FTD.py, FutureToDo.tx, task_list.ftd). 

How it works:
FutureToDo.tx is the textX file that defines the grammar for the language. The task_list.ftd file is the file that will be used to write the code for the program. 
Once the task_list.ftd file is saved the user will run the FTD.py program which will read the .ftd file and interpret and execute the given commands.
The task_list.ftd file is read from top to bottom line-by-line.

Grammar/Commands for task_list.ftd file:
Can be found by reading the FutureToDo.tx file but will also be explained below.
parentheses, single quotes, and double quotes are not used in the language and are solely used for clarification below.
If there is a question mark after a variable then that means the variable is optional and does not have to be included in the command for it to work. 

Each new line is considered a new command for the language, so when ending a command nothing is needed except a new line in the .ftd file.


Adding a single task to the calendar:
'-' date task_name ( | subtask_name | subtask_name)
the subtasks are separated using '|', they are optional, and there is no limit to the number of subtasks per task. 
examples single tasks:
- 1/1/2024 Celebrate the new year!
or
- 2/20/2023 pick up groceries | milk | eggs | cereal | etc...

Adding a repeatable task to the calendar:
'~' date iteration task_name ( | subtask_name | subtask_name)
'iteration' variable takes the string literals "DAILY" "WEEKLY" or "YEARLY" as of this version, this task will repeat for either a year or multiple years depending on the iteration.
Other than the addition of the iteration variable and '~' this command is the same as the single task command.
ex:
~ 1/1/2023 YEARLY celebrate the new year!
this command will add a task with the string "celebrate the new year!" to the calendar database file 

Displaying tasks/users from the calendar:
'?' get_value
where get_value can either be a date or the string literals "CALENDAR", "ADMIN", or "USERS".
when the value is a date, all tasks for that date for the current user will be displayed.
when the value is "CALENDAR", all tasks on the entire calendar for the current user will be displayed.
when the value is "ADMIN", all tasks for every user will be displayed (it will also show which user is assigned to each task)
when the value is "USERS", the program will show all users that have tasks saved in the database.

Clearing tasks from the calendar:
'CLEAR' clear_value
where clear_value can be a date or the string literals "CALENDAR" or "ADMIN".
when clear_value is a date it will clear every task on the specified date for the current user.
when clear_value is "CALENDAR" it will clear every task on the calendar for the current user.
when clear_value is "ADMIN" it will clear every task for every user in the database.

Commands related to the users:
! user_command user_name
where user_command can either be "LOGIN" or "LOGOUT", and user_name is just any string which will represent the user.
the user is automatically logged out whenever starting/stopping the program so in order to make changes to a users calendar you have to enter the login command before any other actions in the task_list.ftd file.
