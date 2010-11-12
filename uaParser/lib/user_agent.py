# Copyright 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the 'License')
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""User Agent model."""

import re

import user_agent_parser

# Mainly used for SeedDatastore.
# You may want models.result_stats.py
TOP_USER_AGENT_STRINGS = (
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) '
     'AppleWebKit/530.1 (KHTML, like Gecko) '
     'Chrome/2.0.169 Safari/530.1'),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) '
     'AppleWebKit/530.1 (KHTML, like Gecko) '
     'Chrome/3.0.169.1 Safari/530.1'),
    ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) '
     'AppleWebKit/530.1 (KHTML, like Gecko) '
     'Chrome/4.0.169.1 Safari/530.1'),
    ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.6) '
     'Gecko/2009011912 Firefox/3.0.3'),
    ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.6) '
     'Gecko/2009011912 Firefox/3.5.3'),
    ('Mozilla/4.0 '
     '(compatible; MSIE 6.0; Windows NT 5.1; Trident/4.0; '
     '.NET CLR 2.0.50727; .NET CLR 1.1.4322; '
     '.NET CLR 3.0.04506.648; .NET CLR 3.5.21022)'),
    ('Mozilla/4.0 '
     '(compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; '
     '.NET CLR 2.0.50727; .NET CLR 1.1.4322; '
     '.NET CLR 3.0.04506.648; .NET CLR 3.5.21022)'),
    ('Mozilla/4.0 '
     '(compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; '
     '.NET CLR 2.0.50727; .NET CLR 1.1.4322; '
     '.NET CLR 3.0.04506.648; .NET CLR 3.5.21022)'),
    'Opera/9.64 (Windows NT 5.1; U; en) Presto/2.1.1',
    'Opera/10.00 (Windows NT 5.1; U; en) Presto/2.2.0',
    ('Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_4_11; en) '
     'AppleWebKit/525.27.1 (KHTML, like Gecko) Version/3.2.1 Safari/525.27.1'),
    ('Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_4_11; en) '
     'AppleWebKit/525.27.1 (KHTML, like Gecko) Version/4.0.1 Safari/525.27.1'),
)


class UserAgent():
    """User Agent Model."""
    string = ""
    family = ""
    major_version = ""
    minor_version = ""
    beta_version = ""
    confirmed = ""
    created = ""

    def __init__(self, string, family, major_version, minor_version, beta_version):
        self.string = string
        self.family = family
        self.major_version = major_version
        self.minor_version = minor_version
        self.beta_version = beta_version

    def pretty(self):
        """Invokes pretty print."""
        return self.pretty_print(self.family, self.major_version, self.minor_version, self.beta_version)

    def get_string_list(self):
        """Returns a list of a strings suitable a StringListProperty."""
        return self.parts_to_string_list(self.family, self.major_version, self.minor_version, self.beta_version)

    @classmethod
    def factory(cls, string, **kwds):
        """Factory function.

        Args:
            string: the http user agent string.
        Returns:
            a UserAgent instance
        """
        normal_string = string.replace(',gzip(gfe)', '')

        family, major_version, minor_version, beta_version = user_agent_parser.Parse(string)
        user_agent = cls(string=string, family=family, major_version=major_version, minor_version=minor_version, beta_version=beta_version)

        return user_agent

    @staticmethod
    def parse_pretty(pretty_string):
        """Parse a user agent pretty (e.g. 'Chrome 4.0.203') to parts.

        Args:
            pretty_string: a user agent pretty string (e.g. 'Chrome 4.0.203')
        Returns:
            [family, major_version, minor_version, beta_version]
            e.g. ['Chrome', '4', '0', '203']
        """
        major_version, minor_version, beta_version = None, None, None
        family, sep, version_str = pretty_string.rpartition(' ')
        if not family:
            family = version_str
        else:
            version_bits = version_str.split('.')
            major_version = version_bits.pop(0)
            if not major_version.isdigit():
                family = pretty_string
                major_version = None
            elif version_bits:
                minor_version = version_bits.pop(0)
                if version_bits:
                    beta_version = version_bits.pop(0)
        return family, major_version, minor_version, beta_version


    @staticmethod
    def MatchSpans(user_agent_string):
        """Parses the user-agent string and returns the bits.

        Used by the "Confirm User Agents" admin page to highlight matches.

        Args:
            user_agent_string: The full user-agent string.
        """
        for parser in USER_AGENT_PARSERS:
            match_spans = parser.MatchSpans(user_agent_string)
            if match_spans:
                return match_spans
        return []

    @staticmethod
    def pretty_print(family, major_version=None, minor_version=None, beta_version=None):
        """Pretty browser string."""
        if beta_version:
            if beta_version[0].isdigit():
                return '%s %s.%s.%s' % (family, major_version, minor_version, beta_version)
            else:
                return '%s %s.%s%s' % (family, major_version, minor_version, beta_version)
        elif minor_version:
            return '%s %s.%s' % (family, major_version, minor_version)
        elif major_version:
            return '%s %s' % (family, major_version)
        return family

    @classmethod
    def parts_to_string_list(cls, family, major_version=None, minor_version=None, beta_version=None):
        """Return a list of user agent version strings.

        e.g. ['Firefox', 'Firefox 3', 'Firefox 3.5']
        """
        string_list = []
        if family:
            string_list.append(family)
            if major_version:
                string_list.append(cls.pretty_print(family, major_version))
                if minor_version:
                    string_list.append(cls.pretty_print(family, major_version, minor_version))
                    if beta_version:
                        string_list.append(cls.pretty_print(family, major_version, minor_version, beta_version))
        return string_list

    @classmethod
    def parse_to_string_list(cls, pretty_string):
        """Parse a pretty string into string list."""
        return cls.parts_to_string_list(*cls.parse_pretty(pretty_string))
