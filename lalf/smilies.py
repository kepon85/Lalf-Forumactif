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
Module handling the exportation of the smilies
"""

import os
from io import BytesIO

from pyquery import PyQuery
from PIL import Image

from lalf.config import config
from lalf.node import Node
from lalf.util import pages
from lalf import session
from lalf import sql

DEFAULT_SMILIES = {
    ":D" : {
        "code" : ":D",
        "emotion" : "Very Happy",
        "smiley_url" : "icon_e_biggrin.gif"},
    ":-D" : {
        "code" : ":-D",
        "emotion" : "Very Happy",
        "smiley_url" : "icon_e_biggrin.gif"},
    ":grin:" : {
        "code" : ":grin:",
        "emotion" : "Very Happy",
        "smiley_url" : "icon_e_biggrin.gif"},
    ":)" : {
        "code" : ":)",
        "emotion" : "Smile",
        "smiley_url" : "icon_e_smile.gif"},
    ":-)" : {
        "code" : ":-)",
        "emotion" : "Smile",
        "smiley_url" : "icon_e_smile.gif"},
    ":smile:" : {
        "code" : ":smile:",
        "emotion" : "Smile",
        "smiley_url" : "icon_e_smile.gif"},
    ";)" : {
        "code" : ";)",
        "emotion" : "Wink",
        "smiley_url" : "icon_e_wink.gif"},
    ";-)" : {
        "code" : ";-)",
        "emotion" : "Wink",
        "smiley_url" : "icon_e_wink.gif"},
    ":wink:" : {
        "code" : ":wink:",
        "emotion" : "Wink",
        "smiley_url" : "icon_e_wink.gif"},
    ":(" : {
        "code" : ":(",
        "emotion" : "Sad",
        "smiley_url" : "icon_e_sad.gif"},
    ":-(" : {
        "code" : ":-(",
        "emotion" : "Sad",
        "smiley_url" : "icon_e_sad.gif"},
    ":sad:" : {
        "code" : ":sad:",
        "emotion" : "Sad",
        "smiley_url" : "icon_e_sad.gif"},
    ":o" : {
        "code" : ":o",
        "emotion" : "Surprised",
        "smiley_url" : "icon_e_surprised.gif"},
    ":-o" : {
        "code" : ":-o",
        "emotion" : "Surprised",
        "smiley_url" : "icon_e_surprised.gif"},
    ":eek:" : {
        "code" : ":eek:",
        "emotion" : "Surprised",
        "smiley_url" : "icon_e_surprised.gif"},
    ":shock:" : {
        "code" : ":shock:",
        "emotion" : "Shocked",
        "smiley_url" : "icon_eek.gif"},
    ":?" : {
        "code" : ":?",
        "emotion" : "Confused",
        "smiley_url" : "icon_e_confused.gif"},
    ":-?" : {
        "code" : ":-?",
        "emotion" : "Confused",
        "smiley_url" : "icon_e_confused.gif"},
    ":???:" : {
        "code" : ":???:",
        "emotion" : "Confused",
        "smiley_url" : "icon_e_confused.gif"},
    "8-)" : {
        "code" : "8-)",
        "emotion" : "Cool",
        "smiley_url" : "icon_cool.gif"},
    ":cool:" : {
        "code" : ":cool:",
        "emotion" : "Cool",
        "smiley_url" : "icon_cool.gif"},
    ":lol:" : {
        "code" : ":lol:",
        "emotion" : "Laughing",
        "smiley_url" : "icon_lol.gif"},
    ":x" : {
        "code" : ":x",
        "emotion" : "Mad",
        "smiley_url" : "icon_mad.gif"},
    ":-x" : {
        "code" : ":-x",
        "emotion" : "Mad",
        "smiley_url" : "icon_mad.gif"},
    ":mad:" : {
        "code" : ":mad:",
        "emotion" : "Mad",
        "smiley_url" : "icon_mad.gif"},
    ":P" : {
        "code" : ":P",
        "emotion" : "Razz",
        "smiley_url" : "icon_razz.gif"},
    ":-P" : {
        "code" : ":-P",
        "emotion" : "Razz",
        "smiley_url" : "icon_razz.gif"},
    ":razz:" : {
        "code" : ":razz:",
        "emotion" : "Razz",
        "smiley_url" : "icon_razz.gif"},
    ":oops:" : {
        "code" : ":oops:",
        "emotion" : "Embarrassed",
        "smiley_url" : "icon_redface.gif"},
    ":cry:" : {
        "code" : ":cry:",
        "emotion" : "Crying or Very Sad",
        "smiley_url" : "icon_cry.gif"},
    ":evil:" : {
        "code" : ":evil:",
        "emotion" : "Evil or Very Mad",
        "smiley_url" : "icon_evil.gif"},
    ":twisted:" : {
        "code" : ":twisted:",
        "emotion" : "Twisted Evil",
        "smiley_url" : "icon_twisted.gif"},
    ":roll:" : {
        "code" : ":roll:",
        "emotion" : "Rolling Eyes",
        "smiley_url" : "icon_rolleyes.gif"},
    ":!:" : {
        "code" : ":!:",
        "emotion" : "Exclamation",
        "smiley_url" : "icon_exclaim.gif"},
    ":?:" : {
        "code" : ":?:",
        "emotion" : "Question",
        "smiley_url" : "icon_question.gif"},
    ":idea:" : {
        "code" : ":idea:",
        "emotion" : "Idea",
        "smiley_url" : "icon_idea.gif"},
    ":arrow:" : {
        "code" : ":arrow:",
        "emotion" : "Arrow",
        "smiley_url" : "icon_arrow.gif"},
    ":|" : {
        "code" : ":|",
        "emotion" : "Neutral",
        "smiley_url" : "icon_neutral.gif"},
    ":-|" : {
        "code" : ":-|",
        "emotion" : "Neutral",
        "smiley_url" : "icon_neutral.gif"},
    ":mrgreen:" : {
        "code" : ":mrgreen:",
        "emotion" : "Mr. Green",
        "smiley_url" : "icon_mrgreen.gif"},
    ":geek:" : {
        "code" : ":geek:",
        "emotion" : "Geek",
        "smiley_url" : "icon_e_geek.gif"},
    ":ugeek:" : {
        "code" : ":ugeek:",
        "emotion" : "Uber Geek",
        "smiley_url" : "icon_e_ugeek.gif"},

    "8)" : {
        "code" : "8)",
        "emotion" : "Cool",
        "smiley_url" : "icon_cool.gif",
        "smiley_width" : "15",
        "smiley_height" : "17",
        "smiley_order" : "43",
        "display_on_posting" : "0"}
}

class Smiley(Node):
    """
    Node representing a smiley

    Attrs:
        smiley_id (int): The index of the smiley in the original forum (used
                         to convert html to bbcode)
        code (str): The bbcode of the smiley
        url (str): The url of the image of the smiley
        emotion (str): An expression describing the smiley

        smiley_url (str): The filename of the smiley in the new forum
        width (int): The width of the image
        height (int): The height of the image
        order (int): The position of the smiley in the interface
    """

    # Attributes to save
    STATE_KEEP = ["id", "code", "url", "emotion", "smiley_url", "width", "height", "order"]

    def __init__(self, parent, smiley_id, code, url, emotion):
        Node.__init__(self, parent)

        self.smiley_id = smiley_id
        self.code = code
        self.url = url
        self.emotion = emotion

        self.smiley_url = None
        self.width = None
        self.height = None
        self.order = None

    def _export_(self):
        if config["export_smilies"]:
            self.logger.debug("Téléchargement de l'émoticone \"%s\"", self.code)

            # Create the smilies directory if necessary
            dirname = os.path.join("images", "smilies")
            if not os.path.isdir(dirname):
                os.makedirs(dirname)

            # Download the image and get its dimensions and format
            response = session.get_image(self.url)
            with Image.open(BytesIO(response.content)) as image:
                self.smiley_url = "icon_exported_{}.{}".format(self.smiley_id, image.format.lower())
                self.width = image.width
                self.height = image.height

            # Save the image
            with open(os.path.join(dirname, self.smiley_url), "wb") as fileobj:
                fileobj.write(response.content)

            self.parent.parent.count += 1
            self.order = self.parent.parent.count

        # Add the smiley to the smilies dictionnary
        self.parent.parent.smilies[self.smiley_id] = {
            "code" : self.code,
            "emotion" : self.emotion,
            "smiley_url" : self.smiley_url}

    def _dump_(self, file):
        sql.insert(file, "smilies", {
            "code" : self.code,
            "emotion" : self.emotion,
            "smiley_url" : self.smiley_url,
            "smiley_width" : self.width,
            "smiley_height" : self.height,
            "smiley_order" : self.order,
            "display_on_posting" : "0"
        })

class SmiliesPage(Node):
    """
    Node representing a page of the list of smilies

    Attrs:
        page (int): The index of the first smiley on the page
    """

    # Attributes to save
    STATE_KEEP = ["page"]

    def __init__(self, parent, page):
        Node.__init__(self, parent)
        self.page = page

    def _export_(self):
        self.logger.info('Récupération des émoticones (page %d)', self.page)

        # Get the page
        params = {
            "part" : "themes",
            "sub" : "avatars",
            "mode" : "smilies",
            "start" : self.page
        }
        response = session.get_admin("/admin/index.forum", params=params)
        document = PyQuery(response.text)

        for element in document('table tr'):
            e = PyQuery(element)
            if e("td").eq(0).text() and e("td").eq(0).attr("colspan") is None:
                smiley_id = e("td").eq(0).text()
                code = e("td").eq(1).text()
                url = e("td").eq(2).find("img").eq(0).attr("src")
                emotion = e("td").eq(3).text()

                if code in DEFAULT_SMILIES:
                    self.logger.debug("L'émoticone \"%s\" existe déjà dans phpbb.", code)
                    self.parent.smilies[smiley_id] = DEFAULT_SMILIES[code]
                else:
                    child = Smiley(self, smiley_id, code, url, emotion)
                    self.children.append(child)

class Smilies(Node):
    """
    Node used to export the smilies

    Attrs:
        smilies (dict): Dictionnary associating each smiley to its code, url and emotion.
        count (int): The number of smilies
    """

    # Attributes to save
    STATE_KEEP = ["smilies", "order"]

    def __init__(self, parent):
        Node.__init__(self, parent)
        self.smilies = {}
        self.count = len(DEFAULT_SMILIES)

    def _export_(self):
        self.logger.info('Récupération des émoticones')

        params = {
            "part" : "themes",
            "sub" : "avatars",
            "mode" : "smilies"
        }
        response = session.get_admin("/admin/index.forum", params=params)
        for page in pages(response.text):
            self.children.append(SmiliesPage(self, page))
