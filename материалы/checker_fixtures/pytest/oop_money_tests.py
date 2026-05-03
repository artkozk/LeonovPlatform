from decimal import Decimal
from solution import Money


def test_money_add_same_currency():
    assert Money(Decimal('10.00'), 'RUB') + Money(Decimal('5.50'), 'RUB') == Money(Decimal('15.50'), 'RUB')


def test_money_rejects_other_currency():
    try:
        Money(Decimal('10.00'), 'RUB') + Money(Decimal('1.00'), 'USD')
    except ValueError:
        return
    raise AssertionError('different currencies must raise ValueError')
