#!/usr/bin/python -OO
# Copyright 2010 The SABnzbd-Team <team@sabnzbd.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Extract translatable strings from all PY files

import glob
import os
import sys
import re

# Import version.py without the sabnzbd overhead
f = open('sabnzbd/version.py')
code = f.read()
f.close()
exec(code)

# Fixed information for the POT header
HEADER = r'''#
# SABnzbd Translation Template file __TYPE__
# Copyright (C) 2010 by the SABnzbd Team
#   team@sabnzbd.org
#
msgid ""
msgstr ""
"Project-Id-Version: SABnzbd-%s\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: shypike@sabnzbd.org\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=ASCII\n"
"Content-Transfer-Encoding: 7bit\n"
''' % __version__

PO_DIR = 'po/main'
POE_DIR = 'po/email'
PON_DIR = 'po/nsis'
DOMAIN = 'SABnzbd'
DOMAIN_EMAIL = 'SABemail'
DOMAIN_NSIS = 'SABnsis'
PARMS = '-d %s -p %s -k T -k Ta -k TT -o %s.pot.tmp' % (DOMAIN, PO_DIR, DOMAIN)
FILES = 'SABnzbd.py SABHelper.py SABnzbdDelegate.py sabnzbd/*.py sabnzbd/utils/*.py'

if not os.path.exists(PO_DIR):
    os.makedirs(PO_DIR)

# Determine location of PyGetText tool
path, exe = os.path.split(sys.executable)
if os.name == 'nt':
    TOOL = os.path.join(path, r'Tools\i18n\pygettext.py')
else:
    TOOL = os.path.join(path, 'pygettext.py')
if not os.path.exists(TOOL):
    TOOL = 'pygettext.py'



cmd = '%s %s %s' % (TOOL, PARMS, FILES)
print cmd
os.system(cmd)

# Post-process the POT file
src = open('%s/%s.pot.tmp' % (PO_DIR, DOMAIN), 'r')
dst = open('%s/%s.pot' % (PO_DIR, DOMAIN), 'wb')
dst.write(HEADER.replace('__TYPE__', 'MAIN'))
header = True

for line in src:
    if line.startswith('#:'):
        line = line.replace('\\', '/')
        if header:
            dst.write('\n\n')
        header = False
    if header:
        if not ('"POT-Creation-Date:' in line or '"Generated-By:' in line):
            continue
    dst.write(line)

src.close()
dst.close()
os.remove('%s/%s.pot.tmp' % (PO_DIR, DOMAIN))


# Create the email POT file
if not os.path.exists(POE_DIR):
    os.makedirs(POE_DIR)
dst = open(os.path.join(POE_DIR, DOMAIN_EMAIL+'.pot'), 'wb')
dst.write(HEADER.replace('__TYPE__', 'EMAIL'))

src = open('language/email-en.tmpl', 'r')
dst.write('\n#: email/email.tmpl:1\n')
dst.write('msgid ""\n')
for line in src:
    dst.write('"%s"\n' % line.replace('\n', '\\n').replace('"', '\\"'))
dst.write('msgstr ""\n\n')
src.close()

src = open('language/rss-en.tmpl', 'r')
dst.write('#: email/rss.tmpl:1\n')
dst.write('msgid ""\n')
for line in src:
    dst.write('"%s"\n' % line.replace('\n', '\\n').replace('"', '\\"'))
dst.write('msgstr ""\n\n')
src.close()

dst.close()


# Create the NSIS POT file
NSIS= 'NSIS_Installer.nsi'
RE_NSIS = re.compile(r'LangString\s+\w+\s+\$\{LANG_ENGLISH\}\s+(".*)', re.I)

print 'Creating the NSIS POT file'
if not os.path.exists(PON_DIR):
    os.makedirs(PON_DIR)
src = open(NSIS, 'r')
dst = open(os.path.join(PON_DIR, DOMAIN_NSIS+'.pot'), 'w')
dst.write(HEADER.replace('__TYPE__', 'NSIS'))
dst.write('\n')
count = 0
for line in src:
    count += 1
    m = RE_NSIS.search(line)
    if m:
        dst.write('#: %s:%s\n' % (NSIS, count))
        text = m.group(1).replace('$\\"', '\\"').replace('$\\', '\\')
        dst.write('msgid %s\n' % text)
        dst.write('msgstr ""\n\n')
dst.close()
src.close()