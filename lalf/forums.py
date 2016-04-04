# -*- coding: utf-8 -*-
#
# This file is part of Lalf.
#
# Lalf is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lalf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lalf.  If not, see <http://www.gnu.org/licenses/>.

"""
Module handling the exportation of the forums
"""

import re

from pyquery import PyQuery

from lalf.node import Node
from lalf.topics import ForumPage
from lalf.posts import NoPost
from lalf.util import pages, Counter
from lalf import htmltobbcode

def default_forum_acl(forumid):
    for gid, perm in ((1, 17), # guests: readonly
                      (2, 21), # registered: standard w/ polls
                      (3, 21), # registered+COPPA: standard w/ polls
                      (4, 14), # global mods: full access
                      (4, 11), # global mods: standard moderation
                      (5, 14), # admins: full access
                      (5, 10), # admins: full moderation
                      (6, 19), # bots: bot access
                     ):
        yield {
            "group_id" : gid,
            "forum_id" : forumid,
            "auth_option_id" : 0,
            "auth_role_id" : perm,
            "auth_setting" : 0
        }

@Node.expose(self="forum")
class Forum(Node):
    """
    Node representing a forum

    Attrs:
        id (str): The id in the old forum
        newid (int): The id in the new forum
        left_id (int): Left id of the forum in the nested set model (see
                       https://en.wikipedia.org/wiki/Nested_set_model)
        right_id (int): Right id of the forum in the nested set model
        parent (Forum): The parent forum (or None)
        title (str): The title of the forum

        description (str): The description of the forum
        icon (str): The url of the forum icon
    """
    # Attributes to save
    STATE_KEEP = ["newid", "parent", "title", "description", "icon", "left_id",
                  "right_id", "status", "num_topics", "num_posts", "forum_type"]

    def __init__(self, forum_id, parent, title, num_topics, num_posts):
        Node.__init__(self, forum_id)
        self.parent = parent
        self.title = title.replace('"', '&quot;')

        if self.id[0] == "f":
            self.forum_type = 1
        else:
            self.forum_type = 0

        self.num_topics = num_topics
        self.num_posts = num_posts

        self.newid = None
        self.left_id = None
        self.right_id = None
        self.description = ""
        self.icon = ""
        self.status = 0

    def get_topics(self):
        """
        Returns the topics of this forum
        """
        for page in self.get_children():
            for topic in page.get_children():
                yield topic

    def get_posts(self):
        """
        Returns the posts of this forum
        """
        for topic in self.get_topics():
            for post in topic.get_posts():
                yield post

    def _export_(self):
        self.logger.info('Récupération du forum %s', self.id)

        self.forums.count += 1
        self.newid = self.forums.count.value

        response = self.session.get("/{}-a".format(self.id))

        # Get subforums descriptions, number of topics, ...
        self.forums.get_subforums_infos(response.text)

        for page in pages(response.text):
            self.add_child(ForumPage(page))

    def _dump_(self, sqlfile):
        # Get forum_parents field
        entry = "i:{};a:2:{{i:0;s:{}:\"{}\";i:1;i:{};}}"
        entries = []
        parent = self.parent
        while parent.newid > 0:
            title = parent.title
            entries.append(entry.format(
                parent.newid, len(parent.title), title, parent.forum_type))
            parent = parent.parent

        parents = "a:{}:{{{}}}".format(len(entries), "".join(reversed(entries)))

        parser = htmltobbcode.Parser(self.root)
        parser.feed(self.description)
        description = parser.get_post()

        num_posts = sum(1 for post in self.get_posts())
        num_topics = sum(1 for post in self.get_topics())

        if num_posts == 0:
            last_post = NoPost()
        else:
            last_post = max(self.get_posts(), key=lambda post: post.time)

        sqlfile.insert("forums", {
            "forum_id" : self.newid,
            "parent_id" : self.parent.newid,
            "left_id" : self.left_id,
            "right_id" : self.right_id,
            "forum_parents" : parents,
            "forum_name" : self.title,
            "forum_desc" : description.text,
            "forum_desc_bitfield" : description.bitfield,
            "forum_desc_uid" : description.uid,
            "forum_type" : self.forum_type,
            "forum_image" : self.icon,
            "forum_status" : self.status,
            "forum_posts" : num_posts,
            "forum_topics" : num_topics,
            "forum_topics_real" : num_topics,
            "forum_last_post_id" : last_post.id,
            "forum_last_poster_id" : last_post.poster.newid,
            "forum_last_post_subject" : last_post.title,
            "forum_last_post_time" : last_post.time,
            "forum_last_poster_name" : last_post.poster.name,
            "forum_last_poster_colour" : last_post.poster.colour
        })

        for acl in default_forum_acl(self.newid):
            sqlfile.insert("acl_groups", acl)

class ForumRoot(Node):
    STATE_KEEP = ["id", "newid", "left_id", "right_id"]
    def __init__(self):
        Node.__init__(self, 0)
        self.newid = 0
        self.left_id = 0
        self.right_id = 1

class Forums(Node):
    """
    Node used to export the forums
    """

    STATE_KEEP = ["count"]

    def __init__(self):
        Node.__init__(self, "forums")
        self.count = Counter(0)

    def _export_children(self, element, parent=None):
        """
        Export the forums shown in an html element
        """
        idpattern = re.compile("([cf]\d+)_open")

        for e in element.children("div"):
            match = idpattern.fullmatch(e.get("id"))
            if match:
                forum_id = match.group(1)

                child_element = PyQuery(e)
                row = child_element.children("table").eq(0).find("tr").eq(0)

                # Get title, number of topics and number of posts
                title = row.children("td").eq(1).text().strip()

                num_topics = int(row.children("td").eq(2).text())
                num_posts = int(row.children("td").eq(3).text())

                # Add forum to children
                forum = Forum(forum_id, parent, title, num_topics, num_posts)
                self.add_child(forum)

                # Export children and set left and right ids
                forum.left_id = parent.right_id
                forum.right_id = forum.left_id + 1
                self._export_children(child_element, forum)
                parent.right_id = forum.right_id + 1

    def _export_(self):
        self.logger.info('Récupération des forums')

        # Get the page of the administration panel listing the forums
        params = {
            "part" : "general",
            "sub" : "general",
            "mode" : "forum"
        }
        response = self.session.get_admin("/admin/index.forum", params=params)
        document = PyQuery(response.text)

        current_element = document("#root_open").eq(0)
        self._export_children(current_element, ForumRoot())

        # Get subforums descriptions
        response = self.session.get("/forum")
        self.get_subforums_infos(response.text)

    def get_subforums_infos(self, html):
        """
        Get informations (description, number of topics and posts, ...) about
        the forums listed on a page
        """
        document = PyQuery(html)

        idpattern = re.compile(r"/([fc]\d+)-.*")

        for element in document("a.forumlink"):
            e = PyQuery(element)

            match = idpattern.fullmatch(e.attr("href"))
            if not match:
                continue

            forum_id = match.group(1)
            forum = self.get(forum_id)

            row = e.closest("tr")

            # Get forum status
            alt = row("td:nth-of-type(1) img").eq(0).attr("alt")
            forum.status = 1 if "verrouillé" in alt else 0

            # Get subforum description
            forum.description = row("td:nth-of-type(2) span").eq(1).html() or ""
