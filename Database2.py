import json
from Database import *
#from server import *

#Structures
class Group:
	def __init__(self, gid, name):
		self.gid = gid
		self.name = name

class Post: 
	def __init__(self, pid, subject, body, userid, gname, time):
		self.pid = pid
		self.subject = subject
		self.body = body
		self.userid = userid
		self.time = time
		self.gname = gname

	def getTimeStamp(self):
		return 0.1
        
    
def saveDiscussionGroupsAndPosts(groups, posts):
    for group in groups:
        addDiscussionGroup(group.name)

    for post in posts:
        addPost(post.gname, post.subject, post.userid, post.time, post.body)
        
def appendPost(post):
    addPost(post.gname, post.subject, post.userid, post.time, post.body)
        
    
        
def loadDiscussionGroups():
    groups = getDiscussionGroupNames()
    groupObjects = []
    
    x = 0
    for group in groups:
        g = Group(x, group)
        x+=1
        groupObjects.append(g)
        
    return groupObjects

def loadPosts():
    groupNames = getDiscussionGroupNames()

    posts = []
    
    x = 0
    for groupName in groupNames:
        group = getDiscussionGroup(groupName)
        
        for post in group['posts']:
            p = Post(x, post['subject'], post['post'], post['author'], groupName, post['timeStamp'])
            x+=1
            posts.append(p)
    
    return posts

groups = loadDiscussionGroups()
posts = loadPosts()

saveDiscussionGroupsAndPosts(groups, posts)