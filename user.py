import logging
logger = logging.getLogger("lalf")

import re
from pyquery import PyQuery
import hashlib
import random
import string
import time

import session
from node import Node
import ui
import sql
import phpbb
from config import config
import about

number = 0

def random_password(length=8):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(8)])

def md5(str):
    return hashlib.md5(str.encode("utf8")).hexdigest()

class User(Node):
    STATE_KEEP = ["id", "newid", "name", "mail", "posts", "date", "lastvisit"]

    def __init__(self, parent, id, newid, name, mail, posts, date, lastvisit, incuser=True):
        Node.__init__(self, parent)
        self.id = id
        self.newid = newid
        self.name = name
        self.mail = mail
        self.posts = posts
        self.date = date
        self.lastvisit = lastvisit
        self.exported = True
        self.children_exported = True

        if incuser:
            self.inc()

    def inc(self):
        global number
        number += 1
        ui.update()
            
    def __setstate__(self, dict):
        global number
        Node.__setstate__(self, dict)
        number += 1
        
    def _export_(self):
        return

    def confirm_email(self, r):
        return

    def _dump_(self, file):
        user = {}
        user["user_id"] = self.newid
        user["user_type"] = "0"
        user["group_id"] = "2"
        user["username"] = self.name
        user["username_clean"] = self.name.lower()
        user["user_regdate"] = self.date
        user["user_password"] =  md5(random_password())
        user["user_email"] = self.mail
        user["user_email_hash"] = sql.email_hash(self.mail)
        user["user_lang"] = "fr"
        user["user_style"] = "1"
        user["user_rank"] = "0"
        user["user_colour"] = ""
        user["user_posts"] = self.posts
        user["user_permissions"] = ""
        user["user_ip"] = ""
        user["user_birthday"] = " 0- 0- 0"
        user["user_lastpage"] = ""
        user["user_last_confirm_key"] = ""
        user["user_post_sortby_type"] = "t"
        user["user_post_sortby_dir"] = "a"
        user["user_topic_sortby_type"] = "t"
        user["user_topic_sortby_dir"] = "d"
        user["user_avatar"] = ""
        user["user_sig"] = ""
        user["user_sig_bbcode_uid"] = ""
        user["user_from"] = ""
        user["user_icq"] = ""
        user["user_aim"] = ""
        user["user_yim"] = ""
        user["user_msnm"] = ""
        user["user_jabber"] = ""
        user["user_lastvisit"] = self.lastvisit
        user["user_website"] = ""
        user["user_occ"] = ""
        user["user_interests"] = ""
        user["user_actkey"] = ""
        user["user_newpasswd"] = ""
        user["user_pass_convert"] = "1"
        user["user_avatar_type"] = "2"

        # Administrator
        if self.name == config["admin_name"]:
            user["user_type"] = 3
            user["group_id"] = 5
            user["user_password"] = md5(config["admin_password"])
            user["user_rank"] = 1
            user["user_colour"] = "AA0000"
            user["user_new_privmsg"] = 1
            user["user_unread_privmsg"] = 1
            user["user_last_privmsg"] = time.time()

        sql.insert(file, "users", user)

        sql.insert(file, "user_group", {
            "group_id" : 2,
            "user_id" : self.newid,
            "user_pending" : 0
            })

        # Administrator
        if self.name == config["admin_name"]:
            sql.insert(file, "user_group", {
                "group_id" : 4,
                "user_id" : self.newid,
                "user_pending" : 0,
                "group_leader" : 0
                })
            sql.insert(file, "user_group", {
                "group_id" : 5,
                "user_id" : self.newid,
                "user_pending" : 0,
                "group_leader" : 1
                })

            # Send a pm to give instructions/ask donation
            post, uid, bitfield, checksum = phpbb.format_post(about.admin_pm_post)
                
            sql.insert(file, "privmsgs", {
            "msg_id"             : 1,
            'root_level'         : 0,
            'author_id'          : self.newid,
            'icon_id'            : 0,
            'author_ip'          : "127.0.0.1",
            'message_time'       : int(time.time()),
            'enable_bbcode'      : 1,
            'enable_smilies'     : 1,
            'enable_magic_url'   : 1,
            'enable_sig'         : 1,
            'message_subject'    : about.admin_pm_subject,
            'message_text'       : post,
            'message_attachment' : 0,
            'bbcode_bitfield'    : bitfield,
            'bbcode_uid'         : uid,
            'to_address'         : "u_{}".format(self.newid),
            'bcc_address'        : "",
            'message_reported'   : 0})

            # Inbox
            sql.insert(file, "privmsgs_to", {
                'msg_id'	   : 1,
                'user_id'	   : self.newid,
                'author_id'	   : self.newid,
                'folder_id'	   : -1,
                'pm_new'	   : 1,
                'pm_unread'	   : 1,
                'pm_forwarded' : 0})
            # Outbox
            sql.insert(file, "privmsgs_to", {
                'msg_id'	   : 1,
                'user_id'	   : self.newid,
                'author_id'	   : self.newid,
                'folder_id'	   : 0,
                'pm_new'	   : 1,
                'pm_unread'	   : 1,
                'pm_forwarded' : 0})
