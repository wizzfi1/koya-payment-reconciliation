import json
import unittest
from decimal import Decimal
from reconcile import reconcile


def event(txn_id, status, amount, day):
    return json.dumps(dict(txn_id=txn_id, status=status, amount=amount,
                           currency='NGN', ts=f'2026-09-{day:02d}T00:00:00Z'))


class ReconciliationTests(unittest.TestCase):
    def test_latest_attempt_wins_regardless_of_file_order(self):
        rows = [event('a', 'failed', 100, 2), event('a', 'success', 100, 1),
                event('b', 'success', 200, 3), event('b', 'pending', 200, 1),
                event('c', 'success', 300, 1), event('c', 'pending', 300, 2)]
        self.assertEqual(reconcile(rows), (1, Decimal('200')))
        self.assertEqual(reconcile(reversed(rows)), (1, Decimal('200')))

    def test_unreadable_lines_and_missing_ids_are_ignored(self):
        rows = ['', '{broken', '{}', 'null', event('', 'success', 900, 1),
                event('valid', 'success', 25, 1)]
        self.assertEqual(reconcile(rows), (1, Decimal('25')))

    def test_formatted_amounts_and_decimal_precision(self):
        rows = [event('a', 'success', '1,234.56', 1),
                event('b', 'success', 0.1, 1), event('c', 'success', 0.2, 1)]
        self.assertEqual(reconcile(rows), (3, Decimal('1234.86')))

    def test_repeated_event_is_counted_once(self):
        row = event('a', 'success', 10, 1)
        self.assertEqual(reconcile([row, row]), (1, Decimal('10')))


if __name__ == '__main__':
    unittest.main()
