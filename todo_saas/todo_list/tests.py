from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import TodoList

User = get_user_model()

class TodoListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@example.com', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.todo_list = TodoList.objects.create(title='Test Todo', user=self.user)
        
    def tearDown(self) -> None:
        return super().tearDown() 
    
    def test_get_todolist_by_id(self):
        response = self.client.get(f'/api/todo-lists/{self.todo_list.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Test Todo')

    def test_get_first_todolist(self):
        response = self.client.get('/api/todo-lists/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)
        self.assertEqual(response.data['title'], 'Test Todo')

    def test_get_todolist_not_found(self):
        response = self.client.get('/api/todo-lists/9999/')
        self.assertEqual(response.status_code, 404)


    def test_create_todolist_should_not_be_created(self):
        response = self.client.post('/api/todo-lists/', {'title': 'Another Todo'})
        self.assertEqual(response.status_code, 400)

    def test_create_todolist(self):
        TodoList.objects.filter().delete()
        response = self.client.post('/api/todo-lists/', {'title': 'Another Todo'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get("title"),'Another Todo')

    def test_update_todolist(self):
        response = self.client.patch(f'/api/todo-lists/{self.todo_list.id}/', {'title': 'Updated Todo'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Updated Todo')

    def test_update_todolist_not_found(self):
        response = self.client.patch('/api/todo-lists/9999/', {'title': 'Nonexistent Todo'})
        self.assertEqual(response.status_code, 404)

    def test_delete_todolist(self):
        response = self.client.delete(f'/api/todo-lists/{self.todo_list.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(TodoList.objects.filter(id=self.todo_list.id).exists())

    def test_delete_todolist_not_found(self):
        response = self.client.delete('/api/todo-lists/9999/')
        self.assertEqual(response.status_code, 404)
