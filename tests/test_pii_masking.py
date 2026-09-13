from app.services.pii_masking_service import PIIMaskingService


def test_mask_card_number_standard_length():
    masked = PIIMaskingService.mask_card_number("6037991234567890")
    assert masked.startswith("603799")
    assert masked.endswith("7890")
    assert "*" in masked


def test_mask_card_number_none():
    assert PIIMaskingService.mask_card_number(None) is None


def test_mask_phone_number_standard():
    masked = PIIMaskingService.mask_phone_number("09121234567")
    assert masked.startswith("0912")
    assert masked.endswith("67")


def test_mask_phone_number_strips_non_digits():
    masked = PIIMaskingService.mask_phone_number("+98 912 123 4567")
    assert masked is not None
    assert all(ch.isdigit() or ch == "*" for ch in masked)
