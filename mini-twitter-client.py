import sys, getopt
import cmd
import string, sys
import urllib
import urllib.parse
import httplib2
import time
import datetime
import shlex
import xml.dom.minidom
import json
import xmltodict

MAIN_PROMPT="Login $"
JSON_MEDIA_TYPE="application/json"
XML_MEDIA_TYPE="application/xml"
HOST="jbossews-rameseum.rhcloud.com"
CONTENT_TYPE=JSON_MEDIA_TYPE
TOKEN=None

##### Utility functions #####
def split(value):
	lex = shlex.shlex(value)
	lex.quotes = '"'
	lex.whitespace_split = True
	return list(lex)

def buildUrl(restUrl):
	return "http://"+HOST+"/"+restUrl

def prettyResponse(content):
	prettyContent = content.decode()
	try:
		if CONTENT_TYPE == XML_MEDIA_TYPE:
			xmlContent = xml.dom.minidom.parseString(content.decode())
			prettyContent = xmlContent.toprettyxml()
		if CONTENT_TYPE == JSON_MEDIA_TYPE:
			prettyContent = json.loads(content.decode())
	except Exception as e:
		prettyContent = content

	return prettyContent
##### Utility functions #####

##### Request Calls #####
def doPost(restUrl, params = {}, body={}):
	return doHttpRequest(restUrl, "POST", params)

def doGet(restUrl,params = {}, body={}):
	return doHttpRequest(restUrl,"GET",params)

def doDelete(restUrl,params = {}, body={}):
	return doHttpRequest(restUrl,"DELETE",params)

def doHttpRequest(restUrl, method, params = {}, body = {}):
	global TOKEN

	url = buildUrl(restUrl)

	if TOKEN is not None:
		params["token"] = TOKEN['token']
		params["username"] = TOKEN['user']['username']

	if params is not None and len(params) > 0:
		url += "?" + urllib.parse.urlencode(params)

	headers = {
		"Content-Type": CONTENT_TYPE,
		"Accept": CONTENT_TYPE
	}

	print ("Trying: ["+method+"]" + url)

	http = httplib2.Http(".cache")
	resp, content = http.request(url, method, headers=headers, body=body)

	content = prettyResponse(content)
	return content
##### Request Calls #####

class ClientCommand(cmd.Cmd):
	def getArgumentsList(self, arg, minimumNumberOfArguments, maximumNumberofArguments = None):
		argumentList = split(arg)
		argumentCount = len(argumentList)

		if maximumNumberofArguments is None:
			maximumNumberofArguments = minimumNumberOfArguments

		if argumentCount < minimumNumberOfArguments:
			raise Exception("The number of arguments is not correct. It was expected "+ str(minimumNumberOfArguments) + " but received " + str(len(argumentList)))
			return
		if argumentCount > maximumNumberofArguments:
			raise Exception("The number of arguments is not correct. It was expected "+ str(maximumNumberofArguments) + " but received " + str(len(argumentList)))
			return

		for index, item in enumerate(argumentList):
			argumentList[index] = item.replace('"','').strip()

		return argumentList

	def tokenExists(self):
		isValid = TOKEN is not None
		if not isValid:
			raise Exception("You need to login before in order to continue")
		return isValid

	def precmd(self, line):
		try:
			isTokenNeeded = True
			for action in ["login","back","exit","quit","logout", "create", "help", "json","xml"]:
				if line.startswith( action ):
					isTokenNeeded = False
					break

			if isTokenNeeded :
				self.tokenExists()
			return cmd.Cmd.precmd(self,line)
		except Exception as e:
			print(str(e))
			return ""

	def onecmd(self, line):
		try:
			return cmd.Cmd.onecmd(self,line)
		except Exception as e:
			print(str(e))

	def do_xml(self, arg):
		global	CONTENT_TYPE
		CONTENT_TYPE = XML_MEDIA_TYPE
		print ("Receiving responses in XML fomat")

	def do_json(self, arg):
		global CONTENT_TYPE
		CONTENT_TYPE = JSON_MEDIA_TYPE
		print ("Receiving responses in JSON fomat")

	def help_xml(self):
		print ("Usage: xml")
		print ("\t This action will cause taht all the resposnes will be received in XML format")

	def help_json(self):
		print ("Usage: json")
		print ("\t This action will cause taht all the resposnes will be received in JSON format")

	def help_host(self):
		print ("Switch the host to with the request will de send")
		print ("\t Example: python mini-twitter-client.py --host jbossews-rameseum.rhcloud.com")

class SubPrompt(ClientCommand):
	def do_back(self, arg):
		return "stop"

	def help_back(self):
		print("Usage: back")
		print("\t  Returns to the main menu.") 

class UserCommandSubMenu(SubPrompt):
	def do_followers(self, arg):
		global TOKEN
		argumentList = self.getArgumentsList(arg, 0)
		followers = doGet("rest/follow/"+TOKEN['user']['username'])
		print(followers)

	def do_following(self, arg):
		global TOKEN
		argumentList = self.getArgumentsList(arg, 0)
		following = doGet("rest/followee/"+TOKEN['user']['username'])
		print (following)

	def do_follow(self, arg):
		global TOKEN
		argumentList = self.getArgumentsList(arg, 1)
		params = {'followeeUsername': argumentList[0]}
		result = doPost("rest/follow", params)
		print (result)

	def do_unfollow(self, arg):
		global TOKEN
		argumentList = self.getArgumentsList(arg, 1)
		result = doDelete('rest/follow/'+TOKEN['user']['username']+'/'+argumentList[0])
		print (result)

	def do_list(self, arg):
		global TOKEN
		users = doGet("rest/users")
		print (users)

	def help_followers(self):
		print ("Usage: followers")
		print ("\t Prints the list of users that are following the current user")

	def help_following(self):
		print ("Usage: following")
		print ("\t Prints the list of users that the current user ia following")

	def help_follow(self):
		print ("Usage: follow {@usernmae to follow}")
		print ("\t Creates a new folllowee for the current user")

	def help_unfollow(self):
		print ("Usage: unfollow {@usernmae to unfollow}")
		print ("\t Deletes the specified folllowee for the current user")

	def help_list(self):
		print ("Usage: list")
		print ("\t Prints the list of the current users of the application/")

class TweetCommandSubMenu(SubPrompt):
	def do_tweet(self, arg):
		global TOKEN
		argumentList = self.getArgumentsList(arg, 1)
		params = {'authorId': TOKEN['user']['id'], 'message': argumentList[0]}
		message = doPost("rest/tweets",params)
		print (message)

	def do_timeline(self, arg):
		argumentList = self.getArgumentsList(arg,0,1)
		params = {}
		if len(argumentList) == 1 :
			search = argumentList[0]
			params = {'filter': search}

		timeline = doGet("rest/tweets",params)
		print (timeline)

	def help_tweet(self):
		print ("Usage: add \"{@message}\"")
		print ("\t Adds a new tweet in the user timeline. NOTE @message must be between quotes.")

	def help_timeline(self):
		print ("Usage: timeline {@filter}")
		print ("\t Shows the user timeline. Pass an extra argunemt to filter tweets (optional)")
		print ("\t *NOTE: If you want to search a whole sentence please use \" at the begining and at the end")
		
class StartClient(ClientCommand):
	def __init__(self):
		cmd.Cmd.__init__(self)
		self.prompt = MAIN_PROMPT

	def postcmd(self, stop, line):
		global TOKEN
		if TOKEN is None:
			self.prompt = MAIN_PROMPT
		else:
			self.prompt = "Welcome "+TOKEN['user']['username']+"$"

	def do_create(self, arg):
		argumentList = self.getArgumentsList(arg, 2)
		params = {'name': argumentList[0], 'username': argumentList[1]}
		user = doPost("public/user",params)
		print (user)

	def do_login(self, arg):
		global TOKEN

		if TOKEN is not None:
			print ("Already loggedin. Logout first")
			return

		argumentList = self.getArgumentsList(arg, 1)
		params = {'username': argumentList[0]}
		token = doPost("public/login", params)
		if not token:
			token=None
		if CONTENT_TYPE == XML_MEDIA_TYPE:
			try:
				token = xmltodict.parse(token)['token']
			except Exception as e:
				print("")

		if 'token' in token and 'user' in token:
			TOKEN = token
		else:
			print(token)

	def do_logout(self, arg):
		global TOKEN
		doPost("rest/users/logout")
		TOKEN=None;

	def do_exit(self, arg):
		global TOKEN
		if TOKEN is not None:
			self.do_logout(arg)
		sys.exit(0)
    	
	def do_quit(self, arg):
		self.do_exit(arg)


	def do_users(self, arg):
		i = UserCommandSubMenu()
		i.prompt = self.prompt[:-1]+' --> Users $'
		i.cmdloop()
        
	def do_tweets(self, arg):
		i = TweetCommandSubMenu()
		i.prompt = self.prompt[:-1]+' --> Tweets $'
		i.cmdloop()

	def help_login(self):
		print ("Usage: login {@username}")
		print ("\t Login into the system using yout username")

	def help_create(self):
		print ("Usage: create {@name} {@username}")
		print ("\t Creates an account in the system, Requires your name and username.")

	def help_users(self):
		print ("Usage: users")
		print ("\t Go to the users sub-menu")

	def help_tweets(self):
		print ("Usage: tweets")
		print ("\t Go to the tweets sub-menu")

	def help_quit(self):
		print ("Usage: quit")
		print ("\t Exits the mini twitter client.")
    
	def help_logout(self):
		print ("Usage: logout")
		print ("\t Terminates the session od the current user.")

	def help_exit(self):
		print ("Usage: exit")
		print ("\t Exits the mini twitter client.")

def main(argv):
	global HOST
	opts, args = getopt.getopt(argv,"h",["host="])

	for opt, arg in opts:
		if opt  in ("-h", "--host"):
			HOST = arg

	console = StartClient()
	console.cmdloop()

if __name__ == '__main__':
	main(sys.argv[1:])  