import uuid
from unittest.mock import ANY

from django.contrib.auth.models import User
from django.test import TestCase
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from lunch.models import Restaurant, UserVote

RESTAURANT_URL = reverse('restaurant-list')
RESTAURANT_URL_DETAIL = reverse('restaurant-detail', kwargs={"pk": 1})
VOTE_URL = reverse("restaurant-vote", kwargs={"pk": 1})


class LunchTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="Peter")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.prepopulate_db()

    @staticmethod
    def get_restaurant_payload():
        return {
            "name": f"SuperKebabs-{uuid.uuid4().hex[0:3]}",
            "description": "Kebabs for great price!"
        }

    def prepopulate_db(self):
        for x in range(0, 3):
            Restaurant.objects.create(**self.get_restaurant_payload())

    def test_should_return_201_on_restaurant_creation(self):
        # WHEN
        resp = self.client.post(RESTAURANT_URL, self.get_restaurant_payload())

        # THEN
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp.data.pop("url")
        self.assertTrue(Restaurant.objects.filter(**resp.data).exists())

    def test_should_return_200_on_repeated_restaurant_vote_and_check_scores(self):

        for i in range(0, 3):
            # WHEN
            resp = self.client.post(VOTE_URL)

            # THEN
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.assertEqual(UserVote.objects.filter(user=self.user).count(), i + 1)

    def test_user_point_calculation_on_diff_restaurants(self):

        user_points = [9, 8.5, 8.25, 8, 7, 6.5, 6.25, 6]
        restaurant_score = [1, 1.5, 1.75, 2]
        k = 0

        for pk in range(1, 3):
            for i in range(0, 4):
                # WHEN
                vote_url = reverse("restaurant-vote", kwargs={"pk": pk})
                resp = self.client.post(vote_url)

                # THEN
                self.assertEqual(resp.data["remaining_points"], user_points[k])
                k += 1
                restaurant_url = reverse("restaurant-detail", kwargs={"pk": pk})
                self.assertEqual(self.client.get(restaurant_url).data["score"], str(restaurant_score[i]))

    def test_user_point_reset_next_day(self):
        # GIVEN
        with freeze_time("2022-01-01"):
            for i in range(0, 4):
                self.client.post(VOTE_URL)
            self.assertEqual(self.client.get(VOTE_URL).data["remaining_points"], 8)

        # WHEN / THEN
        self.assertEqual(self.client.get(VOTE_URL).data["remaining_points"], 10)

    def test_should_return_restaurant_list(self):
        # WHEN
        resp = self.client.get(RESTAURANT_URL + "?ordering=id")

        # THEN
        expected_resp = []
        for i in range(1, 4):
            expected_resp.append({
                "url": f"http://testserver/restaurant/{i}/",
                "score": "0",
                "unique_users": "0",
                "name": ANY,
                "description": ANY
            })
        self.assertEqual(resp.json(), expected_resp)

    def test_should_return_list_by_date(self):
        # GIVEN

        vote_url_1 = reverse("restaurant-vote", kwargs={"pk": 1})
        vote_url_2 = reverse("restaurant-vote", kwargs={"pk": 2})
        with freeze_time("2022-01-01"):
            self.client.post(vote_url_1)
            self.client.post(vote_url_2)
        with freeze_time("2022-01-05"):
            self.client.post(vote_url_1)

        # WHEN / THEN
        resp = self.client.get(RESTAURANT_URL + "?ordering=id&by_date=2022-01-01")
        self.assertEqual(resp.data[0]["score"], "1")
        self.assertEqual(resp.data[1]["score"], "1")
        resp = self.client.get(RESTAURANT_URL + "?ordering=id&by_date=2022-01-05")
        self.assertEqual(resp.data[0]["score"], "1.5")
        self.assertEqual(resp.data[1]["score"], "1")
        resp = self.client.get(RESTAURANT_URL + "?ordering=id&by_date=2022-01-06")
        self.assertEqual(resp.data[0]["score"], "1.5")
        self.assertEqual(resp.data[1]["score"], "1")

    def test_should_return_detail_resp_by_date(self):
        # GIVEN
        with freeze_time("2022-01-01"):
            self.client.post(VOTE_URL)
        with freeze_time("2022-01-05"):
            self.client.post(VOTE_URL)

        # WHEN / THEN
        resp = self.client.get(RESTAURANT_URL_DETAIL + "?by_date=2022-01-01")
        self.assertEqual(resp.data["score"], "1")
        resp = self.client.get(RESTAURANT_URL_DETAIL + "?by_date=2022-01-05")
        self.assertEqual(resp.data["score"], "1.5")
        resp = self.client.get(RESTAURANT_URL_DETAIL + "?by_date=2022-01-06")
        self.assertEqual(resp.data["score"], "1.5")

    def test_should_return_winner_first(self):
        # GIVEN

        vote_url_1 = reverse("restaurant-vote", kwargs={"pk": 1})
        vote_url_2 = reverse("restaurant-vote", kwargs={"pk": 2})

        # Peter votes
        for i in range(0, 4):
            self.client.post(vote_url_1)
        self.client.post(vote_url_2)

        # Tommy votes
        user = User.objects.create(username="Tommy")
        self.client.force_authenticate(user=user)
        self.client.post(vote_url_2)

        # WHEN
        resp = self.client.get(RESTAURANT_URL)

        # THEN
        self.assertEqual(resp.data[0]["score"], "2")
        self.assertEqual(resp.data[0]["url"][-2], "2")
        self.assertEqual(resp.data[0]["unique_users"], "2")

        self.assertEqual(resp.data[1]["score"], "2")
        self.assertEqual(resp.data[1]["url"][-2], "1")
        self.assertEqual(resp.data[1]["unique_users"], "1")

        self.assertEqual(resp.data[2]["score"], "0")
        self.assertEqual(resp.data[2]["url"][-2], "3")
        self.assertEqual(resp.data[2]["unique_users"], "0")
