
import re
import datetime
import sys
import os
import pytz
from collections import OrderedDict

from peewee import *

db = SqliteDatabase('work_log.db')

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

class Entry(Model):
    user_name = CharField(max_length=255, unique=False)
    task_name = CharField(max_length=255)
    task_time = IntegerField(default=0)
    add_notes = TextField(default='') # Allows for any length of text.
    timestamp = DateField(default=datetime.date.today())

    class Meta:
        database = db

def initialize():
    """Create database and the table if they don't exist."""
    db.connect(reuse_if_open=True)
    db.create_tables([Entry], safe=True) 

def user_menu():

    clear_screen()
    user_choice = None

    menu = OrderedDict([
    ('a', add_entry),
    ('s', search_entries_menu), 
    ])

    while user_choice !='q':
        clear_screen()
        print("Press 'q' to quit")
        for key, value in menu.items():
            print('{}: {}'.format(key,value.__doc__))
        user_choice = input("Action:  ").lower().strip()
       
        if user_choice in menu:
            menu[user_choice]()
  
def add_entry():
    """Adds entry to DB"""
    clear_screen()
    add_name = input("Please enter your name:  ")
    add_task = input("Please enter the task at hand:  ")
    try:
        add_time = int(input("Please enter the task's length:  "))
    except ValueError:
        print("Please enter a digit value only")
        add_time = int(input("Please enter the task's length:   "))
    user_notes = input("Any additional notes for the task:   ")

    if all([add_name, add_task, add_time, user_notes]):
        if input("Save entry? [Yn]").lower() != 'n':
            Entry.create(
                user_name=add_name,
                task_name=add_task,
                task_time=add_time,
                add_notes=user_notes
                ) 
            print("Saved successfully!")
        else:
            user_menu()
    menu_loop_choice = input("Enter another task? [Yn] : ")
    if menu_loop_choice.lower() == 'y':
        add_entry()
    else:
        user_menu()
    

def view_entries(result_list):
    """Views entry"""
    clear_screen()
    counter = 1
    for item in result_list:
        print("""
            Result {} of {}\n
            Name: {}
            Task: {}
            Time Length: {}
            Date: {}
            Notes: {}\n""".format(counter, len(result_list), item.user_name, item.task_name, item.task_time, item.timestamp, item.add_notes))
        user_selection = None
        while not user_selection:
            user_selection = input("""
            Please Select...
            {}
            [E] for Edit entry, 
            [D] for Delete entry, 
            [S] for the Search Menu:  
            """.format('''
            [N] for Next Result ''' if counter < len(result_list) else ''))
            if user_selection.lower() == 'e':
                edit_entry(item)
            elif user_selection.lower() == 'd':
                delete_entry(item)
            elif user_selection.lower() == 's':
                return search_entries_menu()
            elif user_selection.lower() == 'n':
                user_selection == None  
                clear_screen()          
        counter += 1
    print("End of search results\n")
    search_entries_menu()

def search_entries_menu():
    """Search for specified value"""
    clear_screen()
    print("""
    Search by...
    1: Name
    2: Task Length
    3: Date
    4: Search Term
    5: Back to menu
    """)
    user_input = input(">>>  ")

    if user_input == '1':
        name_search()
    elif user_input == '2':
        time_search()
    elif user_input == '3':
        date_search()
    elif user_input == '4':
        exact_search()
    elif user_input == '5':
        user_menu()

def date_list(date_entered): # Allows for usage in program by acting as a list
    while len(date_entered) == 0:
        try:
            date_input = input("Please enter the date:  ")
            date_entered.append(datetime.datetime.strptime(date_input, '%m/%d/%Y'))
        except ValueError:
            print("Please enter the date in a MM/DD/YYYY format.")

def exact_search():
    search = None
    search_result = []
    print("Enter text to be searched")
    while search is None or search.isspace():
        search = input(">>  ")
        if search.strip() == '':
            print("Please enter text to be searched.")
            search = None
    query = Entry.select().where((Entry.task_name.contains(search)) | (Entry.add_notes.contains(search)))
    for res in query:
        search_result.append(res)
    if len(search_result) == 0:
        print("\nNo results found.\n")
        search_entries_menu()
    else:
        print("Number of results = " + str(len(search_result)))
        view_entries(search_result)

def name_search():
    names = Entry.select().order_by(Entry.user_name.asc())
    users = []
    count = 1
    for name in names:
        if name.user_name not in users:
            users.append(name.user_name)
    print("Pick from the following to see the entry(ies)")
    for human in users:
        num_entries = Entry.select().where(Entry.user_name == human).count()
        print(str(count) + ": " + human + " (" + str(num_entries) + ")")
        count += 1
    selection = None
    while not selection:
        print("Enter a number to the corresponding entry")
        selection = input(">>  ")
        try:
            selection = int(selection)
        except ValueError:
            print("Please enter a valid number")
            selection = None
        else:
            if selection > len(users):
                print("Please enter a valid number {}".format(' between 1 and {}'.format(len(users) if len(users) >1 else '.')))
                selection = None
    search_result = []
    query = Entry.select().where(Entry.user_name == users[selection - 1])
    for result in query:
        search_result.append(result)
    view_entries(search_result)

def time_search():
    search_res = []
    search_time = int(input("Please enter time to the nearest minute:  "))
    query = Entry.select().where(Entry.task_time == search_time)
    for result in query:
        search_res.append(result)
    if len(search_res) == 0:
        print("\nNo matches found.\n")
        search_entries_menu()
    else:
        view_entries(search_res)

def date_search():
    first_search_date = []
    second_search_date = []
    searched = None
    while not searched:
        clear_screen()
        searched = input("""
        Please enter 
        1: to browse all dates 
        2: to find within a range of two dates
        >>>   """)
        if searched not in ['1' , '2']:
            print("Not a valid selection. Please enter 1 or 2.")
            searched = None
    if searched == '2':
        print("Please enter a beginning date in MM/DD/YYYY format")
        date_list(first_search_date)
        print("Please enter an end date in MM/DD/YYYY format")
        while not second_search_date:
            date_list(second_search_date)
            if first_search_date[0] > second_search_date[0]:
                print("The first date cannot be later than the second date. Please enter end date again")
                second_search_date = []
    results = []
    entries = Entry.select().order_by(Entry.timestamp.asc())
    if searched == '2':
        entries = entries.where(Entry.timestamp >= first_search_date[0].timestamp())
        entries = entries.where(Entry.timestamp <= second_search_date[0].timestamp())
    if not entries.count():
        print("No results found.")
        search_entries_menu()
    else:
        entry_dates = []
        count = 1
        for entry in entries:
            if entry.timestamp not in entry_dates:
                entry_dates.append(entry.timestamp)
        print("Choose a date to see it's entries")
        for date in entry_dates:
            all_date_entries = Entry.select().where(Entry.timestamp == str(date)).count()
            print(str(count) + ": " + str(date) + " (" + str(all_date_entries) + " entry(ies))")
            count += 1 
    user_selection = None
    print("Enter the number corresponding to desired date.")
    while not user_selection:
        user_selection = input(">> ")
        try:
            user_selection = int(user_selection)
        except ValueError:
            print("Please select a valid number")
            user_selection = None
        else:
            if user_selection > len(entry_dates) or user_selection < 0:
                print("Please select from 1 to {}".format(len(entry_dates) if len(entry_dates) > 1 else '.'))
                user_selection = None
        end_results = []
        user_query = Entry.select().where(Entry.timestamp == str(entry_dates[user_selection - 1]))
        for result in user_query:
            end_results.append(result)
        view_entries(end_results)

def edit_entry(result_list):
    dict_header = {'1': 'user_name', '2': 'task_name', '3': 'task_time', '4': 'add_notes', '5': 'timestamp'}
    user_field = None
    while not user_field:
        user_field = input('''
            Select what field to edit:
            1: Name
            2: Task Name
            3: Task Length
            4: Task Notes
            5: Task Dates
            6: Go back to search results
            7: Go back to main menu\n
            >>  ''')
        if user_field == '6':
            return
        if user_field == '7':
            return search_entries_menu()
    new_entry = None
    while not new_entry:
        new_entry = input("Enter new {}: ".format(dict_header[user_field]))
        if new_entry.isspace():
            new_entry = None
            continue
        if user_field == '3':
            try:
                new_entry = int(new_entry)
            except:
                print("Please enter a valid number")
                new_entry = None
            else:
                new_entry = str(new_entry)
        if user_field == '5':
            try:
                datetime.datetime.strptime(new_entry, '%m/%d/%Y')
            except ValueError:
                print("Dates need to be valid and in MM/DD/YYYY format")
                new_entry = None
    if user_field == '1':
        query = Entry.update(user_name=new_entry).where(Entry.id == result_list.id)
    elif user_field == '2':
        query = Entry.update(task_name=new_entry).where(Entry.id == result_list.id)
    elif user_field == '3':
        query = Entry.update(task_time=new_entry).where(Entry.id == result_list.id)
    elif user_field == '4':
        query = Entry.update(add_notes=new_entry).where(Entry.id == result_list.id)
    else:
        query = Entry.update(timestamp=new_entry).where(Entry.id == result_list.id)
    query.execute()
    print("\nEdited!\n") 

def delete_entry(row):
    """Allows user to delete an entry/field"""
    print("Do you want to delete this? [Yn]?")
    confirm_del = input(">>  ")
    if confirm_del.lower() == 'y':
        table_row = Entry.get(Entry.id == row.id)
        table_row.delete_instance()
        print("Deleted.\n")
    else:
        print("Deletion canceled\n")



if __name__ == "__main__":
    initialize()
    user_menu()
    