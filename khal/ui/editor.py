import tempfile
import subprocess
import os
import sys


def external_editor(editor, event, current_day):
    # get event template
    old_template = edit_template(event, current_day)
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
        new_event = process_user_input(new_template)
        if event.etag:
            return
            # update event
        else:
            return
            # add event


def get_agenda(current_day):
    """convert current_day to commented string

    :current_day: today's agenda
    :returns: commented string of today's agenda

    """
    agenda = []
    for event in current_day:
        agenda.append("# %s" % event)
    return '\n'.join(agenda)


def edit_template(event, current_day):
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
                agenda, event.allday, event.start_local, event.end_local,
                freq, until)


def process_user_input(input):
    return
    # parse user input string
    data = {}
    counter = 1
    for line in input.splitlines():
        counter += 1
        if line == "" or line.startswith("#"):
            continue
        try:
            obj = line.split(':', 1)
            key = obj[0].strip().lower()
            value = obj[1].strip()
            data[key] = value.decode("utf-8")
        except IndexError:
            print("Error in input line %d: Malformed input\nLine: %s" %
                  (counter, line))
            sys.exit(1)
