#!/usr/bin/python2.5
#
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

"""Shared models."""

import re
import yaml

class UserAgentParser(object):
    def __init__(self, pattern, family_replacement=None, major_version_replacement=None):
        """Initialize UserAgentParser.

        Args:
            pattern: a regular expression string
            family_replacement: a string to override the matched family (optional)
            major_version_replacement: a string to override the matched major_version (optional)
        """
        self.pattern = pattern
        self.user_agent_re = re.compile(self.pattern)
        self.family_replacement = family_replacement
        self.major_version_replacement = major_version_replacement

    def MatchSpans(self, user_agent_string):
        match_spans = []
        match = self.user_agent_re.search(user_agent_string)
        if match:
            match_spans = [match.span(group_index)
                                         for group_index in range(1, match.lastindex + 1)]
        return match_spans

    def Parse(self, user_agent_string):
        family, major_version, minor_version, beta_version = None, None, None, None
        match = self.user_agent_re.search(user_agent_string)
        if match:
            if self.family_replacement:
                if re.search(r'\$1', self.family_replacement):
                    family = re.sub(r'\$1', match.group(1), self.family_replacement)
                else:
                    family = self.family_replacement
            else:
                family = match.group(1)

            if self.major_version_replacement:
                major_version = self.major_version_replacement
            elif match.lastindex >= 2:
                major_version = match.group(2)
            if match.lastindex >= 3:
                minor_version = match.group(3)
                if match.lastindex >= 4:
                    beta_version = match.group(4)
        return family, major_version, minor_version, beta_version


def Parse(user_agent_string, js_user_agent_string=None,
                    js_user_agent_family=None,
                    js_user_agent_major_version=None,
                    js_user_agent_minor_version=None,
                    js_user_agent_beta_version=None):
    """Parses the user-agent string and returns the bits.

    Args:
        user_agent_string: The full user-agent string.
        js_user_agent_string: JavaScript ua string from client-side
        js_user_agent_family: This is an override for the family name to deal
                with the fact that IE platform preview (for instance) cannot be
                distinguished by user_agent_string, but only in javascript.
        js_user_agent_major_version: major_version override - see above.
        js_user_agent_minor_version: major_version override - see above.
        js_user_agent_beta_version: major_version override - see above.
    Returns:
        [family, major_version, minor_version, beta_version]
        e.g. ['Chrome', '4', '0', '203']
    """

    # Override via JS properties.
    if js_user_agent_family is not None and js_user_agent_family != '':
        family = js_user_agent_family
        major_version = None
        minor_version = None
        beta_version = None
        if js_user_agent_major_version is not None:
            major_version = js_user_agent_major_version
        if js_user_agent_minor_version is not None:
            minor_version = js_user_agent_minor_version
        if js_user_agent_beta_version is not None:
            beta_version = js_user_agent_beta_version
    else:
        for parser in USER_AGENT_PARSERS:
            family, major_version, minor_version, beta_version = parser.Parse(user_agent_string)
            if family:
                break

    # Override for Chrome Frame IFF Chrome is enabled.
    if (js_user_agent_string and js_user_agent_string.find('Chrome/') > -1 and
            user_agent_string.find('chromeframe') > -1):
        family = 'Chrome Frame (%s %s)' % (family, major_version)
        cf_family, major_version, minor_version, beta_version = Parse(js_user_agent_string)

    return family or 'Other', major_version, minor_version, beta_version

def GetFilters(user_agent_string, js_user_agent_string=None,
                             js_user_agent_family=None,
                             js_user_agent_major_version=None,
                             js_user_agent_minor_version=None,
                             js_user_agent_beta_version=None):
    """Return the optional arguments that should be saved and used to query.

    js_user_agent_string is always returned if it is present. We really only need
    it for Chrome Frame. However, I added it in the generally case to find other
    cases when it is different. When the recording of js_user_agent_string was
    added, we created new records for all new user agents.

    Since we only added js_document_mode for the IE 9 preview case, it did not
    cause new user agent records the way js_user_agent_string did.

    js_document_mode has since been removed in favor of individual property
    overrides.

    Args:
        user_agent_string: The full user-agent string.
        js_user_agent_string: JavaScript ua string from client-side
        js_user_agent_family: This is an override for the family name to deal
                with the fact that IE platform preview (for instance) cannot be
                distinguished by user_agent_string, but only in javascript.
        js_user_agent_major_version: major_version override - see above.
        js_user_agent_minor_version: major_version override - see above.
        js_user_agent_beta_version: major_version override - see above.
    Returns:
        {js_user_agent_string: '[...]', js_family_name: '[...]', etc...}
    """
    filters = {}
    filterdict = {
        'js_user_agent_string': js_user_agent_string,
        'js_user_agent_family': js_user_agent_family,
        'js_user_agent_major_version': js_user_agent_major_version,
        'js_user_agent_minor_version': js_user_agent_minor_version,
        'js_user_agent_beta_version': js_user_agent_beta_version
    }
    for key, value in filterdict.items():
        if value is not None and value != '':
            filters[key] = value
    return filters


# Build the list of user agent parsers from YAML
yamlFile = open('uaParser/resources/user_agent_parser.yaml')
yaml = yaml.load(yamlFile)
yamlFile.close()

USER_AGENT_PARSERS = []
for parser in yaml['user_agent_parsers']:
    regex = parser['regex']

    family_replacement = None
    if 'family_replacement' in parser:
        family_replacement = parser['family_replacement']

    major_version_replacement = None
    if 'major_version_replacement' in parser:
        major_version_replacement = parser['major_version_replacement']

    USER_AGENT_PARSERS.append(UserAgentParser(regex, family_replacement, major_version_replacement))
