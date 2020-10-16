# DESIGN

The summit table contains contains six fields: user_id, list_id, task, complete, task_id, and priority.
The user_id enables tracking of which session the website is currently in with respect to the user.
List_id gives the list under which the goals and tasks are inputted, which is also associated to the listname.
Tasks inputted are stored within task, and displayed under the appropriate list_id.
Task complete indicates whether or not the task has been fulfilled (but would still like to be displayed).

The user table stores the login information of registered users, including username, password (hashed), and date joined.
The user_id "id" allows for easy access to the user when referencing it later on.

The newsletter table stores emails inputed through the footer email subscription.
This is executed through the email function within application.py, which inserts it into newsletter and notifies the user.

The lists table stores the ids and names of each list existing for global access among the different app routes. In future
models of this website, you could implement functionality allowing for the creation of new lists, specific to the user.

The overview page selects all of the lists and todos and displays them.
Rather than having independent functions and app routes for each list, a general list function was created.
It takes in the list_id and generates from there the path for the specified list and names associated.
The todos, listname, and list_id rendered in list.html will be changed accordingly.
This design choice was also made to avoid making too many different html templates for each page, since the individual list pages for goals look the same.

The layout.html pages (1 and 2) were created to easily extend the other pages to.
These contain the formatting of the page and various texts, including the menu bar/side panel, header, and footer.
The side menu utilized the class="pushy pushy-left", and jinja for going through all the list names and looping breaks.
The layouts utilize bootstrap and primarily the styles.css for styling.
Flashed messages in addition to displaying error images were used with error handling, in different contexts of generated errors.

Social media icons are located within the footer, which link to external addresses including Youtube! :)