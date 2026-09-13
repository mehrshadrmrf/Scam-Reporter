from app.models.enums import CaseStatus


def test_registered_can_move_to_pending_review():
    assert CaseStatus.PENDING_REVIEW in CaseStatus.allowed_transitions()[CaseStatus.REGISTERED]


def test_approved_cannot_move_back_to_pending_review():
    assert CaseStatus.PENDING_REVIEW not in CaseStatus.allowed_transitions()[CaseStatus.APPROVED]


def test_archived_is_a_terminal_state():
    assert CaseStatus.allowed_transitions()[CaseStatus.ARCHIVED] == set()


def test_rejected_can_be_reopened_for_review():
    assert CaseStatus.PENDING_REVIEW in CaseStatus.allowed_transitions()[CaseStatus.REJECTED]
