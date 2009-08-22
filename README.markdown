Automatically Merge Google/Gmail Contacts
=========================================

merge_csv_contacts.py
---------------------

Usage: `./merge_csv_contacts.py <source> <output filename>`

#### Why would I want to use this?

People have multiple email addresses, and Gmail doesn't do anything to help you to indicate that those people with the same name are actually the same person. You can [manually merge contacts][1], but that's no fun.

[1]: http://lifehacker.com/5150139/merge-multiple-emails-to-one-contact-in-gmail

It's even worse when you've exported your contacts from your phone and imported them into Gmail, only to get a separate phone number contact for each person. This particular annoyance inspired this script.

#### You should probably use the Mac Address Book instead.

Apparently the Mac Address Book has a contact merging feature. If you have access to a Mac, export your contacts from Google, import them into Address Book, merge your contacts, then export them back to Google. If you don't have access to a Mac, keep reading.

#### Instructions

1. Export your contacts from Gmail.
2. Check the first line of the exported file. If you see fields like "Section 1 - Email", you're fine. If you see fields like "E-mail 1 - Value", this won't work. See [Issue 1](http://github.com/niran/merge-gmail-contacts/issues/closed/#issue/1) for more info.
3. Run merge_csv_contacts.py on the file you saved.
4. Open the output file in a spreadsheet program, such as OpenOffice.org Calc or Microsoft Excel, and look over it to make sure it looks reasonable. **You can't undo a contact import**, so if something's wrong, it'll be tedious to fix afterward.
5. Import the output file into GMail, assigning a new group to those contacts. (The new group is just to help you deal with any oddities that result from the import. Once you're satisfied, you can remove the group.) GMail will notice that your existing contacts have the same email addresses, etc, and it will merge the new ones with the duplicates, leaving one glorious entry per person.

If you want to merge contacts from another application, [import your contacts into Gmail][2], follow the rest of these instructions, then export the merged contacts into a format your application can read (the export page will explain the formats if you aren't sure).

[2]: http://mail.google.com/support/bin/answer.py?answer=12118&cbid=-1qlxpodsfyozq&src=cb&lev=answer

#### Caveat

As I mentioned above, my duplicates were mostly phone numbers that were separate from emails, so I was aiming to merge non-overlapping data into a single contact. I've added code to merge multiple values for the same attribute and it looks like it works, but I didn't have many cases where that was necessary, so buyer beware.

#### License

This code is [Apache licensed][3]. If you abide by the few restrictions of the license, you are allowed to freely redistribute it, modify it, and include it in your own code, even if it's closed source.

[3]: http://www.apache.org/licenses/LICENSE-2.0
