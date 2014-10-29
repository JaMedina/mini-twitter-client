mini-twitter-client
===================

#Requirements
* python3
* urllib
	+ pip install urllib
* httplib2
	+ pip install httplib2
* xmltodict
 	+ pip install xmltodict
* pudb
	+ pip install pudb
	
# Usage
```
    $ python mini-twitter-client.py
```

# Commands

* **login**
	- Usage: login {@username}
	- Login into the system using yout username
* **create**
	- Usage: create {@name} {@username}
	- Creates an account in the system, Requires your name and username.
* **users** Goes into the users sub-menu
  * **followers**
  	* Usage: followers
  	* Prints the list of users that are following the current user
  * **following**
  	* Usage: following
  	* Prints the list of users that the current user ia following
  * **follow**
  	* Usage: follow {@username to follow}
  	* Creates a new folllowee for the current user
  * **unfollow**
  	* Usage: unfollow {@username to unfollow}
  	* Deletes the specified folllowee for the current user
  * **list**
  	* Usage: list
  	* Prints the list of the current users of the application
	
* **tweets** Goes into the tweets sub-menu
  * **tweet**
  	* Usage: add @message}"
  	* Adds a new tweet in the user timeline. NOTE @message must be between quotes.
  * **timeline**
  	* Usage: timeline {@filter}
  	* hows the user timeline. Pass an extra argunemt to filter tweets (optional)
  	* NOTE: If you want to search a whole sentence please use " at the begining and at the end

* **quit** | **exit** 
	- Usage: quit
	- Exits the mini twitter client.
* **logout**
	- Usage: logout
	- Terminates the session od the current user.
* **back**
	- Usage: back
	- Returns to the main menu. Only available when inside the tweets or the users menu.

