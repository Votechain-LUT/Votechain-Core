from datetime import timedelta
from rest_framework.test import APITestCase, APIRequestFactory, URLPatternsTestCase, \
    force_authenticate
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import include, path, reverse
from votechain import settings
from core.models.models import Poll
from core.views.admin_poll_view import AdminListOrCreatePoll


def datetime_to_string(datetime):
    """ Converts datetime to string using format specified in project settings """
    return datetime.strftime(settings.REST_FRAMEWORK["DATETIME_FORMAT"])


class PollTests(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('/', include('core.urls')),
    ]
    fixtures = [ "test_data.json" ]

    def setUp(self):
        self.user_model = get_user_model()
        self.admin_user = self.user_model.objects.get(username="admin")

    def test_poll_list(self):
        """ Tests listing empty poll """
        factory = APIRequestFactory()
        request = factory.get(
            reverse("admin_list_poll")
        )
        force_authenticate(request, user=self.admin_user)
        response = AdminListOrCreatePoll.as_view()(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_poll_list_unauthorized(self):
        """ Tests listing empty poll """
        factory = APIRequestFactory()
        request = factory.get(
            reverse("admin_list_poll")
        )
        response = AdminListOrCreatePoll.as_view()(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsNotNone(response.data.get("detail", None))

    def test_poll_create(self):
        """ Testing adding a correct poll """
        count = Poll.objects.count()
        datenow = timezone.now()
        title = "title1"
        start = "{0}".format(datetime_to_string(datenow + timedelta(hours=1)))
        end = "{0}".format(datetime_to_string(datenow + timedelta(hours=3)))
        input_data = {
            "title": title,
            "start": start,
            "end": end,
            "isActive": "true"
        }
        factory = APIRequestFactory()
        request = factory.post(
            reverse("admin_list_poll"),
            input_data,
            format="json"
        )
        force_authenticate(request, user=self.admin_user)
        response = AdminListOrCreatePoll.as_view()(request)
        response.render()
        self.assertEqual(Poll.objects.count(), count + 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["start"], start)
        self.assertEqual(response.data["end"], end)
        self.assertEqual(response.data["title"], title)
        self.assertEqual(response.data["isActive"], True)

    def test_poll_create_unathorized(self):
        """ Testing adding a correct poll """
        count = Poll.objects.count()
        datenow = timezone.now()
        title = "title1"
        start = "{0}".format(datetime_to_string(datenow + timedelta(hours=1)))
        end = "{0}".format(datetime_to_string(datenow + timedelta(hours=3)))
        input_data = {
            "title": title,
            "start": start,
            "end": end,
            "isActive": "true"
        }
        factory = APIRequestFactory()
        request = factory.post(
            reverse("admin_list_poll"),
            input_data,
            format="json"
        )
        response = AdminListOrCreatePoll.as_view()(request)
        response.render()
        self.assertEqual(Poll.objects.count(), count)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsNotNone(response.data.get("detail", None))

    def test_poll_create_incorrect_dates(self):
        """ Testing adding an incorrect poll """
        count = Poll.objects.count()
        datenow = timezone.now()
        title = "title1"
        start = "{0}".format(datetime_to_string(datenow + timedelta(hours=3)))
        end = "{0}".format(datetime_to_string(datenow + timedelta(hours=1)))
        input_data = {
            "title": title,
            "start": start,
            "end": end,
            "isActive": "true"
        }
        factory = APIRequestFactory()
        request = factory.post(
            reverse("admin_list_poll"),
            input_data,
            format="json"
        )
        force_authenticate(request, user=self.admin_user)
        response = AdminListOrCreatePoll.as_view()(request)
        response.render()
        self.assertEqual(Poll.objects.count(), count)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
