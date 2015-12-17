from will.plugin import WillPlugin
from will.mixins.roster import RosterMixin
from will.mixins.hipchat import HipChatMixin
from will.decorators import respond_to, periodic, hear, \
    rendered_template, require_settings
from will import settings
import logging
from launchpadlib.launchpad import Launchpad
from jira import JIRA
import warnings
warnings.simplefilter("ignore")

MODULE_DESCRIPTION = "Help manage the relationship between Launchpad and Jira"


class LaunchpadPlugin(WillPlugin, RosterMixin, HipChatMixin):

    SEARCH_PATTERN = 'project = %s and ("OpenStack BugId URL"  = '\
        '"https://bugs.launchpad.net/designate/+bug/%s"  OR '\
        '"OpenStack BugId URL" = "https://bugs.launchpad.net/bugs/%s")'

    def render_jira(self, bug):
        return rendered_template(
            "jira_bug.html",
            {
                'key': bug.key,
                'title': bug.fields.summary,
                'link': bug.permalink(),
                'status': bug.fields.status.name
            }
        )

    def render_lp(self, bug):

        bug_info = {
            'link': bug.web_link,
            'title': bug.title,
            'milestones': []
        }

        for task in bug.bug_tasks:

            task_info = {
                'status': 'Unknown',
                'assignee': 'None',
                'title': 'None'
            }
            try:
                (task_info['status'], ) = task.status
            except Exception:
                pass
            try:
                task_info['assignee'] = task.assignee.name
            except Exception:
                pass
            try:
                task_info['title'] = task.target.name
            except Exception:
                pass
            bug_info['milestones'].append(task_info)

        return rendered_template("lp_bug.html", bug_info)

    def get_requester_email(self, message):
        msg_user = self.get_user_from_message(message)
        hc_user = self.get_hipchat_user(msg_user['hipchat_id'])
        email = hc_user['email']
        return email

    @hear("^(lp|launchpad|upstream)( bug)? (?P<bug>.*)")
    @hear("https://bugs.launchpad.net/.*/(?P<bug>\d*)")
    def inform_about_launchpad_bug(self, message, bug):
        launchpad = Launchpad.login_anonymously('just testing', 'production')

        self.say(
            self.render_lp(launchpad.bugs[bug]),
            html=True,
            message=message
        )

    @respond_to("^link lp (?P<bug>.*)")
    def link(self, message, bug):
        """link lp ____: Get Launchpad web link for bug ___"""
        launchpad = Launchpad.login_anonymously('just testing', 'production')
        try:
            launchpad.bugs[bug]
            self.reply(message, launchpad.bugs[bug].web_link)
        except KeyError:
            self.reply(message, "That issue does not exist in Launchpad")

    @respond_to("^show lp (?P<bug>.*)")
    def show(self, message, bug):
        """show lp ____: Show details of bug ___ on Launchpad"""
        launchpad = Launchpad.login_anonymously('just testing', 'production')

        self.say(
            self.render_lp(launchpad.bugs[bug]),
            message=message,
            html=True
        )

        jira = JIRA(
            basic_auth=(settings.JIRA_USER, settings.JIRA_PASS),
            server=settings.JIRA_HOST,
            validate=False,
            options={'verify': False}
        )

        issues = jira.search_issues(self.SEARCH_PATTERN % (
            settings.JIRA_PROJ, bug, bug))

        if len(issues) > 0:
            self.say("I also found a jira ticket for that", message=message)
            for issue in issues:
                self.say(
                    self.render_jira(issue),
                    message=message,
                    html=True
                )

    @require_settings(
        "JIRA_HOST",
        "JIRA_USER",
        "JIRA_PASS",
        "JIRA_PROJ"
    )
    @respond_to("^import lp (?P<bug>.*)")
    def import_issue(self, message, bug):
        """import lp ____: Creates a Jira ticket based on ___ bug"""
        jira = JIRA(
            basic_auth=(settings.JIRA_USER, settings.JIRA_PASS),
            server=settings.JIRA_HOST,
            validate=False,
            options={'verify': False}
        )

        issues = jira.search_issues(self.SEARCH_PATTERN % (
            settings.JIRA_PROJ, bug, bug))

        if len(issues) > 0:

            self.reply(
                message,
                self.render_jira(issues[0]),
                html=True
            )

        else:
            launchpad = Launchpad.login_anonymously(
                'will_jira_import',
                'production'
            )
            try:
                launchpad.bugs[bug]
            except KeyError:
                self.reply(message, "That issue does not exist in Launchpad")
                return

            issue_dict = {
                'project': {'key': settings.JIRA_PROJ},
                'summary': launchpad.bugs[bug].title,
                'description': launchpad.bugs[bug].description,
                'issuetype': {'name': 'Bug'},
                'customfield_10602': launchpad.bugs[bug].web_link,
                'components': [{'id': '18567'}],
                'reporter': {'name': self.get_requester_email(message)}
            }

            self.reply(message, "I need to create that")
            new_issue = jira.create_issue(fields=issue_dict)
            self.reply(message, self.render_jira(new_issue), html=True)
