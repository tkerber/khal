import tempfile
import subprocess
import os
import sys

from datetime import date
from datetime import datetime


def external_editor(editor, event, current_day, locale):
    # get event template
    old_template = get_template(event, current_day, locale)
    # create temp file and open it with the specified text editor
    tf = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
    temp_file_name = tf.name
    tf.write(old_template)
    tf.close()
    # start editor to edit template
    # have tried .call .Popen and os.system - none have worked
    child = subprocess.Popen([editor, temp_file_name])
    child.communicate()[0]
    # read temp file contents after editing
    tf = open(temp_file_name, "r")
    new_template = tf.read()
    tf.close()
    os.remove(temp_file_name)
    # check if the user changed anything
    if old_template != new_template:
        new_event = process_user_input(new_template, locale)
        event.update_summary(new_event['summary'])
        event.update_description(new_event['description'])
        event.update_location(new_event['location'])
        event.update_start_end(new_event['from'], new_event['to'])
        # XXX take care of repition rules
        event.increment_sequence()
        return event
    else:
        return None


def get_agenda(current_day):
    """convert current_day to commented string

    :current_day: today's agenda
    :returns: commented string of today's agenda

    """
    # XXX perhaps rename current_day to agenda?
    agenda = []
    for event in current_day:
        agenda.append("# %s" % event.event_description)
    return '\n'.join(agenda)


def get_template(event, current_day, locale):
    if event.allday:
        dt_format = locale['longdateformat']
    else:
        dt_format = locale['longdatetimeformat']
    # XXX we could also format the example dates in the user's locale
    agenda = get_agenda(current_day)
# Calendar: %s
    if event.recurobject:
        freq = event.recurobject['freq'][0].lower() if 'freq' in event.recurobject else ''
        until = event.recurobject['until'][0].lower() if 'until' in event.recurobject else ''
    else:
        freq = ''
        until = ''

    return """# Edit Event
# if you want to cancel, exit without saving

Summary: %s
Location: %s
Description: %s

%s

# yes or no
Allday: %s

# From and To can be in any of the below formats:
# timeformat = %%H:%%M
# dateformat = %%d.%%m.
# longdateformat = %%d.%%m.%%Y
# datetimeformat =  %%d.%%m. %%H:%%M
# longdatetimeformat = %%d.%%m.%%Y %%H:%%M
# example:
#   From: 21.11.2017 9:30
#   To: 11:30
#
# **IMPORTANT**
# the above examples depict the default settings
# if you changed the settings in your config,
# you must use the format that you specified
From: %s
To: %s

# no, daily, weekly, monthly, or yearly
Repeat: %s

# will throw an error if Repeat is not set
# if set, must be set to a valid date or longdate format
Until: %s""" % (event.summary, event.location, event.description,
                agenda, event.allday,
                event.start_local.strftime(dt_format),
                event.end_local.strftime(dt_format),
                freq, until)


def process_user_input(input, locale):
    # parse user input string
    data = {}
    counter = 1
    # XXX what is this counter for?

    for line in input.splitlines():
        counter += 1
        if line == "" or line.startswith("#"):
            continue
        try:
            obj = line.split(':', 1)
            key = obj[0].strip().lower()
            value = obj[1].strip()
            data[key] = value.decode("utf-8")
            # TODO take care of 'text fields' that span multiple lines
        except IndexError:
            print("Error in input line %d: Malformed input\nLine: %s" %
                  (counter, line))
            sys.exit(1)
    # XXX with this you need to make the format fit the long formats
    # but obviously the short versions and only a time for the `to` setting
    # should be valid, too
    if data['allday'].lower() == 'true':
        data['allday'] = True
    else:
        data['allday'] = False

    if data['allday']:
        dt_format = locale['longdateformat']
    else:
        dt_format = locale['longdatetimeformat']

    data['from'] = datetime.strptime(data['from'], dt_format)
    data['to'] = datetime.strptime(data['to'], dt_format)

    if data['allday']:
        data['from'] = data['from'].date()
        data['to'] = data['to'].date()

    return data
