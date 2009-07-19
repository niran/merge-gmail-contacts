#!/usr/bin/env python
#
# merge_csv_contacts.py
#
# Given a CSV file in Google's contacts format, merge the rows with the same name.
# Usage: ./merge_csv_contacts.py <source> <output filename>
#
# Copyright 2009 Niran Babalola
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import re

with open(sys.argv[1], 'r') as original_file:
    rows = tuple(line for line in original_file)

def parse_line(line):
    values = []
    last_index = 0
    line = line.strip()

    for match in re.finditer(r'"(.*?)",?', line):
        # The unprocessed part of the line before the quoted match is normal comma-
        # separated values. Split it.
        if match.start() > last_index:
            values.extend(line[last_index:match.start()].split(','))

        values.append(match.group(1))
        last_index = match.end()

    # No more quoted values. Split the rest of the line.
    if len(line) > last_index:
        values.extend(line[last_index:].split(','))

    return values

column_names = parse_line(rows[0])

contacts = {} # {'name': data}
unnamed_rows = []

def process_row(row):
    values = parse_line(row)

    # Give empty values for trailing columns that were omitted so we can zip the
    # column names with the row.
    values = values + ([''] * (len(column_names) - len(values)))

    row_data = dict(zip(column_names, values))
    contact_name = row_data['Name']
    
    if contact_name == '':
        unnamed_rows.append(row_data)
    elif contact_name in contacts:
        merged_data = contacts[contact_name]

        for col in column_names[1:]:
            merged_val = merged_data[col]
            row_val = row_data[col]
            if merged_val != row_val and merged_val != '' and row_val != '':
                if 'Description' in col:
                    # When Gmail merges values with different descriptions, it looks
                    # like it changes the description to 'Other'. Do that.
                    if merged_data[col] != row_data[col]:
                        merged_data[col] = 'Other'
                        continue
                else:
                    # ' ::: ' is used as the separator for multiple values.
                    merged_data[col] = '%s ::: %s' % (merged_val, row_val)

            # One or none of the rows have a value for this column. Merge them.
            merged_data[col] = merged_data[col] or row_data[col]
    else:
        contacts[contact_name] = row_data

for row in rows[1:]:
    process_row(row)

def process_emails(row_data):
    """Remove duplicate email addresses and ensure that the 'E-mail' column has one
       or zero emails."""
    columns = 'E-mail', 'Section 1 - Email', 'Section 2 - Email'
    email, sec_one, sec_two = (row_data[col] for col in columns)
    overflow = set()

    if email:
        # Use the first email as the primary email and push any others to Section 1
        col_emails = email.split(' ::: ')
        row_data[columns[0]] = col_emails[0]
        if len(col_emails) > 1:
            overflow.update(col_emails[1:])

    if sec_one:
        col_emails = set(sec_one.split(' ::: '))
        col_emails |= overflow
        col_emails.discard(row_data[columns[0]]) # Remove email we've stored
        row_data[columns[1]] = ' ::: '.join(col_emails)
    else:
        row_data[columns[1]] = ' ::: '.join(overflow)

    if sec_two:
        col_emails = set(sec_two.split(' ::: '))
        col_emails.discard(row_data[columns[0]])
        col_emails.difference_update(row_data[columns[1]].split(' ::: '))
        row_data[columns[2]] = ' ::: '.join(col_emails)

# This list doesn't include 'Email' because we deal with that in process_emails.
SECTION_COLS = 'IM', 'Phone', 'Mobile', 'Pager', 'Fax', 'Company', 'Title', 'Other', 'Address'

def remove_dupes(row_data):
    for col in SECTION_COLS:
        values = set()
        for section in (1, 2):
            key = 'Section %d - %s' % (section, col)
            if row_data[key]:
                sec_values = set(row_data[key].split(' ::: '))
                sec_values -= values
                row_data[key] = ' ::: '.join(sec_values)
                values |= sec_values

def row_to_string(row):
    try:
        values = tuple(row[col] for col in column_names)
    except TypeError:
        values = row

    quoted = ('"%s"' % value if value.find(',') != -1 else value for value in values)
    return ','.join(quoted)

with open(sys.argv[2], 'w') as output_file:
    output_file.write(row_to_string(column_names) + '\n')

    for row in unnamed_rows:
        output_file.write(row_to_string(row) + '\n')

    for name in sorted(contacts.keys()):
        row = contacts[name]
        process_emails(row)
        remove_dupes(row)
        output_file.write(row_to_string(row) + '\n')
