from decimal import Decimal
from solution import Money


def test_add_same_currency():
    assert Money(Decimal('10.00'), 'RUB') + Money(Decimal('5.50'), 'RUB') == Money(Decimal('15.50'), 'RUB')


def test_reject_different_currency():
    try:
        Money(Decimal('1'), 'RUB') + Money(Decimal('1'), 'USD')
    except ValueError:
        assert True
    else:
        assert False
