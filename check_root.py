import urllib.request
content = urllib.request.urlopen('http://[::1]:5173').read().decode()
if '<div id="root"></div>' in content:
    print('ROOT DIV IS EMPTY - React not mounted')
else:
    print('ROOT DIV HAS CONTENT - React mounted')