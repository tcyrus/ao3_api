# Usage

This package is divided in 8 core modules: works, users, series, search, session, comments, extra, and utils.

## Works

One of the most basic things you might want to do with this package is loading a work and checking its statistics and informations. To do that, you'll need the `AO3.Work` class.

We start by finding the _workid_ of the work we want to load. We do that either by using `AO3.utils.workid_from_url(url)` or by just looking at the url ourselves. Let's take a look:

```py3
import AO3

url = "https://archiveofourown.org/works/14392692/chapters/33236241"
workid = AO3.utils.workid_from_url(url)
print(f"Work ID: {workid}")
work = AO3.Work(workid)
print(f"Chapters: {work.chapters}")
```

After running this snippet, we get the output:

```
Work ID: 14392692
Chapters: 46
```

It's important to note that some works may not be accessible to guest users, and in this case you will get 0 chapters as an output, and the error `AO3.utils.AuthError: This work is only available to registered users of the Archive` if you try to load it. Nontheless, we can still do a lot more with this Work object: Lets try to get the first 20 words of the second chapter.

```py3
import AO3

work = AO3.Work(14392692)

print(work.chapter_names[1])  # Second chapter name
text = work.get_chapter_text(2)  # Second chapter text
print(' '.join(text.split(" ")[:20]))
```

```
2. What Branches Grow Meaning

Chapter Text

December 27, 2018
 Christmas sucked this year, and Shouto’s got the black eye to prove it.Things had started out well
```

Another thing you can do with the work object is download the entire work as a pdf or e-book.

```py3
import AO3

work = AO3.Work(14392692)
work.load_chapters()

with open(f"{work.title}.pdf", "wb") as file:
    file.write(work.download("PDF"))
```


__Advanced functionality__

Usually, when you call the constructor for the `Work` class, all info about it is loaded in the `__init__()` function. However, this process takes quite some time (~1-1.5 seconds) and if you want to load a list of works from a series, for example, you might be waiting for upwards of 30 seconds. To avoid this problem, the `Work.reload()` function, called on initialization, is a "threadable" function, which means that if you call it with the argument `threaded=True`, it will return a `Thread` object and work in parallel, meaning you can load multiple works at the same time. Let's take a look at an implementation:

```py3
import AO3
import time

series = AO3.Series(1295090)

works = []
threads = []
start = time.time()
for workid, _, _ in series.work_list:
    work = AO3.Work(workid, load=False)
    works.append(work)
    threads.append(work.reload(threaded=True))
for thread in threads:
    thread.join()
print(f"Loaded {len(works)} works in {round(time.time()-start, 1)} seconds.")
```

`Loaded 29 works in 2.2 seconds.`

The `load=False` inside the `Work` constructor makes sure we don't load the work as soon as we create an instance of the class. In the end, we iterate over every thread and wait for the last one to finish using `.join()`. Let's compare this method with the standard way of loading AO3 works:

```py3
import AO3
import time

series = AO3.Series(1295090)

works = []
start = time.time()
for workid, _, _ in series.work_list:
    work = AO3.Work(workid)
    works.append(work)

print(f"Loaded {len(works)} works in {round(time.time()-start, 1)} seconds.")
```

`Loaded 29 works in 18.6 seconds.`

As we can see, there is a significant performance increase. There are other functions in this package which have this functionality. To see if a function is "threadable", either use `hasattr(function, "_threadable")` or check its `__doc__` string.



## Users

Another useful thing you might want to do is get information on who wrote which works / comments. For that, we use the `AO3.User` class.

```py3
import AO3

user = AO3.User("bothersomepotato")
print(user.url)
print(user.bio)
print(user.works)  # Number of works published
```

```
https://archiveofourown.org/users/bothersomepotato
University student, opening documents to write essays but writing this stuff instead. No regrets though. My Tumblr, come chat with -or yell at- me if you feel like it! :)
2
```


## Search

To search for works, you can either use the `AO3.search()` function and parse the BeautifulSoup object returned yourself, or use the `AO3.Search``` class to automatically do that for you

```py3
import AO3
search = AO3.Search(any_field="Clarke Lexa", word_count=AO3.utils.Constraint(5000, 15000))
search.update()
print(search.total_results)
for result in search.results:
  print(result)
```

```py3
3070
(5889004, 'five times lexa falls for clarke', ['nutmeg101'])
(10988430, 'an incomplete list of reasons (why Clarke loves Lexa)', ['RaeDMagdon'])
(6216283, "five times clarke and lexa aren’t sure if they're a couple or not", ['nutmeg101'])
(6422242, 'Chemistry', ['CaffeineDream'])
(3516830, 'The New Commander (Lexa Joining Camp Jaha)', ['Vision'])
(23012080, "it's always been (right in front of me)", ['kursty'])
(8915020, 'Ode to Clarke', ['Combatboots'])
(7383091, 'The Girlfriend Tag', ['hush_mya'])
(11100006, 'The After-Heda Chronicles', ['hedasgirl'])
(6748720, 'The Counter', ['FompFloat'])
(3504113, 'The Games We Play', ['MsRay3'])
(13550457, 'Self Control', ['Drummer_Girl'])
(9647864, 'May We Meet Again', ['HJ1'])
(5196890, "A l'épreuve des balles", ['Kardhane (ThroughMyMind)'])
(13438785, 'Celebration', ['Na_Na_Nessa'])
(10139129, 'No Filter', ['Bal3xicon'])
(None, 'My osom girlfriend', ['Tabitha Craft (Tabithacraft)'])
(9927671, 'Another level of fucked up', ['I_am_clexa'])
(4687346, "He's Jealous", ['WhoKilledBambi'])
(3847735, "(Don't Ever Want to Tame) This Wild Heart", ['acaelousqueadcentrum'])
```

You can then use the workid to load one of the works you searched for. To get more then the first 20 works, change the page number using 
```py3
search.page = 2
```

## Session

A lot of actions you might want to take might require an AO3 account, and if you have one, you can get access to those actions using an AO3.Session object. You start by logging in using your username and password, and then you can use that object to access restricted content.

```py3
import AO3

session = AO3.Session("username", "password")
print(f"Bookmarks: {session.get_n_bookmarks()}")
session.refresh_auth_token()
print(session.kudos(14392692))
```

```
Bookmarks: 67
True
```

We successfully left kudos in a work and checked our bookmarks. The `session.refresh_auth_token()` is needed for some activities such as leaving kudos and comments. If it is expired or you forget to call this function, the error `AO3.utils.AuthError: Invalid authentication token. Try calling session.refresh_auth_token()` will be raised.

You can also comment / leave kudos in a work by calling `Work.leave_kudos()`/`Work.comment()` and passing the session as an argument.

If you would prefer to leave a comment or kudos anonimously, you can use an `AO3.GuestSession` in the same way you'd use a normal session, except you won't be able to check your bookmarks, subscriptions, etc... because you're not actually logged in.


## Comments

To retrieve and process comment threads, you might want to look at the `Work.get_comments()` method. It returns all the comments in a specific chapter and their respective threads. You can then process them however you want. Let's take a look:

```py3
from time import time

import AO3


work = AO3.Work(24560008)
work.load_chapters()
start = time()
comments = work.get_comments(1, 5)
print(f"Loaded {len(comments)} comment threads in {round(time()-start, 1)} seconds\n")
for comment in comments:
    print(f"Comment ID: {comment.comment_id}\nReplies: {len(comment.get_thread())}")
```

```
Loaded 5 comment threads in 1.8 seconds

Comment ID: 312237184
Replies: 1
Comment ID: 312245032
Replies: 1
Comment ID: 312257098
Replies: 1
Comment ID: 312257860
Replies: 1
Comment ID: 312285673
Replies: 2
```

Loading comments takes a very long time so you should try and use it as little as possible. It also causes lots of requests to be sent to the AO3 servers, which might result in getting the error `utils.HTTPError: We are being rate-limited. Try again in a while or reduce the number of requests`. If it happens, you should try to space out your requests or reduce their number.


## Extra

AO3.extra contains the the code to download some extra resources that are not core to the functionality of this package and don't change very often. One example would be the list of fandoms recognized by AO3.
To download a resource, simply use `AO3.extra.download(resource_name)`. To download every resource, you can use `AO3.extra.download_all()`. To see the list of available resources, `AO3.extra.get_resources()` will help you.