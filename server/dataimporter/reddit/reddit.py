import praw

#unused for now
class Redditxxx:
    reddit = None

    def __init__(self):
        self.reddit = praw.Reddit(client_id='frV5DR2pJEab3g',
                             client_secret='rQ2XDxr3LnHoC__NikVwFVCCtJM',
                             user_agent='Python AlgoCryptos v2.0 /u/cysacenda',
                             username = 'cysacenda',
                             password= 'pirate00')
        # Test connexion, the next line should print the username logged in
        # print(self.reddit.user.me())

        subreddit = self.reddit.subreddit("ethereum")
        sinfos = subreddit.traffic()
        subreddit.traffic()


    def get_subreddit_infos(self, subreddit_name):
        subreddit = self.reddit.subreddit(subreddit_name)
        sinfos = subreddit.traffic()