# req
Command line tool for making quick HTTP requests.
## Usage
### Routes
Routes loaded from `ROUTES_FILE`. The request's group, route name, HTTP verb, URL, header, and paramaters are represented.
```
beevrr|dash|GET|https://beevrr.herokuapp.com/mobile/dashboard|{'user-agent': 'agent'}|{}
beevrr|home|GET|https://beevrr.herokuapp.com/mobile/home/p/0/|{}|{'parm': 'val'}
beevrr|logout|POST|https://beevrr.herokuapp.com/mobile/logout|{}|{}
```
### Request
Display a list of routes and groups from `ROUTES_FILE`. The routes in group `beevrr` share the same cookies.
<pre>
--------------------------------------------------------------------------------
                                   <b>[req]</b>
--------------------------------------------------------------------------------
<b>[beevrr]</b> (2 cookies, 3 routes)
--------------------------------------------------------------------------------
<b>[dash]</b> | GET | https://beevrr.herokuapp.com/mobile/dashboard
header: {'user-agent': 'agent'}
params: {}

<b>[home]</b> | GET | https://beevrr.herokuapp.com/mobile/home/p/0/
header: {}
params: {'parm': 'val'}

<b>[logout]</b> | POST | https://beevrr.herokuapp.com/mobile/logout
header: {}
params: {}

--------------------------------------------------------------------------------
type 'cmds' for commands

</pre>
### Result
Response with body, stats, headers, and cookies. Cookies are saved to the group's `COOKIE_ROOT` folder and are passed to each subsequent request for any route in the group.
<pre>
home
Loading "home"...
--------------------------------------------------------------------------------
<b>[response]</b>
--------------------------------------------------------------------------------
{
    "disc_count": 2,
    "discussion_count": [
        {
            "count": 2
        }
    ],

    ...

    "user_count": [
        {
            "count": 2
        }
    ],
    "vote_count": [
        {
            "count": 1
        }
    ]
}
--------------------------------------------------------------------------------
<b>[stats]</b>
--------------------------------------------------------------------------------
status code: 200, time: 0.246745 seconds, size: 4.052734375 KB
--------------------------------------------------------------------------------
<b>[headers]</b>
--------------------------------------------------------------------------------
Connection: keep-alive
Date: Wed, 23 Jan 2019 11:09:00 GMT
Server: Apache
Cache-Control: no-cache, private
Set-Cookie: ...
Transfer-Encoding: chunked
Content-Type: application/json
Via: 1.1 vegur
--------------------------------------------------------------------------------
<b>[cookies]</b>
--------------------------------------------------------------------------------
"laravel_session" added to "beevrr"
"XSRF-TOKEN" added to "beevrr"
</pre>
### Test
Run test commands from `TEST_FILE`. Check to see if a route's result contains a particular JSON key, a sub string, or a certain status code. Use `cookies_clear` to remove a group's cookies.
```
home|200|has_str|Beevrr
login|200|has_json|{'status':'success'}
dash|200|has_json|{'status':'success'}
cookies_clear|beevrr
```
<pre>
test
--------------------------------------------------------------------------------
1: <b>[passed]</b> route "home" has status code "200"
1: <b>[passed]</b> route "home" contains "Beevrr"
2: <b>[passed]</b> route "login" has status code "200"
2: <b>[passed]</b> route "login" contains "{'status': 'success'}"
3: <b>[passed]</b> route "dash" has status code "200"
3: <b>[passed]</b> route "dash" contains "{'status': 'success'}"
4: <b>[cookie]</b> cookies cleared for "beevrr"
</pre>
### Commands
```
<route> | make http request

<route> url <url> | set route url
<route> name <name> | set route name
<route> type <type> | set route type
<route> type <group> | set route group
<route> header {...} | set route header, '{}' to clear
<route> params {...} | set route params, '{}' to clear

cookies show <group> | show cookies for group
cookies clear <group> | clear cookies for group

route add <group> <route> <type> <url> | add new route
route remove <route> | remove route

group name <group> <name> | set group name
group remove <group> | remove group and all associated routes
```
