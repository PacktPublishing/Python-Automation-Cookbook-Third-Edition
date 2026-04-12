import os

NOTES_DIR = './data'


def available_notes():
    ''' Retrieve all available notes '''

    notes = []
    for filename in os.listdir(NOTES_DIR):
        if filename.endswith('.md'):
            notes.append(filename.strip('.md'))

    return notes


def retrieve_note(user):
    '''
    Retrieve the note from a user
    '''
    filename = os.path.join(NOTES_DIR, f'{user}.md')
    with open(filename) as fp:
        note = fp.read()

    return note


def write_meeting_brief(user, date, text):
    '''
    Append into the note for the user the brief for the
    next meeting
    '''
    filename = os.path.join(NOTES_DIR, f'{user}.md')

    # Check that the file exists
    if not os.path.exists(filename):
        return f'ERROR: NOTE FOR {user} DOES NOT EXIST. USE AN EXISTING NOTE'

    with open(filename, 'a') as fp:
        data = f'''## Meeting brief for {date}
        {text}
        '''
        fp.write(data)

    return 'SUCCESS'


if __name__ == '__main__':
    # Small check retrieving the first user note
    notes = available_notes()
    print(notes)
    print(retrieve_note(notes[0]))
