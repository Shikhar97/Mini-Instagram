# List of friends of friends...
# ff_list = {
#     1 : [2, 4, 5],
#     2 : [1, 4],
#     3 : [4, 5],
#     4 : [1, 2, 3],
#     5 : [1, 3]
# }
 
def get_friend_suggestions(user_id,ff_list):
	'''
	@param user_id - currently logged in user
	Find the list of suggested friends for a user along with
	the friends that are mutual to the suggested friend.
	'''
	suggested_friends = {}
	# Get the friends of the current user.
	friends = ff_list[user_id]
 
	for friend in friends:
		# Friends friends list.
	    ffriends = ff_list[friend]
	    for ff in ffriends:
	    	# If the friendsFriend(ff) is not us, and not our friend, he can be suggested
	        if ff != user_id and ff not in friends:
	        	# The key is the suggested friend
	            suggested_friends[ff] = {'mutual_friends' : []}
	            for f in ff_list[ff]:
	            	# If he is a friend of the current user, he is a mutual friend
	                if f in friends:
	                    suggested_friends[ff]['mutual_friends'].append(f)
 
	return suggested_friends
 
# user_id_input = 2
# print("Suggested Friends and Mutual Friends for user {}".format(user_id_input))
# print(get_friend_suggestions(user_id_input))# your code goes here