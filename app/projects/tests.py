import os
import shutil
import filecmp
import tempfile

from shutil import copyfile
from unittest import skip

from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from projects.models import Project


settings.PROJECTS_ROOT += '_test'


def testdata_path(path):
    basepath = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(basepath, 'testdata', path)


class ProjectTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        # Insert a user into the db
        self.test_user1 = get_user_model().objects.create_user(
            username='test_user1', password='abc123')
        self.test_user1.save()
        self.token = Token.objects.get_or_create(user=self.test_user1)[0]

        # Insert a public project into the db
        self.test_project1 = Project(
            name='test_project1',
            description='Test project 1',
            homepage='http://test_project1.com',
            private=False,
            owner=self.test_user1)
        self.test_project1.save()

        # Insert another public project into the db
        self.test_project2 = Project(
            name='test_project2',
            description='Test project 2',
            homepage='http://test_project2.com',
            private=False,
            owner=self.test_user1)
        self.test_project2.save()

        # Add 2 files to the project2
        filename1 = os.path.join(
            settings.PROJECTS_ROOT,
            'test_user1',
            'test_project2',
            'file.txt')

        filename2 = os.path.join(
            settings.PROJECTS_ROOT,
            'test_user1',
            'test_project2',
            'file2.txt')

        os.makedirs(os.path.dirname(filename1), exist_ok=True)

        copyfile(testdata_path('file.txt'), filename1)
        copyfile(testdata_path('file2.txt'), filename2)

        # Insert a private project into the db
        self.test_project3 = Project(
            name='test_project3',
            description='Test project 3',
            homepage='http://test_project3.com',
            private=True,
            owner=self.test_user1)
        self.test_project3.save()

    def tearDown(self):
        Project.objects.all().delete()
        get_user_model().objects.all().delete()
        # Remove credentials
        self.client.credentials()

        # Remove test's PROJECTS_ROOT
        shutil.rmtree(settings.PROJECTS_ROOT, ignore_errors=True)

    def test_project_content(self):
        project = Project.objects.get(id=1)
        self.assertEqual(project.name, 'test_project1')
        self.assertEqual(project.description, 'Test project 1')
        self.assertEqual(project.homepage, 'http://test_project1.com')
        self.assertFalse(project.private)
        self.assertEqual(str(project.owner), 'test_user1')

    def test_list_public_projects_api(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/v1/projects/')

        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 2)
        self.assertTrue(
            response.data[0]['name'] in ['test_project1', 'test_project2'])
        self.assertTrue(
            response.data[1]['name'] in ['test_project1', 'test_project2'])

    def test_list_user_projects_api(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/v1/projects/test_user1/')

        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 3)

    def test_create_user_project_api(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(
            '/api/v1/projects/test_user1/',
            {
                'name': 'api_created_project',
                'description': 'desc',
                'homepage': 'http://perdu.com',
                'private': True,
            }
        )

        self.assertTrue(status.is_success(response.status_code))

        project = Project.objects.get(name='api_created_project')
        # Will raise exception if donesn't exist

        self.assertEqual(str(project.owner), 'test_user1')

    def test_push_file_api(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        file_path = testdata_path('file.txt')
        # Push a file
        response = self.client.post(
            '/api/v1/projects/test_user1/test_project1/push/',
            {
                "file_content": open(file_path, 'rb')
            },
            format='multipart'
        )
        self.assertTrue(status.is_success(response.status_code))

        # Check if the file is actually stored in the correct position
        stored_file = os.path.join(
            settings.PROJECTS_ROOT,
            'test_user1',
            'test_project1',
            'file.txt')
        self.assertTrue(os.path.isfile(stored_file))

        # Check if file content is still the same
        self.assertTrue(filecmp.cmp(file_path, stored_file))

    def test_push_multiple_files_api(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        file_path = testdata_path('file.txt')
        file_path2 = testdata_path('file2.txt')

        # Push the files
        response = self.client.post(
            '/api/v1/projects/test_user1/test_project1/push/',
            {
                "file_content": [open(file_path, 'rb'), open(file_path2, 'rb')]
            },
            format='multipart'
        )
        self.assertTrue(status.is_success(response.status_code))

        # Check if the files are actually stored in the correct position
        stored_file = os.path.join(
            settings.PROJECTS_ROOT,
            'test_user1',
            'test_project1',
            'file.txt')
        self.assertTrue(os.path.isfile(stored_file))
        stored_file2 = os.path.join(
            settings.PROJECTS_ROOT,
            'test_user1',
            'test_project1',
            'file2.txt')
        self.assertTrue(os.path.isfile(stored_file2))

        # Check if files content is still the same
        self.assertTrue(filecmp.cmp(file_path, stored_file))
        self.assertTrue(filecmp.cmp(file_path2, stored_file2))

    def test_pull_file_api(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Pull the project
        response = self.client.get(
            '/api/v1/projects/test_user1/test_project2/file.txt/')
        self.assertTrue(status.is_success(response.status_code))

        temp_file = tempfile.NamedTemporaryFile()
        with open(temp_file.name, 'wb') as f:
            for _ in response.streaming_content:
                f.write(_)

        self.assertEqual(response.filename, 'file.txt')
        self.assertTrue(filecmp.cmp(temp_file.name, testdata_path('file.txt')))

    def test_get_files_list_api(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Pull the project
        response = self.client.get(
            '/api/v1/projects/test_user1/test_project2/files/')
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.json()[0]['name'], 'file.txt')
        self.assertEqual(response.json()[1]['name'], 'file2.txt')
        self.assertEqual(response.json()[0]['size'], 13)
        self.assertEqual(response.json()[1]['size'], 13)
        self.assertEqual(
            response.json()[0]['sha256'],
            '8663bab6d124806b9727f89bb4ab9db4cbcc3862f6bbf22024dfa7212aa4ab7d')
        self.assertEqual(
            response.json()[1]['sha256'],
            'fcc85fb502bd772aa675a0263b5fa665bccd5d8d93349d1dbc9f0f6394dd37b9')
