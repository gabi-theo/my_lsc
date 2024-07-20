"""
Unit tests for the DailySchoolSchedule view (mostly the GET endpoint since that needs testing)
"""

from json import dumps

from rest_framework.test import (
    APIClient,
    APITestCase,
)

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
)

from app.tests.dailyschoolschedule.utils import (
    erase_and_load_data,
    is_valid_response_format,
    make_up_dates,
    START_DATE,
    DEBUG,
)


class TestGET(APITestCase):

    def setUp(self):
        self.client = APIClient()

        if hasattr(self, "_testMethodName"):
            test_name = self._testMethodName

            valid_data, self.data = erase_and_load_data(
                f"/app/app/tests/dailyschoolschedule/inputs/get/{test_name}.json")
            self.assertTrue(valid_data)
            self.client.force_authenticate(self.data["admin"])

            print("")
            print(f" {self._testMethodName} ".upper().center(80, "#"))
        else:
            self.fail("No _testMethodName for fixture... HOW???!?")

    def tearDown(self) -> None:
        print("#" * 80)

    def get_and_validate_response(self, school_id):
        response = self.client.get(f"/api/school_schedules/{school_id}/")
        json: dict = response.json()

        if DEBUG:
            # Print repsonse json for better visualization
            print(dumps(json, indent=4))

        # Check that response code is OK
        self.assertContains(response=response, text="",
                            count=None, status_code=HTTP_200_OK)

        # Check that the response json has the expected format
        self.assertTrue(
            is_valid_response_format(response_json=json))

        return json

    # @unittest.skip("")
    def test_bad_school_id(self):
        response = self.client.get("/api/school_schedules/1/")

        # Check that response code is 404
        self.assertContains(response=response, text="",
                            count=None, status_code=HTTP_404_NOT_FOUND)

    # @unittest.skip("")
    def test_school_empty_schedule(self):
        for school in self.data["schools"]:
            json = self.get_and_validate_response(school.id)

            for course_type in ("onl", "sed"):

                for date in make_up_dates(START_DATE):

                    date_str = str(date.date())

                    if not json[course_type][date_str]:
                        continue

                    for trainer in self.data["trainers"]:

                        trainer_key: str = f'{trainer.id}-{trainer.first_name}-{trainer.last_name}'

                        try:
                            json[course_type][date_str][trainer_key]
                        except KeyError:
                            continue

                        self.assertEqual(
                            len(json[course_type][date_str][trainer_key]["free"]), 1)
                        self.assertEqual(
                            len(json[course_type][date_str][trainer_key]["busy"]), 0)

    # @unittest.skip("")
    def test_school_full_schedule(self):

        for school in self.data["schools"]:

            json = self.get_and_validate_response(school.id)

            for course_type in ("onl", "sed"):

                for date in make_up_dates(START_DATE):

                    date_str = str(date.date())

                    if not json[course_type][date_str]:
                        continue

                    for trainer in self.data["trainers"]:

                        trainer_key: str = f'{trainer.id}-{trainer.first_name}-{trainer.last_name}'

                        try:
                            json[course_type][date_str][trainer_key]
                        except KeyError:
                            continue

                        self.assertEqual(
                            len(json[course_type][date_str][trainer_key]["busy"]), 1)
                        self.assertEqual(
                            len(json[course_type][date_str][trainer_key]["free"]), 0)

    # @unittest.skip("")
    def test_30m_breaks(self):

        for school in self.data["schools"]:

            json = self.get_and_validate_response(school.id)

            for course_type in ("onl", "sed"):

                for date in make_up_dates(START_DATE):

                    date_str = str(date.date())

                    if not json[course_type][date_str]:
                        continue

                    for trainer in self.data["trainers"]:

                        trainer_key: str = f'{trainer.id}-{trainer.first_name}-{trainer.last_name}'

                        try:
                            json[course_type][date_str][trainer_key]
                        except KeyError:
                            continue

                        self.assertEqual(
                            len(json[course_type][date_str][trainer_key]["busy"]), 4)
                        self.assertEqual(
                            len(json[course_type][date_str][trainer_key]["free"]), 0)

    # @unittest.skip("")
    def test_45m_breaks(self):
        for school in self.data["schools"]:

            json = self.get_and_validate_response(school.id)

            for course_type in ("onl", "sed"):

                for date in make_up_dates(START_DATE):

                    date_str = str(date.date())

                    if not json[course_type][date_str]:
                        continue

                    for trainer in self.data["trainers"]:

                        trainer_key: str = f'{trainer.id}-{trainer.first_name}-{trainer.last_name}'

                        try:
                            json[course_type][date_str][trainer_key]
                        except KeyError:
                            continue

                        self.assertEqual(
                            len(json[course_type][date_str][trainer_key]["busy"]), 4)
                        self.assertEqual(
                            len(json[course_type][date_str][trainer_key]["free"]), 0)

    # @unittest.skip("")
    def test_60m_breaks(self):
        for school in self.data["schools"]:

            json = self.get_and_validate_response(school.id)

            for course_type in ("onl", "sed"):

                for date in make_up_dates(START_DATE):

                    date_str = str(date.date())

                    if not json[course_type][date_str]:
                        continue

                    for trainer in self.data["trainers"]:

                        trainer_key: str = f'{trainer.id}-{trainer.first_name}-{trainer.last_name}'

                        try:
                            json[course_type][date_str][trainer_key]
                        except KeyError:
                            continue

                        self.assertEqual(
                            len(json[course_type][date_str][trainer_key]["busy"]), 4)
                        self.assertEqual(
                            len(json[course_type][date_str][trainer_key]["free"]), 2)

    # @unittest.skip("")
    def test_90m_breaks(self):
        for school in self.data["schools"]:

            json = self.get_and_validate_response(school.id)

            for course_type in ("onl", "sed"):

                for date in make_up_dates(START_DATE):

                    date_str = str(date.date())

                    if not json[course_type][date_str]:
                        continue

                    for trainer in self.data["trainers"]:

                        trainer_key: str = f'{trainer.id}-{trainer.first_name}-{trainer.last_name}'

                        try:
                            json[course_type][date_str][trainer_key]
                        except KeyError:
                            continue

                        self.assertEqual(
                            len(json[course_type][date_str][trainer_key]["busy"]), 3)
                        self.assertEqual(
                            len(json[course_type][date_str][trainer_key]["free"]), 2)

    # @unittest.skip("")
    def test_multiple_days_full_schedule(self):
        for school in self.data["schools"]:

            json = self.get_and_validate_response(school.id)

            for course_type in ("onl", "sed"):

                for date in make_up_dates(START_DATE):

                    date_str = str(date.date())

                    if not json[course_type][date_str]:
                        continue

                    for trainer in self.data["trainers"]:

                        trainer_key: str = f'{trainer.id}-{trainer.first_name}-{trainer.last_name}'

                        try:
                            json[course_type][date_str][trainer_key]
                        except KeyError:
                            continue

                        self.assertEqual(
                            len(json[course_type][date_str][trainer_key]["busy"]), 1)
                        self.assertEqual(
                            len(json[course_type][date_str][trainer_key]["free"]), 0)

    def test_busy_room(self):
        for school in self.data["schools"]:

            json = self.get_and_validate_response(school.id)

            for course_type in ("onl", "sed"):

                for date in make_up_dates(START_DATE):

                    date_str = str(date.date())

                    if not json[course_type][date_str]:
                        continue

                    for trainer in self.data["trainers"]:

                        trainer_key: str = f'{trainer.id}-{trainer.first_name}-{trainer.last_name}'

                        try:
                            json[course_type][date_str][trainer_key]
                        except KeyError:
                            continue

                        self.assertTrue(
                            len(json[course_type][date_str][trainer_key]["busy"]) == 2 or len(json[course_type][date_str][trainer_key]["busy"]) == 3)
                        self.assertEqual(
                            len(json["sed"][date_str][trainer_key]["free"]), 0)


class TestPOST(APITestCase):

    def setUp(self) -> None:
        return super().setUp()