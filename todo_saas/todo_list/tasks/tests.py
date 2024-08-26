from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.authtoken.models import Token
from .models import Task, File
from todo_list.models import TodoList
from Users.models import User
import tempfile
import os
from django.core.files.uploadedfile import SimpleUploadedFile

class TaskAPITestCase(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(email='testuser@example.com', password='password')
        self.token = Token.objects.create(user=self.user)  # Create token for the user
    
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)  # Set the token in the request headers
    
        # Create a TodoList for the user
        self.todo_list = TodoList.objects.create(user=self.user, title='Test TodoList')

        # Create tasks with similar descriptions
        self.task1 = Task.objects.create(
            todo_list=self.todo_list,
            title='Task 1',
            description='This is task 1',
            due_date='2024-12-31T23:59:59Z'
        )
        self.task2 = Task.objects.create(
            todo_list=self.todo_list,
            title='Task 2',
            description='This is task 1, similar to task 1',
            due_date='2024-12-31T23:59:59Z'
        )
    
        self.file = SimpleUploadedFile("test_file.txt", b"file content", content_type="text/plain")

    def tearDown(self):
        self.client.logout()

    def test_create_task(self):
        url = reverse('task-list')  
        data = {
            'title': 'New Task',
            'description': 'Description of new task',
            'due_date': '2024-12-31T23:59:59Z'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 3)
        self.assertEqual(Task.objects.latest('id').title, 'New Task')

    def test_retrieve_task(self):
        url = reverse('task-detail', args=[self.task1.id])  # Matches with the URL configuration
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Task 1')

    def test_update_task(self):
        url = reverse('task-detail', args=[self.task1.id])  # Matches with the URL configuration
        data = {'title': 'Updated Task 1'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Updated Task 1')

    def test_delete_task(self):
        url = reverse('task-detail', args=[self.task1.id])  # Matches with the URL configuration
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 1)

    def test_upload_file(self):
        url = reverse('file-upload', args=[self.task1.id])
    
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b'Test file content')
            tmp_file.seek(0)
            file = SimpleUploadedFile(tmp_file.name.split('/')[-1], tmp_file.read(), content_type="text/plain")

        os.remove(tmp_file.name)

        response = self.client.post(url, {'file_path': file}, format='multipart')
    
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(File.objects.count(), 1)
    
        # Check the actual file path in the database
        stored_file_path = File.objects.first().file_path.name
        self.assertEqual(stored_file_path, file.name)

    def test_retrieve_files_for_task(self):
        File.objects.create(task=self.task1, file_path=self.file)
        url = reverse('file-list', args=[self.task1.id]) 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
