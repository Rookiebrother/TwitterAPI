# TwitterAPI

Python Simple Twitter api using username And password


## Installation

Installing requirements

```
pip install -r requirements.txt
```

## Running the tests

### Example

login and tweet and follow

```
twitter = Twitter()
twitter.login('username', 'password')
twitter.tweet('TwitterAPI')
user = twitter.getUserInfoByName('diefunction')
twitter.follow(twitter.getID(user))
```
## About the code
there's a comments in the code that explaining what the functions do.

## Authors

* **Diefunction - Rayan Althobaiti** - https://twitter.com/Diefunction

