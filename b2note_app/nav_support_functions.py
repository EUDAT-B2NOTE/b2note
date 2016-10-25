


def list_navbarlinks(request=None, links_out=[]):
    lnks = []
    if request and request.session.get('user')!=None:
        lnks = [
            {"url": "/accounts/profilepage", "title": "Account", "icon": "user"},
            {"url": "/search", "title": "Search", "icon": "search"},
            {"url": "/export", "title": "Download", "icon": "download-alt"},
            {"url": "/accounts/logout", "title": "Logout", "icon": "log-out"},
            {"url": "/help", "title": "Help page", "icon": "question-sign"},
        ]
    else:
        lnks = [
            {"url": "/accounts/login", "title": "Login", "icon": "user"},
            {"url": "/accounts/register", "title": "Registration", "icon": "record"},
            {"url": "/help", "title": "Help page", "icon": "question-sign"},
        ]
    lnks = [lnk for lnk in lnks if lnk["title"] not in links_out]
    return lnks


def list_shortcutlinks(request=None, links_out=[]):
    lnks = []
    lnks = [{"url": "", "title": "Previous page", "icon": "circle-arrow-left"}]
    if request and request.session.get('user')!=None:
        lnks.append({"url": "/interface_main", "title": "Main page", "icon": "home"})
    else:
        lnks.append({"url": "/accounts/login", "title": "Main page", "icon": "home"})
    lnks = [lnk for lnk in lnks if lnk["title"] not in links_out]
    return lnks