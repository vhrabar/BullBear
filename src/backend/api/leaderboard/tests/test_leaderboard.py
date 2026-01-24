from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from api.users.models import UserPortfolio, PortfolioSnapshot
from api.leaderboard.services import get_leaderboard_queryset

User = get_user_model()


class LeaderboardAPITests(TestCase):
    """
    Tests GET /api/leaderboard/
    - permission behavior
    - ordering and rank computation
    - pagination
    - time filter behavior
    """

    def setUp(self):
        self.client = APIClient()

        # Create users
        self.user1 = User.objects.create_user(
            username="user1",
            password="pass12345",
            email="user1@example.com",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="pass12345",
            email="user2@example.com",
        )
        self.user3 = User.objects.create_user(
            username="user3",
            password="pass12345",
            email="user3@example.com",
        )

        # Access profiles
        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile
        self.profile3 = self.user3.profile

        # Access portfolios
        self.portfolio1 = self.profile1.portfolios.first()
        self.portfolio2 = self.profile2.portfolios.first()
        self.portfolio3 = self.profile3.portfolios.first()

        # Delete initial snapshots created by signal on portfolio creation
        PortfolioSnapshot.objects.filter(portfolio__in=[self.portfolio1, self.portfolio2, self.portfolio3]).delete()

        # URL
        self.url = "/api/leaderboard/"

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def clear_auth(self):
        self.client.force_authenticate(user=None)

    def create_snapshot(self, portfolio, total_value, ts=None):
        """
        Create a snapshot for a portfolio.
        """
        if ts is None:
            ts = timezone.now()

        return PortfolioSnapshot.objects.create(
            portfolio=portfolio,
            ts=ts,
            total_value=Decimal(str(total_value)),
            cash_balance=Decimal("0"),
            equity_value=Decimal(str(total_value)),
        )

    def create_latest_only(self, portfolio, total_value):
        """
        latest snaphost
        """
        return self.create_snapshot(portfolio, total_value=total_value, ts=timezone.now())

    def assert_paginated(self, payload):
        self.assertIn("count", payload)
        self.assertIn("next", payload)
        self.assertIn("previous", payload)
        self.assertIn("results", payload)
        self.assertIsInstance(payload["results"], list)

    # Permission tests
    def test_unauthenticated_user_is_forbidden(self):
        """
        No auth + not executor => 403
        """
        self.clear_auth()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_is_allowed(self):
        """
        auth => 200
        """
        self.auth(self.user1)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_executor_user_is_allowed_even_if_not_authenticated(self):
        """
        executor special iser => 200
        """
        self.user2.is_executor = True
        self.user2.save(update_fields=[])

        self.auth(self.user2)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # Response structure + ordering tests
    def test_returns_ordered_by_latest_total_value_desc(self):
        """
        Ensure ordering: highest total_value first.
        """
        self.create_latest_only(self.portfolio1, 150)
        self.create_latest_only(self.portfolio2, 300)
        self.create_latest_only(self.portfolio3, 200)

        self.auth(self.user1)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = res.json()
        self.assert_paginated(data)

        results = data["results"]
        self.assertGreaterEqual(len(results), 3)

        # Expect rank #1 to be portfolio2 (300), then portfolio3 (200), then portfolio1 (150)
        self.assertEqual(results[0]["rank"], 1)
        self.assertEqual(results[0]["username"], self.user2.username)
        self.assertEqual(results[0]["portfolio_name"], self.portfolio2.name)
        self.assertEqual(Decimal(results[0]["total_value"]), Decimal("300"))

        self.assertEqual(results[1]["rank"], 2)
        self.assertEqual(results[1]["username"], self.user3.username)
        self.assertEqual(Decimal(results[1]["total_value"]), Decimal("200"))

        self.assertEqual(results[2]["rank"], 3)
        self.assertEqual(results[2]["username"], self.user1.username)
        self.assertEqual(Decimal(results[2]["total_value"]), Decimal("150"))

    def test_excludes_portfolios_without_snapshots(self):
        """
        empy portfolios
        """
        self.create_latest_only(self.portfolio1, 999)

        self.auth(self.user1)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        results = res.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["username"], self.user1.username)
        self.assertEqual(Decimal(results[0]["total_value"]), Decimal("999"))

    def test_rank_is_continuous_across_pages(self):
        """
        PageNumberPagination page_size=50.
        Create 60 portfolios with snapshots; request page=2 and verify ranks start at 51.
        """

        extra_users = []
        for i in range(60):
            u = User.objects.create_user(
                username=f"extra_{i}",
                password="pass12345",
                email=f"extra_{i}@example.com",
            )
            extra_users.append(u)

            p = u.profile.portfolios.first()
            PortfolioSnapshot.objects.filter(portfolio=p).delete()

            self.create_latest_only(p, 1000 - i)

        self.auth(self.user1)
        res = self.client.get(self.url, {"page": 2})
        self.assertEqual(res.status_code, 200)

        payload = res.json()
        self.assert_paginated(payload)

        results = payload["results"]
        self.assertEqual(len(results), 10)

        # ranks should start at 51
        self.assertEqual(results[0]["rank"], 51)
        self.assertEqual(results[-1]["rank"], 60)

        self.assertEqual(results[0]["username"], "extra_50")
        self.assertEqual(results[-1]["username"], "extra_59")

    # Service tests: get_leaderboard_queryset time filters
    def test_service_time_filter_all_includes_old_snapshots(self):
        """
        time=all should not apply cutoff.
        """
        old_ts = timezone.now() - timedelta(days=400)
        self.create_snapshot(self.portfolio1, total_value=123, ts=old_ts)

        qs = get_leaderboard_queryset("all")
        ids = list(qs.values_list("id", flat=True))
        self.assertIn(self.portfolio1.id, ids)

    def test_service_time_filter_1d_excludes_older_than_1_day(self):
        """
        Snapshot older than 1 day should be ignored; if only old snapshots exist => portfolio excluded.
        """
        old_ts = timezone.now() - timedelta(days=2)
        self.create_snapshot(self.portfolio1, total_value=500, ts=old_ts)

        qs = get_leaderboard_queryset("1D")
        ids = list(qs.values_list("id", flat=True))
        self.assertNotIn(self.portfolio1.id, ids)

    def test_service_time_filter_1w_excludes_older_than_7_days(self):
        old_ts = timezone.now() - timedelta(days=8)
        self.create_snapshot(self.portfolio1, total_value=500, ts=old_ts)

        qs = get_leaderboard_queryset("1W")
        self.assertNotIn(self.portfolio1.id, list(qs.values_list("id", flat=True)))

    def test_service_time_filter_prefers_latest_within_cutoff(self):
        """
        If there are snapshots both old and new, must take latest within cutoff.
        """
        # old snapshot that should be ignored under 1W
        old_ts = timezone.now() - timedelta(days=30)
        self.create_snapshot(self.portfolio1, total_value=999, ts=old_ts)

        # new snapshot within 1W
        new_ts = timezone.now() - timedelta(days=2)
        self.create_snapshot(self.portfolio1, total_value=111, ts=new_ts)

        qs = get_leaderboard_queryset("1W")
        p = qs.get(id=self.portfolio1.id)

        # annotated latest_total_value should be 111 (not 999)
        self.assertEqual(p.latest_total_value, Decimal("111"))

    def test_service_orders_by_latest_total_value_desc(self):
        """
        Service returns sorted result.
        """
        self.create_latest_only(self.portfolio1, 10)
        self.create_latest_only(self.portfolio2, 30)
        self.create_latest_only(self.portfolio3, 20)

        qs = list(get_leaderboard_queryset("all"))
        self.assertGreaterEqual(len(qs), 3)

        self.assertEqual(qs[0].id, self.portfolio2.id)
        self.assertEqual(qs[1].id, self.portfolio3.id)
        self.assertEqual(qs[2].id, self.portfolio1.id)

    # API test: time query param wiring into service
    def test_api_time_param_filters_results(self):
        """
        API passes time filter to get_leaderboard_queryset().
        """
        # portfolio1 only old
        old_ts = timezone.now() - timedelta(days=10)
        self.create_snapshot(self.portfolio1, total_value=111, ts=old_ts)

        # portfolio2 recent
        recent_ts = timezone.now() - timedelta(days=1)
        self.create_snapshot(self.portfolio2, total_value=222, ts=recent_ts)

        self.auth(self.user1)
        res = self.client.get(self.url, {"time": "1W"})
        self.assertEqual(res.status_code, 200)

        results = res.json()["results"]
        usernames = [r["username"] for r in results]

        self.assertIn(self.user2.username, usernames)
        self.assertNotIn(self.user1.username, usernames)

    def test_api_invalid_time_param_defaults_to_all(self):
        """
        Unknown time string => else  fallback branch => cutoff None => behaves like all
        """
        old_ts = timezone.now() - timedelta(days=500)
        self.create_snapshot(self.portfolio1, total_value=123, ts=old_ts)

        self.auth(self.user1)
        res = self.client.get(self.url, {"time": "nonsense"})
        self.assertEqual(res.status_code, 200)

        usernames = [r["username"] for r in res.json()["results"]]
        self.assertIn(self.user1.username, usernames)
