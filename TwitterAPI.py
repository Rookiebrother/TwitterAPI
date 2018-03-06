import requests
import json
from bs4 import BeautifulSoup

class Twitter:
# START
    def __init__(self): # Constructor
        self.host = 'https://twitter.com/' # Twitter host web version
        self.mobileHost = 'https://mobile.twitter.com/' # Twitter host mobile version
        self.helpHost = 'https://help.twitter.com/' # Twitter Helping center host
        self.APIHost = 'https://api.twitter.com/' # Twitter API host
        self.session = None
        self.username = ''
        self.password = ''

    def initSession(self): # Initiate requests session with twitter
        self.session = requests.session()
        self.session.get(self.mobileHost)

    def isValidEmail(self, email): # [No login required] Check if Email are registered or not
        path = 'users/email_available?email=' + email
        response = requests.get(self.host + path)
        data = json.loads(response.text)
        return (data['valid'])

    def isValidUsername(self, username): # [No login required] Check if Username are registered or not
        path = 'users/username_available?username=' + username
        response = requests.get(self.host + path)
        data = json.loads(response.text)
        return (data['valid'])

    def isValidPhoneNumber(self, countryCode, phoneNumber): # [No login required] Check is valid phone number or not
        path = 'users/phone_number_available?raw_phone_number=' + countryCode + phoneNumber
        response = requests.get(self.host + path)
        data = json.loads(response.text)
        return (data['valid'])

    def usernameLookup(self, username): # [No login required] Get username country, block status, suspended status - limited requests
        path = 'api/v1/username_lookups?username=' + username
        response = requests.get(self.helpHost + path)
        data = json.loads(response.text)
        return data

    def getAuthenticityToken(self): # [Nothing required] - used for login also used in most twitter web services
        response = self.session.get(self.mobileHost)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.find("input", {'name': "authenticity_token"}).attrs['value']

    def setAuthorizationXCSRF(self): # [Nothing required] - do not change me please, you can get me from Cookie
        self.session.headers.update({
            'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'x-csrf-token': 'efd9310dfc384307332ce99ce853f4d9'
        })
        self.session.cookies.update({'ct0': 'efd9310dfc384307332ce99ce853f4d9'})

    def clearAuthorizationXCSRF(self): # [Nothing required] - do not change me please
        self.session.headers.update({
            'Authorization': '',
            'x-csrf-token': ''
        })
        self.session.cookies.update({'ct0': ''})

    def login(self, username, password): # [Nothing Required] Login using username and password
        self.initSession()
        self.username = username
        self.password = password
        path = 'sessions'
        payload = {
        'authenticity_token': self.getAuthenticityToken(),
        'session[username_or_email]': username,
        'session[password]': password,
        'redirect_after_login': '/home'
        }
        self.session.post(self.mobileHost + path, data = payload)
        if 'twid' in self.session.cookies:
            self.userID = self.session.cookies['twid']
            self.setAuthorizationXCSRF()
        else:
            raise Exception('Username or password is incorrect')

    def logout(self): # logout clear the Authorization and XCSRF
        self.clearAuthorizationXCSRF()

    def changePassword(self, password): # [Login Required] Change Password, you have to re-login
        path = 'i/account/change_password.json'
        payload = {
            'current_password': self.password,
            'password': password,
            'password_confirmation': password
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])
        self.password = password
        self.login(self.username, self.password)

    def changeEmail(self, email): # [Login Required] Change Email
        path = '1.1/account/settings.json'
        payload = {
            'include_mention_filter': 'true',
            'include_ranked_timeline': 'true',
            'email': email
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def changeUsername(self, username): # [Login Required] Change Username
        path = '1.1/account/settings.json'
        payload = {
            'include_mention_filter': 'true',
            'include_ranked_timeline': 'true',
            'screen_name': username
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])
        self.username = username

    def changeCountry(self, countryCode): # [Login Required] Change the country of your account
        path = '1.1/account/settings.json'
        payload = {
            'include_mention_filter': 'true',
            'include_ranked_timeline': 'true',
            'country_code': countryCode
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def deletePhoneNumber(self, phoneNumber): # [Login Required] Delete the phone number from your account
        path = '1.1/device/unregister.json'
        payload = {'phone_number': phoneNumber}
        response = self.session.post(self.APIHost + path, data = payload)
        try:
            data = json.loads(response.text)
            if 'errors' in data:
                raise Exception(data['errors'][0]['message'])
        except json.decoder.JSONDecodeError:
            pass

    def updateAndAddPhoneNumber(self, phoneNumber): # [Login Required] change the phone number to a new one or add a phone number
        path = '1.1/device/register.json'
        payload = {
            'raw_phone_number': phoneNumber,
            'send_numeric_pin': 'true',
            'notifications_disabled': 'true',
            'update_phone': 'true'
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            print(data)
            raise Exception(data['errors'][0]['message'])

    def activePhoneNumber(self, phoneNumber, pinCode): # [Login Required] Activate the phone number that you update or add it using updateAndAddPhoneNumber by applying the pinCode
        path = '1.1/device/register_complete.json'
        payload = {
            'numeric_pin': pinCode,
            'phone_number': phoneNumber,
            'notifications_disabled': 'true',
            'update_phone': 'true'
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def getConnectedApps(self): # [Login Required] return list of Connected apps with there tokens
        path = '1.1/oauth/list.json'
        response = self.session.get(self.APIHost + path)
        data = json.loads(response.text)
        return data['applications']

    def revokeApp(self, token): # [Login Required] revoke app return true if revoked else return false
        path = '1.1/oauth/revoke.json'
        payload = {'token': token}
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception('invalid token')

    def personalization(self): # [Login Required] get personalization data - logs history and creator details
        path = '1.1/account/personalization/p13n_data.json'
        response = self.session.get(self.APIHost + path)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception('invalid token')
        return data

    def personalInfo(self): # [Login Required] get your email and phone data
        path = '1.1/users/email_phone_info.json'
        response = self.session.get(self.APIHost + path)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception('invalid token')
        return data

    def tweet(self, text, attachmentUrl = ''): # [Login Required] tweet by using text parameter and attachment a tweet using the url
        path = '1.1/statuses/update.json'
        payload = {
            'tweet_mode': 'extended',
            'status': text
        }

        if attachmentUrl != '':
            payload.update({'attachment_url': attachmentUrl})

        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def retweet(self, tweetID): # [Login Required] retweet a tweet with tweet id
        path = '1.1/statuses/retweet.json'
        payload = {
            'tweet_mode': 'extended',
            'id': tweetID
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def unretweet(self, tweetID): # [Login Required] unretweet with tweet id
        path = '1.1/statuses/unretweet.json'
        payload = {
            'tweet_mode': 'extended',
            'id': tweetID
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def deleteTweet(self, tweetID): # [Login Required] delete a tweet from your account by the tweet id
        path = '1.1/statuses/destroy.json'
        payload = {
            'tweet_mode': 'extended',
            'id': tweetID
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def favoriteTweet(self, tweetID): # [Login Required] favorite a tweet by tweet id
        path = '1.1/favorites/create.json'
        payload = {
            'tweet_mode': 'extended',
            'id': tweetID
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def unfavoriteTweet(self, tweetID): # [Login Required] unfavorite a tweet by tweet id
        path = '1.1/favorites/destroy.json'
        payload = {
            'tweet_mode': 'extended',
            'id': tweetID
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def pinTweet(self, tweetID): # [Login Required] pin a tweet by tweet id
        path = '1.1/account/pin_tweet.json'
        payload = {
            'tweet_mode': 'extended',
            'id': tweetID
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def unpinTweet(self, tweetID): # [Login Required] unpin a tweet by tweet id
        path = '1.1/account/unpin_tweet.json'
        payload = {
            'tweet_mode': 'extended',
            'id': tweetID
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def follow(self, userID): # [Login Required] follow by entering the user id
        path = '1.1/friendships/create.json'
        payload = {
            'include_profile_interstitial_type': '1',
            'include_blocking': '1',
            'include_blocked_by': '1',
            'include_followed_by': '1',
            'include_want_retweets': '1',
            'skip_status': '1',
            'include_can_dm': '1',
            'include_mute_edge': '1',
            'id': userID
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def unfollow(self, userID): # [Login Required] unfollow by entering the user id
        path = '1.1/friendships/destroy.json'
        payload = {
            'include_profile_interstitial_type': '1',
            'include_blocking': '1',
            'include_blocked_by': '1',
            'include_followed_by': '1',
            'include_want_retweets': '1',
            'skip_status': '1',
            'include_can_dm': '1',
            'include_mute_edge': '1',
            'id': userID
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def editProfileName(self, name): # [Login Required] change your profile name
        path = '1.1/account/update_profile.json'
        payload = {
            'displayNameMaxLength': '50',
            'name': name
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def editProfileBio(self, bio): # [Login Required] change your profile description
        path = '1.1/account/update_profile.json'
        payload = {
            'displayNameMaxLength': '50',
            'description': bio
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def editProfileLocation(self, location): # [Login Required] change your profile location
        path = '1.1/account/update_profile.json'
        payload = {
            'displayNameMaxLength': '50',
            'location': location
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def editProfileWebsite(self, url): # [Login Required] change your profile website
        path = '1.1/account/update_profile.json'
        payload = {
            'displayNameMaxLength': '50',
            'url': url
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def getFollowing(self, userID): # [Login Required] return following data
        cursor = '-1'
        following = []
        while True:
            path = '1.1/friends/list.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&skip_status=1&cursor=' + cursor + '&user_id=' + userID + '&count=20'
            response = self.session.get(self.APIHost + path)
            data = json.loads(response.text)
            if 'errors' in data:
                raise Exception(data['errors'][0]['message'])
            for user in data['users']:
                following.append(user)
            if data['next_cursor'] == 0:
                return following
            cursor = data['next_cursor_str']

    def getFollowers(self, userID): # [Login Required] return followers data
        cursor = '-1'
        followers = []
        while True:
            path = '1.1/followers/list.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&skip_status=1&cursor=' + cursor + '&user_id=' + userID + '&count=20'
            response = self.session.get(self.APIHost + path)
            data = json.loads(response.text)
            if 'errors' in data:
                raise Exception(data['errors'][0]['message'])
            for user in data['users']:
                followers.append(user)
            if data['next_cursor'] == 0:
                return followers
            cursor = data['next_cursor_str']

    def getUserInfoByName(self, screen_name): # [Login Required] get user informations by screen name
        path = '1.1/users/show.json?screen_name=' + screen_name
        response = self.session.get(self.APIHost + path)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])
        return data

    def getUserInfoByID(self, userID): # [Login Required] get user informations by user id
        path = '1.1/users/show.json?user_id=' + userID
        response = self.session.get(self.APIHost + path)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])
        return data

    def tweetLookup(self, tweetID): # [Login Required] get tweet information
        path = '1.1/statuses/lookup.json?id=' + tweetID
        response = self.session.get(self.APIHost + path)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])
        return data

    def tweetSearch(self, query, options = ''): # [Login Required] stantard search get result based on query ( https://developer.twitter.com/en/docs/tweets/search/guides/standard-operators ) , options ( https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets )
        path = '1.1/search/tweets.json?q=' + query + options
        response = self.session.get(self.APIHost + path)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])
        return data

    def sendDirectMessageSN(self, screenName, text): # [Login Required] send Direct Message using screen name
        path = '1.1/direct_messages/new.json'
        payload = {
            'text': text,
            'screen_name': screenName
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def sendDirectMessageID(self, userID): # [Login Required] send Direct Message using user id
        path = '1.1/direct_messages/new.json'
        payload = {
            'text': text,
            'user_id': userID
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def reportSpamSN(self, screenName): # [Login Required] report user for spam by user id
        path = '1.1/users/report_spam.json'
        payload = {
            'screen_name': screenName,
            'perform_block': 'true'
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def reportSpamID(self, userID): # [Login Required] report user for spam by screen name
        path = '1.1/users/report_spam.json'
        payload = {
            'user_id': userID,
            'perform_block': 'true'
        }
        response = self.session.post(self.APIHost + path, data = payload)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])

    def getLocationsTrends(self): # [Login Required] Get locations with trending topics - Returns the locations that Twitter has trending topic information for.
        path = '1.1/trends/available.json'
        response = self.session.get(self.APIHost + path)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])
        return data

    def getClosestTrends(self, lat, lon): # [Login Required] Get locations with trending topics - Returns the locations that Twitter has trending topic information for, closest to a specified location.
        path = '1.1/trends/closest.json?lat=' + lat + '&long=' + lon
        response = self.session.get(self.APIHost + path)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])
        return data

    def getTrends(self, ID = '1'): # [Login Required] Global information is available by using 1 as the WOEID . return trends id is The Yahoo! Where On Earth ID of the location to return trending information for.
        path = '1.1/trends/place.json?id=' + ID
        response = self.session.get(self.APIHost + path)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])
        return data

    def retweetedBy(self, tweetID): # [Login Required] return users data who retweets it ( problem need to load the next users )
        path = '2/timeline/retweeted_by.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_reply_count=1&tweet_mode=extended&include_entities=true&include_user_entities=true&include_ext_media_color=true&send_error_codes=true&tweet_id=' + tweetID + '&count=200'
        response = self.session.get(self.APIHost + path)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])
        return data

    def likedBy(self, tweetID): # [Login Required] return users data who liked the tweet ( problem need to load the next users )
        path = '2/timeline/liked_by.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_reply_count=1&tweet_mode=extended&include_entities=true&include_user_entities=true&include_ext_media_color=true&send_error_codes=true&tweet_id=' + tweetID + '&count=200'
        response = self.session.get(self.APIHost + path)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])
        return data

    def getTweetConversation(self, tweetID): # [Login Required] return all tweet conversation ( problem need to load the next users )
        cursor = ''
        path = '2/timeline/conversation/' + tweetID + '.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_reply_count=1&tweet_mode=extended&include_entities=true&include_user_entities=true&include_ext_media_color=true&send_error_codes=true&count=200'
        tweets = []
        response = self.session.get(self.APIHost + path + cursor)
        data = json.loads(response.text)
        if 'errors' in data:
            raise Exception(data['errors'][0]['message'])
        for tweet in data['globalObjects']['tweets']:
            tweets.append(tweet)
        return tweets

    # Start Filters

        # users filters
    def getUserName(self, user): # Return user name
        return user['name']

    def getScreenName(self, user): # Return user screen name
        return user['screen_name']

    def getLocation(self, user): # Return user location
        return user['location']

    def getCreatedAt(self, user): # Return user creation date and time
        return user['created_at']

    def getImg(self, user): # Return user image
        imgs = []
        for user in users:
            imgs.append(user['profile_image_url'])
        return imgs

    def getID(self, user): # Return user ID
        return str(user['id'])
        # users filters

        # personalization filters
    def getCreator(self, personal): # get sing up details
        return personal['sign_up_details']

    def getLogs(self, personal): # get logs history
        return personal['sign_up_details']
        # personalization filters

        # personalInfo filters
    def getEmails(self, personal): # get emails that are linked to the account
        return personal['emails']

    def getPhoneNumbers(self, personal): # get phone numbers that are linked to the account
        return personal['phone_numbers']
        # personalInfo filters

        # lookup filters
    def getUserCountryName(self, lookup): # Return country name after lookup
        return lookup['country_name']

    def isAccountBlocked(self, lookup): # Check if blocked (Bounced) after lookup
        return lookup['is_bounced']

    def isAccountSuspended(self, lookup): # Check if suspended status after lookup
        return lookup['is_suspended']
        # lookup filters

    # End Filters
# END

# Missing tweets in accounts
# Missing data in trinds
# Missing user search MAYBE LATER
# Missing tweets search
# Missing recieve dm
