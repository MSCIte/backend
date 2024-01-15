import sqlite3
import re

import models
import schema 

def normalize_reqs_str(str_):
    """Normalize the prereq string of a course

    TODO(mack): handle the following special cases:
        1) "CS/ECE 121"
    """

    # Split on non-alphanumeric characters (includes chars we split on)
    old_splits = re.compile('(\W+)').split(str_)
    # Newly normalized splits
    new_splits = []
    # Last department id encountered as we traverse prereq str
    last_dep_id = None

    # Traverse the splits
    for split in old_splits:
        new_split = split
        if last_dep_id and re.findall(r'^[0-9]{3}[a-z]?$', split.lower()):
            # If there's a previous dep id and this matches the number portion
            # of a course, check if this is a valid course
            # NOTE: we're not validating whether the course exists since
            # we should still normalize to make the output to look consistent,
            # even when the course does not exist
            new_split = last_dep_id.upper() + split
        elif (re.findall('^[A-Z]+', split) and
              m.Department.objects.with_id(split.lower())):
            # We check it's uppercase, so we don't have false positives like
            # "Earth" that was part of "Earth Science student"

            last_dep_id = split.lower()
            # Do not include the department id since it will be included
            # with the course we find
            new_split = ''

        new_splits.append(new_split)

        # We're here if this split matches a department id
        # Increment idx by 1 more to skip the next non-alphanum character

    new_str = ''.join(new_splits)
    # While removing department ids, we could have left redundant spaces
    # (e.g. "CS 247" => " CS247", so remove them now.
    return re.sub('\s+', ' ', new_str).strip()

def clean_requirements_description():

    pass

def clean():
    with sqlite3.connect('../data/db.sqlite') as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM courses LIMIT 2')
        print(cur.fetchall())
        for row in cur:
            print(row)


