# Legionnaire Bot

## This is a bot created for BitCraft resource management by Lanidae, Benevo, and Cj from The Legion.


## Requests Commands

### These commands handle individual resource requests

### $request \<resource\>

	This command will enter a new request into the database. Try to keep the thing you're requesting short, under 40 characters.

	Example: $request 50 T1 Planks

### $claim \<request id\>

	This command will have you claim a request, saying you will be the one to complete it.

	Example : $claim 72

### $complete \<request id\>

	This command will complete a request you have claimed. If you have not claimed the request, it will not complete it.

	Example : $complete 72

### $requests

	This command shows all of the requests that you have made and that have not been completed yet.

### $claims

	This commands shows all of the requests you have claimed and not completed yet.

### $requestlist

	This shows all uncompleted requests.


## Project Commands

### These commands handle larger scale, group-oriented projects.

### $newProject \<name\>

	This command creates a new project with the name set in the command.

### $listProjects

	This command lists all active projects in the server along with their Project IDs.
	Project IDs are how most commands will access a particular project.

### $addResource \<pid\> \<count\> \<name\>

	This command adds a resource to be completed to a specific project.

	Example: $addResource 1 50 T1 Wood Planks

### $removeResource \<pid\> \<name\>

	This command removes a resource from a specific project, in case you add something in error.

	Example: $removeResource 1 T1 Wood Planks

### $getResources \<pid\>

	This command retrieves the list of resources for a particular project.

### $contribute \<pid\> \<count\> \<name\>

	This command marks you as having added <count> resources to the project.

	Example: $contribute 1 10 T1 Wood Planks

### $getContributors \<pid\>

	This command returns a list of everyone who has made a contribution to a specific project.

### $getContributions \<pid\>

	This command returns a list of what contributions each person made to a specific project.

### $finishProject \<pid\>

	This command marks a project as completed.

	NOTE: Most project commands will not work once a project has been marked as completed, and the project will stop showing up in $listProjects.

	Make sure you are done with the project before using this command.