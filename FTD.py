from tkinter.tix import INTEGER
from textx import metamodel_from_file
from datetime import datetime, timedelta, date
import sqlite3
import calendar as cd

#Retrieving meta language from file.
FutureToDo_meta = metamodel_from_file('FutureToDo.tx')
#Assigning file to read the language from.
#try-except used in case of invalid commands.
try:
    FutureToDo_model = FutureToDo_meta.model_from_file('task_list.ftd')
except Exception:
    print(f"ERROR! INVALID COMMAND(s)")

connect = sqlite3.connect('FutureCalendar2.db')
cursor = connect.cursor()

#default user/username if there is no login or someone only logs out
global DEFAULT_USERNAME 
DEFAULT_USERNAME = "Default User"

#table to hold calendar and task values
cursor.execute("""CREATE TABLE IF NOT EXISTS calendar (
               date text,
               task text,
               username text,
               ID int PRIMARY KEY,
               UNIQUE(date, task, username) ON CONFLICT REPLACE
               )""")

class Calendar(object):
    #function to add years to a date
    def add_years(start_date, years):
        try:
            return start_date.replace(year=start_date.year + years)
        except ValueError:
            return start_date.replace(year=start_date.year + years, day = 28)
    #function to add single event to specified date if it doesn't already exist
    def add_event(date, task, username):
        with connect:
            cursor.execute("INSERT or REPLACE INTO calendar (date, task, username) VALUES (?, ?, ?)", (date, task, username))
            connect.commit()
            print(f"USER {username} added Task '{task}' to date: {date}")
        return 0
    #function for handling recurring events
    def recurring_event(date, iter, task, username):
        with connect:
            dt_date = datetime.strptime(date, "%Y-%m-%d")
            steps = "year"
            #handling each iteration value (daily, weekly, or yearly)
            if iter == "DAILY":
                steps = "year"
                start_date = dt_date
                end_date = Calendar.add_years(start_date, 1)
                for my_date in Calendar.daterange_daily(start_date, end_date):
                    date = datetime.strftime(my_date, "%Y-%m-%d")
                    cursor.execute("INSERT or REPLACE INTO calendar(date, task, username) VALUES (?, ?, ?)", (date, task, username))
                    connect.commit()
            elif iter == "WEEKLY":
                steps = "year"
                start_date = dt_date
                end_date = Calendar.add_years(start_date, 1)
                for my_date in Calendar.daterange_weekly(start_date, end_date):
                    date = datetime.strftime(my_date, "%Y-%m-%d")
                    cursor.execute("INSERT or REPLACE INTO calendar(date, task, username) VALUES (?, ?, ?)", (date, task, username))
                    connect.commit()
            elif iter == "YEARLY":
                steps = "10 years"
                start_date = dt_date
                end_date = Calendar.add_years(start_date, 10)
                for my_date in Calendar.daterange_yearly(start_date, end_date):
                    date = datetime.strftime(my_date, "%Y-%m-%d")
                    cursor.execute("INSERT or REPLACE INTO calendar(date, task, username) VALUES (?, ?, ?)", (date, task, username))
                    connect.commit()
            print(f"For the user: {username}\r\nThe task: {task} has been added as a {iter} task for the next {steps}.")
    #daterage functions are used in recurring task handling, this one iterates date adding a single day for a year
    #monthly daterange currently not functioning, need to add dateutil or rework date database entries
    def daterange_daily(start_date, end_date):
        for n in range(0, int((end_date - start_date).days) + 1):
            yield start_date + timedelta(n)
    #iterates date, adds a week to the date for a year
    def daterange_weekly(start_date, end_date):
        for n in range(0, int((end_date - start_date).days) + 1, 7):
            yield start_date + timedelta(n)
    #iterates date, adds a year to the date for 10 years
    def daterange_yearly(start_date, years):
        for n in range(0, 10): 
            yield Calendar.add_years(start_date, n)

    #function to delete tasks for a specified date
    def del_date(date, username):
        with connect:
            cursor.execute("DELETE FROM calendar WHERE date=? AND username=?",(date, username,))
            connect.commit()
            print(f"All tasks on {date} have been deleted.")
        return 0
    #function to delete all tasks on calendar database
    def del_all():
        with connect:
            cursor.execute("DELETE FROM calendar")
            connect.commit()
            print(f"\r\nAll tasks on the Calendar have been deleted for every user.")
        return 0
    #function to delete all tasks for current user
    def del_user(username):
        with connect:
            cursor.execute("DELETE FROM calendar WHERE username=?",(username,))
            connect.commit()
            print(f"\r\nAll tasks for the user - {username} - have been deleted.")
        return 0

    #deletes specific task when given task ID and logged in as matching user
    def del_task(task_id, user_name):
        with connect:
            cursor.execute("SELECT * FROM calendar WHERE ID=?", (task_id,))
            row = cursor.fetchone()
            try:
                task_user = row[2]
                task_name = row[1]
                task_date = row[0]
                if user_name == task_user:
                    cursor.execute("DELETE FROM calendar WHERE ID=?", (task_id,))
                    connect.commit()
                    print(f"Task number: {task_id} '{task_name}' has been deleted/completed.")
                else:
                    print(f"Unable to make changes to task: {task_name} \r\nAs it belongs to the user: {task_user}")
            except Exception:
                print(f"ERROR CALENDAR NOT INITIALIZED. Please add a task to the calendar before deleting a task.\r\n")


    #function to return all tasks and dates on calendar in the order of the dates
    def get_admin():
        with connect:
            cursor.execute("SELECT * FROM calendar ORDER BY date(date) ASC")
            dates = cursor.fetchall()
            temp_month_year = "TEMPLATE_MONTH_YEAR"
            temp_month_day = "TEMPLATE_MONTH_DAY"
            for date in dates:
                current_date = datetime.strptime(date[0], "%Y-%m-%d")
                current_month_year = datetime.strftime(current_date, "%B %Y")
                current_month_day = datetime.strftime(current_date, "%d %B")
                if (temp_month_year != current_month_year):
                    temp_month_year = current_month_year
                    print(f"\r\nALL TASKS IN {current_month_year}:\r\n----------------------")
                    temp_month_day = current_month_day
                    print(f"Tasks for {current_month_day}:")
                if (temp_month_day != current_month_day):
                    temp_month_day = current_month_day
                    print(f"Tasks for {current_month_day}:")
                print("USER - " + date[2] + ": " + date[1])
        return 0
    #function to get all tasks from current user
    def get_all(username):
        with connect:
            cursor.execute("SELECT * FROM calendar WHERE username=? ORDER BY date(date) ASC",(username,))
            dates = cursor.fetchall()
            temp_month_year = "TEMPLATE_MONTH_YEAR"
            temp_month_day = "TEMPLATE_MONTH_DAY"
            print(f"\r\nAll tasks for '{username}':")
            for date in dates:
                current_date = datetime.strptime(date[0], "%Y-%m-%d")
                current_month_year = datetime.strftime(current_date, "%B %Y")
                current_month_day = datetime.strftime(current_date, "%d %B")
                if (temp_month_year != current_month_year):
                    temp_month_year = current_month_year
                    print(f"\r\nTASKS FOR '{username}' IN {current_month_year}:\r\n----------------------")
                    temp_month_day = current_month_day
                    print(f"Tasks for {current_month_day}:")
                if (temp_month_day != current_month_day):
                    temp_month_day = current_month_day
                    print(f"Tasks for {current_month_day}:")
                print(f"{date[3]} - {date[1]}")
        return 0
    #function to display all tasks on the specified date from the calendar database for the current user
    def get_date(date, username):
        with connect:
            cursor.execute("SELECT * FROM calendar WHERE date =? AND username=? ORDER BY date(date) ASC",(date, username,))
            dates = cursor.fetchall()
            print(f"\r\nCurrent User: {username}")
            print(f"TASKS FOR {date}:\r\n-------------------")
            for mydate in dates:
                print(f"{mydate[3]} - {mydate[1]}")
            print(f"\r\n")
        return 0

    #Display task and owner of task when given ID
    def get_task(task_id):
        with connect:
            cursor.execute("SELECT * FROM calendar WHERE ID=?", (task_id,))
            try:
                row = cursor.fetchone()
                task_user = row[2]
                task_name = row[1]
                task_date = row[0]
                print(f"\r\nTask {task_id} occurs on {task_date} and belongs to the user - {task_user}:\r\n{task_name}\r\n")
            except Exception:
                print(f"\r\nERROR - Task ID ({task_id}) does not exist.\r\n")
            

    #function to display all users in database
    def get_users():
        with connect:
            cursor.execute("SELECT DISTINCT username FROM calendar")
            users = cursor.fetchall()
            print("\r\nList of all Users in the system:\r\n")
            for user in users:
                print("- " + user[0])
        return 0

    #returns a formatted date from any command (from the .ftd file) that requires it
    def set_date(commands):
        year = str(commands.year)
        month = str(commands.month)
        day = str(commands.day)
        day = day.zfill(2)
        month = month.zfill(2)
        date = f"{year}-{month}-{day}"
        return date

    #function to interpret the commands given from the .ftd file using the TextX Grammar specified in FutureToDo.tx
    def interpret(model):
        user_name = DEFAULT_USERNAME
        #iterates through every command on the .ftd file assigning it to 'commands'
        for commands in FutureToDo_model.commands:
            task_list = ""
            subtask = []
            delimiter = "\r\n\t| "
            #these first if-elif blocks detect the type of operation the user will be doing
            #This block is for "-" identifier in code
            if commands.__class__.__name__ == "SingleTask":
                date = Calendar.set_date(commands.add_date)
                name = commands.add_task.name
                for subtasks in commands.sub_task:
                    subtask.append(subtasks.subname.name)
                if subtask != []:
                    task_list = delimiter.join(map(str, subtask))
                    temp_list = [name, task_list]
                    task_list = delimiter.join(temp_list)
                    Calendar.add_event(date, task_list, user_name)
                else:
                    Calendar.add_event(date, name, user_name)
            #Block for "!" identifier in code.
            elif commands.__class__.__name__ == "User":
                try:
                    user_name = commands.user_name.name
                except Exception: pass
                user_value = commands.user_value

                if user_value == "LOGIN":
                    print("LOGGED IN USER: " + user_name)
                elif user_value == "LOGOUT":
                    print("LOGGED OUT USER: " + user_name)
                    user_name = DEFAULT_USERNAME
                    print(f"Now logged in as: {user_name}")
                #elif user_value == "CREATE":
                    #print(user_value + " " + user_name)
                elif user_value == "DELETE":
                    Calendar.del_user(user_name)
            #Block for "~" in code
            elif commands.__class__.__name__ =="RecurringTask":
                date = Calendar.set_date(commands.add_date)
                name = commands.add_task.name
                if commands.iter_option == "DAILY":
                    iter="DAILY"
                elif commands.iter_option == "WEEKLY":
                    iter="WEEKLY"
                elif commands.iter_option == "MONTHLY":
                    iter="MONTHLY"
                elif commands.iter_option == "YEARLY":
                    iter="YEARLY"
                for subtasks in commands.sub_task:
                    subtask.append(subtasks.subname.name)
                if subtask != []:
                    task_list = delimiter.join(map(str, subtask))
                    temp_list = [name, task_list]
                    task_list = delimiter.join(temp_list)
                    Calendar.recurring_event(date, iter, task_list, user_name)
                else:
                    Calendar.recurring_event(date, iter, name, user_name)
            #Block for "?" identifier in code
            elif commands.__class__.__name__ == "GetTask":
                if commands.get_date == "ADMIN":
                    Calendar.get_admin()
                elif commands.get_date == "USERS":
                    Calendar.get_users()
                elif commands.get_date == "CALENDAR":
                    Calendar.get_all(user_name)
                elif isinstance(commands.get_date, int):
                    task_id = int(commands.get_date)
                    Calendar.get_task(task_id)
                else:
                    date = Calendar.set_date(commands.get_date)
                    Calendar.get_date(date, user_name)
            #Block for "CLEAR" identifier in code
            elif commands.__class__.__name__ == "Clear":
                if commands.clear_date == "ADMIN":
                    Calendar.del_all()
                elif commands.clear_date == "CALENDAR":
                    Calendar.del_user(user_name)
                else:
                    date = Calendar.set_date(commands.clear_date)
                    Calendar.del_date(date, user_name)
            #Block for "#" identifier in code
            elif commands.__class__.__name__ == "Complete":
                task_id = int(commands.identifier)
                Calendar.del_task(task_id, user_name)
            #BLock for "GUI" identifier in code, currently not implemented but grammar is in place for this to be implemented in the future.
            elif commands.__class__.__name__ == "GUI":
                print(f"GUI NOT YET IMPLEMENTED")


try:
    calendar = Calendar()
    calendar.interpret()
except Exception:
    print(f"ABORTING\r\n")
connect.close()