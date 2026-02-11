from meetup_gmail_calendar_sync.auth import _scope_satisfied
from meetup_gmail_calendar_sync.config import GMAIL_MODIFY_SCOPE, GMAIL_READ_SCOPE


def test_gmail_modify_satisfies_read_scope():
    assert _scope_satisfied(GMAIL_READ_SCOPE, [GMAIL_MODIFY_SCOPE])
