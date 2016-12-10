import json, os, datetime

################################################################# CLIENT SIDE ############################################################################
# user json object:
    # uid: The user id 
    # discussionGroups: Array of discussion groups that this user is subscribed to

# discussionGroup json object:
    # name: The name of the discussion group
    # readPosts: An array of post names that the user has already read


# Path to the users json file
userHistoryFilePath = './users.json'

# Add a new user to the users json file with the specified uid, name
def addUser(name):
    # Create a new user json object
    newUser = {
        'uid' : name,
        'discussionGroups' : []
    }
    
    # If the file does not exist or it is empty, then create a new json array to hold the user objects
    if (not(os.path.isfile(userHistoryFilePath))) or (os.stat(userHistoryFilePath).st_size == 0):
        data = {}
        data['users'] = []
    # Otherwise load in the array from the json file
    else:
        with open(userHistoryFilePath, 'r') as f:
            data = json.load(f)
        f.close()
        
    # Add the new user to the users array
    data['users'].append(newUser)

    # Write the newly updated json array back to the file
    with open(userHistoryFilePath, 'w') as f:
        json.dump(data, f)
    f.close()

# Add a new discussion group to a specified user
def addDiscussionGroup(uid, discussionGroup):
    # Create new discussion group json object
    newDiscussionGroup = {
        'name' : discussionGroup,
        'readPosts' : []
    }
    
    # Open the json file and read the data from it
    with open(userHistoryFilePath, 'r') as f:
        data = json.load(f)
    f.close()
    
    userFound = 0
    # Loop through all of the users until the specified one is found
    for user in data['users']:
        if(user['uid'] == uid):
            user['discussionGroups'].append(newDiscussionGroup)
            userFound = 1
            break
    
    # If the specified user was not found, return an error
    if(userFound == 0):
        return -1
    
    # Rewrite the newly updated user array back to the file
    with open(userHistoryFilePath, 'w') as f:
        json.dump(data, f)
    f.close()
 
 # Add a post to the specified user's specified discussionGroup
def addReadPost(uid, discussionGroupToFind, post):
    # Load in the data from the json file
    with open(userHistoryFilePath, 'r') as f:
        data = json.load(f)
    f.close()
    
    discussionGroupFound = 0
    # Find the user specifed by uid and then find the discussionGroup specified by discussionGroup and put the post in there
    for user in data['users']:
        if(user['uid'] == uid):
            for discussionGroup in user['discussionGroups']:
                if(discussionGroup['name'] == discussionGroupToFind):
                    discussionGroup['readPosts'].append(post)
                    discussionGroupFound = 1
                    break
            break
            
    # If the post was not placed, return an error
    if(discussionGroupFound == 0):
        return -1
    
    # Write the data back to the file after it is updated
    with open(userHistoryFilePath, 'w') as f:
        json.dump(data, f)
    f.close()

# Return the list of discussion groups for a specified user    
def getDiscussionGroups(uid):
    # Open the json file and load the data
    with open(userHistoryFilePath, 'r') as f:
        data = json.load(f)
    f.close()
    
    # Look for the user specified by uid and if found, return it's list of discussion groups. Otherwise, return -1
    for user in data['users']:
        if(user['uid'] == uid):
            return user['discussionGroups']
    
    return -1

# Get the list of read posts for a given user and discussion group
def getReadPosts(uid, discussionGroupToFind):
    # Open the json file and load the data
    with open(userHistoryFilePath, 'r') as f:
        data = json.load(f)
    f.close()
    
    # Look for the specified user and discussion group. If found return it's list of read posts, otherwise return -1
    for user in data['users']:
        if(user['uid'] == uid):
            for discussionGroup in user['discussionGroups']:
                if(discussionGroup['name'] == discussionGroupToFind):
                    return discussionGroup['readPosts']
    return -1

# Find a user specified by user and if it is found, return it. Otherwise return -1
def getUser(uid):
    try:
        # Open the json file and load the data
        with open(userHistoryFilePath, 'r') as f:
            data = json.load(f)
        f.close()

        # Loop through the users array to find the user that has a uid that matches uid. If it is not found, -1 is returned.
        for user in data['users']:
            if(user['uid'] == uid):
                return user
    except ValueError:
        return -1
    
    return -1

############################################################# SERVER SIDE #################################################################################
# The path to the folder of discussion groups
discussionGroupsFilePath = './DiscussionGroups/'

# Add a new discussion group to all of the discussion groups. Each discussion group will be a json file in the directory containing all of the posts
def addDiscussionGroup(dicussionGroupName):
    newFilePath = discussionGroupsFilePath + dicussionGroupName + '.json'
    
    data = {}
    data['discussionGroups'] = []
    
    with open(newFilePath, 'w') as f:    
        json.dump(data,f)
    f.close()
    
# Add a new post to a specified discussion group.
def addPost(discussionGroupName, postSubject, postAuthor, postContent):
    # Make sure to change this to non hard coded timezone unless it doesn't matter
    newPost = {
        'subject' : postSubject,
        'author' : postAuthor,
        'timeStamp' : str('{:%a, %b %d %X %ZEST %Y}'.format(datetime.datetime.now())),
        'post' : postContent
    }
    
    discussionGroupPath = discussionGroupsFilePath + discussionGroupName + '.json'
    
    try:
        with open(discussionGroupPath, 'r') as f:
            data =  json.load(f)
        f.close()
    except ValueError:
        print 'Error reading data!'
        return -1
    
    data['discussionGroups'].append(newPost)
    
    with open(discussionGroupPath, 'w') as f:
        json.dump(data, f)
    f.close()

def getDiscussionGroup(discussionGroupName):
    discussionGroupPath = discussionGroupsFilePath + discussionGroupName + ".json"
    
    try:
        with open(discussionGroupPath, 'r') as f:
            data = json.load(f)
        f.close()
    except ValueError:
        print 'Error reading data!'
        return -1
    
    return data

def getPost(discussionGroupName, postSubject):
    data = getDiscussionGroup(discussionGroupName)
    
    if(data == -1):
        return -1
    
    for post in data:
        if(post['subject'] == postSubject):
            return post
