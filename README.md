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
```
--------------------------------------------------------------------------------
                                   [req]
--------------------------------------------------------------------------------
[beevrr] (2 cookies, 4 routes)
--------------------------------------------------------------------------------
[dash] | GET | https://beevrr.herokuapp.com/mobile/dashboard
header: {'user-agent': 'agent'}
params: {}

[home] | GET | https://beevrr.herokuapp.com/mobile/home/p/0/
header: {}
params: {'parm': 'val'}

[logout] | POST | https://beevrr.herokuapp.com/mobile/logout
header: {}
params: {}

--------------------------------------------------------------------------------
type 'cmds' for commands

```
### Result
Response with body, stats, headers, and cookies. Cookies are saved to the group's `COOKIE_ROOT` folder and are passed to each subsequent request for any route in the group.
```
home
Loading "home"...
--------------------------------------------------------------------------------
[response]
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
[stats]
--------------------------------------------------------------------------------
status code: 200, time: 0.246745 seconds, size: 4.052734375 KB
--------------------------------------------------------------------------------
[headers]
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
[cookies]
--------------------------------------------------------------------------------
"laravel_session" added to "beevrr"
"XSRF-TOKEN" added to "beevrr"
```
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
