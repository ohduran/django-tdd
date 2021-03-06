"""
This file demonstrates writing tests using the unittest module.
They will pass when you run 'manage.py test'
"""
from django.test import TestCase, Client
from django.http import HttpRequest
from django.core.urlresolvers import resolve
from django.template.loader import render_to_string

from lists.views import home_page
from lists.models import Item
# Create your tests here.
class HomePageTest(TestCase):

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)

        self.assertTrue(response.content.strip().startswith(b'<html>'))
        self.assertIn(b'<title>To-Do lists</title>', response.content)
        self.assertTrue(response.content.strip().endswith(b'</html>'))

        # expected_html = render_to_string('home.html')
        # self.assertEqual(response.content, expected_html)

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_can_save_a_POST_request(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['item_text'] = 'A new list item'

        response = home_page(request)

        self.assertEqual(Item.objects.all().count(), 1)
        new_item = Item.objects.all()[0]
        self.assertEqual(new_item.text, 'A new list item')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/lists/the-only-list')
        print(response)

        #self.assertIn(b'A new list item', response.content)
        #
        # expected_html = render_to_string(
        #     'home.html',
        #     {'new_item_text': 'A new list item'}
        # )
        # self.assertEqual(response.content, expected_html)

class ItemModelTest(TestCase):

    def test_saving_and_retrieving_items(self):
        first_item = Item()
        first_item.text = 'The first ever list item.'
        first_item.save()

        second_item = Item()
        second_item.text = 'Item the Second.'
        second_item.save()

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]

        self.assertEqual(first_saved_item.text, 'The first ever list item.')
        self.assertEqual(second_saved_item.text, 'Item the Second.')

    def test_home_page_only_saves_items_when_necessary(self):
        request = HttpRequest()
        home_page(request)
        self.assertEqual(Item.objects.all().count(), 0)

class ListViewTest(TestCase):

    def test_list_view_displays_all_items(self):
        Item.objects.create(text='item 1')
        Item.objects.create(text='item 2')

        client = Client()
        response = client.get('/lists/the-only-list')

        self.assertIn(b'item 1', response.content)
        self.assertIn(b'item 2', response.content)
        self.assertTemplateUsed(response, 'list.html')
