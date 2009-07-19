#!/usr/bin/env python
# Usage: ./merge_csv_contacts.py <source> <output filename>

import sys
import re

with open(sys.argv[1], 'r') as original_file:
    rows = tuple(line for line in original_file)

def parse_line(line):
    values = []
    last_index = 0
    line = line.strip()

    for match in re.finditer(r'"(.*?)"', line):
        # The unprocessed part of the line before the quoted match is normal comma-
        # separated values. Split it.
        values.extend(line[last_index:match.start()].split(','))

        values.append(match.group(1))
        last_index = match.end()

    # No more quoted values. Split the rest of the line.
    values.extend(line[last_index:].split(','))

    return values

column_names = parse_line(rows[0])

# contacts = {
#     'John Doe': {
#         'merged': A row of merged contact data,
#         'rows': The rows the merged data came from
#     },
# }
contacts = {} 

unmodified_contacts = {} # {'John Doe': [row, row, row...]}
untouchables = set() # Names.

def process_row(row):
    values = parse_line(row)

    # Give empty values for trailing columns that were omitted so we can zip the
    # column names with the row.
    values = values + ([''] * (len(column_names) - len(values)))

    row_data = dict(zip(column_names, values))
    contact_name = row_data['Name']
    
    if contact_name == '' or contact_name in untouchables:
        unmodified_contacts.setdefault(contact_name, []).append(row_data)
    elif contact_name in contacts:
        existing_info = contacts[contact_name]
        merged_data = existing_info['merged']

        # Store each row being merged so we can unmerge if rows conflict.
        existing_info['rows'].append(row_data)

        for col in column_names[1:]:
            merged_val = merged_data[col]
            row_val = row_data[col]
            if merged_val != row_val and merged_val != '' and row_val != '':
                if col.find('Description') == -1:
                    # It looks like all of my duplicates are either just numbers (from
                    # my phone) or just email addresses (from my email). If I'm wrong,
                    # print a notice...
                    print ('%s has at least two values for %s: "%s" and "%s"' %
                           (contact_name, col, merged_data[col], row_data[col]))
                    # ... queue the unmerged rows to be printed...
                    unmodified_contacts[contact_name] = existing_info['rows']
                    # ... dequeue the merged row...
                    del contacts[contact_name]
                    # ... and don't try to merge this person anymore.
                    untouchables.add(contact_name)
                    return
                else:
                    # When GMail merges values with different descriptions, it looks
                    # like it changes the description to 'Other'. Do that.
                    if merged_data[col] != row_data[col]:
                        merged_data[col] = 'Other'
                        continue

            # One or none of the rows have a value for this column. Merge them.
            merged_data[col] = merged_data[col] or row_data[col]
    else:
        contacts[contact_name] = {'merged': row_data, 'rows': [row_data]}

for row in rows[1:]:
    process_row(row)

unmerged_names = tuple(name for name in unmodified_contacts if name != '')
if unmerged_names:
    print "-----------"
    print "The contacts with multiple values for a field were not merged, so you should merge them manually in GMail (http://lifehacker.com/5150139/merge-multiple-emails-to-one-contact-in-gmail). Here they are again:"
    print ', '.join(unmerged_names)

with open(sys.argv[2], 'w') as output_file:
    output_file.write(','.join(column_names) + '\n')

    for name in sorted(unmodified_contacts.keys()):
        for row in unmodified_contacts[name]:
            output_file.write(','.join(row[col] for col in column_names) + '\n')

    for name in sorted(contacts.keys()):
        output_file.write(','.join(contacts[name]['merged'][col] for
                                   col in column_names) + '\n')
