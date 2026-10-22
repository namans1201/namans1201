import unittest
from datetime import date, timedelta
import xml.etree.ElementTree as ET
from scripts.profile_stats import calculate_stats, render_card


class ContributionStatsTests(unittest.TestCase):
    def history(self, start, counts):
        start = date.fromisoformat(start)
        return {start+timedelta(days=i): n for i, n in enumerate(counts)}

    def test_lifetime_total_and_longest_cross_year(self):
        days = self.history('2025-12-29', [1, 2, 3, 4, 0, 8])
        stats = calculate_stats(days, date(2026, 1, 3))
        self.assertEqual((stats['total'], stats['longest'], stats['current']), (18, 4, 1))
        self.assertEqual((stats['longest_start'], stats['longest_end']), ('2025-12-29', '2026-01-01'))

    def test_yesterdays_streak_survives_an_unfinished_today(self):
        stats = calculate_stats(self.history('2026-10-20', [1, 2, 1, 0]), date(2026, 10, 23))
        self.assertEqual(stats['current'], 3)
        self.assertEqual(stats['current_end'], '2026-10-22')

    def test_two_inactive_days_break_current_streak(self):
        stats = calculate_stats(self.history('2026-10-20', [1, 2, 0, 0]), date(2026, 10, 23))
        self.assertEqual(stats['current'], 0)
        self.assertIsNone(stats['current_start'])
        self.assertEqual(stats['longest'], 2)

    def test_empty_calendar_has_no_streak(self):
        stats = calculate_stats({}, date(2026, 10, 23))
        self.assertEqual((stats['total'], stats['current'], stats['longest']), (0, 0, 0))
        self.assertIsNone(stats['longest_end'])

    def test_missing_days_do_not_join_longest_streaks(self):
        days = {date(2026, 10, 20): 2, date(2026, 10, 22): 3}
        stats = calculate_stats(days, date(2026, 10, 23))
        self.assertEqual(stats['longest'], 1)
        self.assertEqual(stats['current'], 1)

    def test_future_days_are_excluded(self):
        stats = calculate_stats(self.history('2026-10-23', [2, 100]), date(2026, 10, 23))
        self.assertEqual((stats['total'], stats['current'], stats['longest']), (2, 1, 1))

    def test_inactive_history_has_zero_metrics(self):
        stats = calculate_stats(self.history('2026-10-20', [0, 0, 0, 0]), date(2026, 10, 23))
        self.assertEqual((stats['total'], stats['current'], stats['longest']), (0, 0, 0))

    def test_all_card_variants_are_valid_accessible_svg(self):
        stats = calculate_stats(self.history('2026-10-20', [1, 2, 1, 0]), date(2026, 10, 23))
        for dark in (False, True):
            for compact in (False, True):
                xml = render_card(stats, 'example', '2026-10-20', '23 Oct 2026', dark, compact)
                root = ET.fromstring(xml)
                self.assertEqual(root.attrib['role'], 'img')
                self.assertIn('3 day current streak', xml)
                self.assertEqual(root.attrib['width'], '420' if compact else '840')


if __name__ == '__main__':
    unittest.main()
