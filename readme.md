## Python interface for IG.com's REST API

Works with the REST interface from [IG.com](http://www.ig.com).
Currently it sets up a client object and then GET's the "popular
markets" which is includes the markets currently being traded on
the most.

### Install

Just close the project:

git clone github.com:veioenza/ig_markets.git

Login details need to be added to a file called "credentials.py"

### To use
The interface is currently set to use a demo account but this
is simple to change. Set base_url = "https://api.ig.com/"
