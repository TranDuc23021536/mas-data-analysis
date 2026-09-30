from decimal import Decimal

from app.core.fact_check import find_unverified_numbers

CATEGORIES = [
    {"category_name": "Electronics", "revenue": Decimal("111.96")},
    {"category_name": "Books", "revenue": Decimal("76.50")},
    {"category_name": "Sports", "revenue": Decimal("55.00")},
    {"category_name": "Home & Kitchen", "revenue": Decimal("25.00")},
]


def test_valid_numbers_and_percentages_pass():
    text = (
        "Electronics có doanh thu cao nhất (111.96, chiếm 41.70% tổng doanh thu). "
        "Home & Kitchen thấp nhất (25.00, chỉ 9.31%). Electronics gấp khoảng 1,5 lần Books."
    )
    assert find_unverified_numbers(text, CATEGORIES) == []


def test_fabricated_amount_is_flagged():
    assert find_unverified_numbers("Electronics đạt 120,50 USD.", CATEGORIES) == ["120,50"]


def test_fabricated_percentage_is_flagged():
    assert find_unverified_numbers("Electronics chiếm 65% tổng doanh thu.", CATEGORIES) == ["65%"]


def test_vietnamese_thousand_separators_are_understood():
    rows = [{"ten": "Giay", "gia": 450000}, {"ten": "Ao", "gia": 120000}]
    assert find_unverified_numbers("Giày giá 450.000 đồng, áo giá 120 000 đồng.", rows) == []


def test_hedged_ratio_within_tolerance_passes():
    rows = [{"orders": 6, "stock": 1065}]
    assert find_unverified_numbers("Kho có 1.065 đơn vị, gấp hơn 170 lần số đơn hàng.", rows) == []


def test_numbers_without_data_are_flagged():
    assert find_unverified_numbers("Doanh thu đạt 1.500 USD.", []) == ["1.500"]


def test_text_without_numbers_passes():
    assert find_unverified_numbers("Không có dữ liệu phù hợp.", []) == []