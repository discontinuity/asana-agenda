# automated generation of meeting agenda based on tags
# using Asana tasks and projects
# python2.7 script I think...
# left to do: 
#    well, the items are ordered based on when the meeting tag was added, not nicely by order within project or anything like that. So I need to fix that.
#    ideally make it possible to sort by anything
#    something key for these two is creating containers for each task then sorting those containers by project.
#    make it easier to change the formatting for the items?
#    error handling
#    automated running of the script
#    automated emailing


import json, os, sys, time, urllib2
from datetime import date
from urllib import urlencode

#task fields are: assignee, assignee_status (inbox, later, today, upcoming), created_at, completed (should be false for usss), due_on, followers, modified_at, name, notes, projects, parent, workspace (shouldn't need to use this since workspace is defined below)
# except that api/workspaces/<wsid>/tags/<tagid> doesn't work the way I hoped :/ You seem to only be able to return the info about one specific id. Which I guess makes sense. dunno. Anyway, for now I'm going to just do a check of the returned tasks workspaces after collecting them to make sure I'm only compiling an email with tasks from allowed workspaces. This is added in BELOW instead of being included in the task fields. Just because, don't ask why.
task_fields = "name,assignee,due_on,projects"
meeting_tag_name = "Meeting"
workspace_name = "Adina's Team!" #should be whatever workspace is shared. Personal here for example use only
api_key = "2jj5oZMd.owh3Upf4UjCTj6XkQK7LCLx"
asana_URL = "https://app.asana.com/api/1.0/"

def format_task(rttsk, level):
	formatted ='\n'

	# manage indentation and bullets
	stdindent = '     '
	nl = '\n' + stdindent
	if level == 1: #indent further on level 1 than level 0
		nl += '   '
		formatted += '      - '
	else: formatted += ' * '
	# name
	formatted += rttsk['name'] + ': '

	# due date
	if rttsk['due_on'] is not None:
		formatted += 'Due on ' + rttsk['due_on'] + ', '
	#else: formatted += 'No set due date'

	if rttsk['assignee'] is not None:
		asn = asana_query(api_key, 'users/' + str(rttsk['assignee']['id']) + '?opt_fields=name')
		formatted += 'Assigned to ' + asn['data']['name']
	else:
		formatted += 'Assigned to: No one...'
	return formatted

#curl -u 2jj5oZMd.owh3Upf4UjCTj6XkQK7LCLx: https://app.asana.com/api/1.0/tags/8140031762252/tasks?opt_pretty

#asana_query is by github.com/Aulos
def asana_query(asana_key, path, data=None, method=None):
    if type(path) is not str:
        path = '/'.join(path)
    url = asana_URL + path
    req = urllib2.Request(url, data)
    req.add_header('Authorization', 'Basic ' + (asana_key + ':').encode('base64').rstrip())
    if method is not None:
        req.get_method = lambda: method
    try:
        return json.loads(urllib2.urlopen(req).read())
    except urllib2.HTTPError as e:
        return {'error': str(e)}

def find_id_in_dict(d, name):
    return [v['id'] for v in d if v['name'] == name]

# make sure the workspace and meeting tag you've defined exist, and figure out what the ID number is

workspaces = asana_query(api_key, 'workspaces')
workspace_id_list = find_id_in_dict(workspaces['data'], workspace_name)
workspace_id = str(workspace_id_list[0])
if not workspace_id:
	print('Workspace ' + workspace_name + ' not found!')
# note: implement something better than printing a thing!

tags = asana_query(api_key, 'workspaces/' + workspace_id + '/tags')
meeting_tag_id = find_id_in_dict(tags['data'], meeting_tag_name)
meeting_tag_id = str(meeting_tag_id[0])
if not meeting_tag_id:
	print 'meeting_tag_name ' + meeting_tag_name + " not found"
# failure should mean more than printing a thing

# grab all the tasks, including requested data for the email
tasks_raw = asana_query(api_key, 'tags/' + meeting_tag_id + '/tasks?opt_fields=workspace,' + task_fields)

#go through each task, check if it's right, format it correctly, check for subtasks, format them correctly, etc.

#start by writing it to file
today = date.today()
filename = str(today) + ' Agenda ' + workspace_name
open(filename, 'w')
append = open(filename,'a')

#generate a header to begin with
header = 'Draft agenda for this ' + workspace_name + ' planning call\n'
header = header + 'Date/Time: ' + str(today) + '\n'
append.write(header)

#go through each task returned

project = ''
for returned_task in tasks_raw['data']:
	# if it's in the right workspace, spit the data out to a file, then check for subtasks
	if returned_task['workspace']['id'] == int(workspace_id):
		rt_proj = returned_task['projects'][0]['id']
		if not rt_proj == project:
			project = rt_proj
			append.write('\n')
			proj_name = asana_query(api_key, 'projects/' + str(project))
			append.write(proj_name['data']['name'] + ':')
		#if 
		append.write(format_task(returned_task,0))

		rt_subs = asana_query(api_key, 'tasks/' + str(returned_task['id']) + '/subtasks?opt_fields=workspace,' + task_fields) #query for subtasks
		rt_subs = rt_subs['data'] # be careful, this returns a set instead of a dict, that's why there's a rt_subs[0] two lines below. Except if you don't get any results, in which case it's an empty listy thingy/dict ([]). I don't even know.
		if not not rt_subs: #see if you got anything then write it if you did
			append.write(format_task(rt_subs[0],1))
		

