asana-agenda
============

Asana agenda generator - for Berlin Geekettes Hackathon, October 2013

The program currently:
* grabs all tasks with the tag meeting_tag_name that are within the workspace workspace_name (hard coded)
* collects task names with assignee and due date
* uses Project names as headings
* exports the collected information to a text file named "<date> <tag name> Agenda"

Things left to do:
* sort the tasks so that they are displayed 
    a) in project groups 
    b) in the order they appear in Asana instead of the order in which the tag was added
* send the file as an email
* set the program up so that it is executed once a week
* make a gui for setup (eg: what tag to be used, what title for the meeting, what information to be included, and how to format it)
