class Constants():

    # Constants used to specify comment states.
    STATE_DELETED = 0
    STATE_TRASH = 100
    STATE_SPAM = 200
    STATE_PENDING = 300
    STATE_VISIBLE = 400

    CONTENT_STATES = (
        (STATE_DELETED, 'Deleted and awaiting purge batch job.'),
        (STATE_TRASH, 'In the trash bin.'),
        (STATE_SPAM, 'SPAM.'),
        (STATE_PENDING, 'Awaiting page owners moderation.'),
        (STATE_VISIBLE, 'Visible to all.'),
    )
