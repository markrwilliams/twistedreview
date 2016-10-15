from txghbot import IWebhook
from twisted.plugin import IPlugin

from zope.interface import implementer
from txgithub.api import GithubApi

import pprint


@implementer(IWebhook, IPlugin)
class ReopenPullRequest(object):
    MAGIC = u"!please-review"

    def __init__(self, token):
        self.api = GithubApi(token)

    def match(self, eventName, eventData):
        pprint.pprint(eventName)
        pprint.pprint(eventData)
        return (eventName == u'issue_comment'
                and u'pull_request' in eventData[u'issue']
                and eventData[u'action'] in (u'created',
                                             u'edited')
                and eventData[u'comment'][u'body'].strip() == self.MAGIC)

    def run(self, eventName, eventData, requestID):
        user = eventData[u'repository'][u'owner'][u'login'].encode('ascii')
        repo = eventData[u'repository'][u'name'].encode('ascii')
        pullNumber = str(eventData[u'issue'][u'number'])

        reopen = self.api.pulls.edit(user, repo, pullNumber, state="open")

        def makeComment(ignored):
            return self.api.comments.create(user, repo, pullNumber,
                                            "Reopened, just for you!")

        reopen.addCallback(makeComment)
        return reopen

with open(".dev/oauth") as f:
    reopener = ReopenPullRequest(f.read().strip())
