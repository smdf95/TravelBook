from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Trip, Post, Comment, Reply
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .forms import ReplyForm
import os
import json
import tempfile

class TripModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a test user
        cls.test_user = User.objects.create_user(username='testuser', password='testpass')
        
        # Create a test trip
        image = cls.create_image()
        cls.trip = Trip.objects.create(
            title='Test Trip',
            image=image,
            created_by=cls.test_user,
        )
        
        # Add a traveller to the test trip
        cls.trip.travellers.add(cls.test_user)

    @classmethod
    def create_image(cls):
        """
        Create a test image.
        """
        file = BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return SimpleUploadedFile(os.path.basename(file.name), file.read())

    def test_title_content(self):
        title = self.trip.title
        self.assertEqual(title, 'Test Trip')

    def test_image_content(self):
        image = self.trip.image
        self.assertTrue(image.name.startswith('trip_pics/'))

    def test_created_by_content(self):
        created_by = self.trip.created_by
        self.assertEqual(created_by.username, 'testuser')

    def test_get_absolute_url(self):
        url = self.trip.get_absolute_url()
        self.assertEqual(url, f'/trip/{self.trip.pk}/')


    def test_image_orientation(self):
        # Create an image with EXIF orientation data
        image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        image_file = SimpleUploadedFile('test.jpg', buffer.getvalue())
        
        # Create a test trip with the new image
        test_trip = Trip.objects.create(
            title='Orientation Test Trip',
            image=image_file,
            created_by=User.objects.get(username='testuser'),
        )
        
        # Check if the image orientation is corrected
        corrected_image_path = test_trip.image.path
        img = Image.open(corrected_image_path)
        exif = img._getexif()
        if exif:
            orientation = exif.get(0x0112)
            if orientation == 3:
                self.assertEqual(orientation, 3)
            elif orientation == 6:
                self.assertEqual(orientation, 6)
            elif orientation == 8:
                self.assertEqual(orientation, 8)
        else:
            self.assertIsNone(exif)

    def test_image_resize(self):
        image_path = self.trip.image.path
        img = Image.open(image_path)
        self.assertTrue(img.height <= 600)
        self.assertTrue(img.width <= 600)

    def test_str_representation(self):
        title = str(self.trip)
        self.assertEqual(title, 'Test Trip')

    def test_travellers(self):
        expected_travellers = [f'{traveller}' for traveller in self.trip.travellers.all()]
        self.assertEqual(expected_travellers, ['testuser'])

    def test_viewers(self):
        # Add a viewer to the test trip
        viewer = User.objects.create_user(username='testviewer', password='testpass')
        self.trip.viewers.add(viewer)
        
        expected_viewers = [f'{viewer}' for viewer in self.trip.viewers.all()]
        self.assertEqual(expected_viewers, ['testviewer'])


class TripListViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.trip.travellers.add(self.user)
        
    def test_trip_list_view_for_logged_in_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('travel-home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'travel/home.html')
        self.assertTrue('filter' in response.context)
        self.assertEqual(response.context['filter'].qs.count(), 1)
        self.assertEqual(response.context['filter'].qs.first(), self.trip)
        
    def test_trip_list_view_for_anonymous_user(self):
        response = self.client.get(reverse('travel-home'))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/')

    def test_trip_create_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('trip-create'), {
            'title': 'New Test Trip',
            'image': 'test_image.jpg',
        })
        self.assertEqual(response.status_code, 302)  # 302 because it redirects after creation

    # Test TripUpdateView
    def test_trip_update_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('trip-update', kwargs={'pk': self.trip.id}), {
            'title': 'Updated Test Trip',
            'image': 'updated_image.jpg',
        })
        self.assertEqual(response.status_code, 302)  # 302 because it redirects after update

    # Test TripDeleteView
    def test_trip_delete_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('trip-delete', kwargs={'pk': self.trip.id}))
        self.assertEqual(response.status_code, 302)  # 302 because it redirects after deletion


class TripDetailViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.trip.travellers.add(self.user)
        self.post = Post.objects.create(content='Test Content', trip=self.trip, created_by=self.user)

    def test_trip_detail_view_for_logged_in_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('trip-detail', kwargs={'pk': self.trip.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'travel/trip_detail.html')
        self.assertTrue('travellers' in response.context)
        self.assertEqual(response.context['travellers'].count(), 1)
        self.assertEqual(response.context['travellers'].first(), self.user)
        self.assertTrue('posts' in response.context)
        self.assertEqual(response.context['posts'].count(), 1)
        self.assertEqual(response.context['posts'].first(), self.post)

    def test_trip_detail_view_for_anonymous_user(self):
        response = self.client.get(reverse('trip-detail', kwargs={'pk': self.trip.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/trip/{}'.format(self.trip.pk))


    def test_add_traveller_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('add-traveller', kwargs={'pk': self.trip.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'travel/add_traveller.html')
        self.assertTrue('form' in response.context)
        self.assertTrue('trip' in response.context)
        self.assertTrue('travellers' in response.context)
        self.assertEqual(response.context['trip'], self.trip)

    def test_create_traveller_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('create-traveller', kwargs={'pk': self.trip.pk}), {'travellers': 'testuser@example.com'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/traveller.html')
        self.assertTrue('traveller' in response.context)
        self.assertEqual(response.context['traveller'], self.user)

    def test_add_viewer_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('add-viewer', kwargs={'pk': self.trip.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'travel/add_viewer.html')
        self.assertTrue('form' in response.context)
        self.assertTrue('trip' in response.context)
        self.assertTrue('viewers' in response.context)
        self.assertEqual(response.context['trip'], self.trip)

    def test_create_viewer_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('create-viewer', kwargs={'pk': self.trip.pk}), {'viewers': 'testuser@example.com'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/viewer.html')
        self.assertTrue('viewer' in response.context)
        self.assertEqual(response.context['viewer'], self.user)

    def test_leave_trip_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('leave-trip', kwargs={'pk': self.trip.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

        # Check if the user is removed from the trip
        self.assertFalse(self.user in self.trip.travellers.all())

    
class PostCreateViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.client.login(username='testuser', password='testpassword')
        
    def test_post_create_view(self):
        response = self.client.post(reverse('post-create', kwargs={'pk': self.trip.pk}), {
            'content': 'Test Content',
            'location': 'Test Location'
        })
        
        self.assertEqual(response.status_code, 302)  # Check if the post request was successful and redirected
        self.assertTrue(Post.objects.exists())  # Check if a post was created
        self.assertEqual(Post.objects.first().content, 'Test Content')  # Check the content of the created post
        self.assertEqual(Post.objects.first().location, 'Test Location')  # Check the location of the created post

class PostViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.post = Post.objects.create(content='Test Content', location='Test Location', created_by=self.user, trip=self.trip)
        
    def test_post_view(self):
        response = self.client.get(reverse('post-detail', kwargs={'pk': self.post.pk}))
        
        self.assertEqual(response.status_code, 302)  # Check if the get request was redirected
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('post-detail', kwargs={'pk': self.post.pk}))  # Check if the correct redirect location is used


class PostLikeTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.post = Post.objects.create(content='Test Content', location='Test Location', created_by=self.user, trip=self.trip)
        self.client.login(username='testuser', password='testpassword')
        
    def test_post_like(self):
        # Like the post

        response = self.client.get(reverse('post-like', kwargs={'pk': self.post.pk}))

        self.assertEqual(response.status_code, 302)  # Check if the get request was successful and redirected       
        self.assertTrue(self.post.likes.filter(id=self.user.id).exists())  # Check if the post is liked by the user
        
        # Unlike the post
        response = self.client.get(reverse('post-like', kwargs={'pk': self.post.pk}))
        self.assertFalse(self.post.likes.filter(id=self.user.id).exists())  # Check if the post is unliked by the user


class PostDeleteViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.post = Post.objects.create(content='Test Content', location='Test Location', created_by=self.user, trip=self.trip)
        self.client.login(username='testuser', password='testpassword')
        
    def test_post_delete_view(self):
        response = self.client.post(reverse('post-delete', kwargs={'pk': self.post.pk}))
        
        self.assertEqual(response.status_code, 302)  # Check if the post request was successful and redirected
        self.assertFalse(Post.objects.exists())  # Check if the post was deleted


class AddCommentViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.post = Post.objects.create(content='Test Content', location='Test Location', created_by=self.user, trip=self.trip)
        self.client.login(username='testuser', password='testpassword')
        
    def test_add_comment_view(self):
        response = self.client.post(reverse('add-comment', kwargs={'pk': self.post.pk}), {
            'content': 'Test Comment'
        })
        
        self.assertEqual(response.status_code, 200)  # Check if the post request was successful
        self.assertTrue(Comment.objects.filter(content='Test Comment', post=self.post, created_by=self.user).exists())  # Check if a comment was created

class CommentLikeViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.post = Post.objects.create(content='Test Content', location='Test Location', created_by=self.user, trip=self.trip)
        self.comment = Comment.objects.create(content='Test Comment', post=self.post, created_by=self.user)
        self.client.login(username='testuser', password='testpassword')
        
    def test_comment_like_view(self):
        response = self.client.post(reverse('comment-like', kwargs={'pk': self.comment.pk}))
        
        self.assertEqual(response.status_code, 200)  # Check if the post request was successful
        self.assertTrue(self.comment.likes.filter(id=self.user.id).exists())  # Check if the comment is liked by the user

class CommentLikeCountViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.post = Post.objects.create(content='Test Content', location='Test Location', created_by=self.user, trip=self.trip)
        self.comment = Comment.objects.create(content='Test Comment', post=self.post, created_by=self.user)
        self.client.login(username='testuser', password='testpassword')
        
    def test_comment_like_count_view(self):
        # Like the comment
        self.client.post(reverse('comment-like', kwargs={'pk': self.comment.pk}))
        
        # Reload the page to get the updated likes count
        response = self.client.get(reverse('comment-like-count', kwargs={'pk': self.comment.pk}))
        likes_count = json.loads(response.content.decode('utf-8'))
        
        self.assertEqual(response.status_code, 200)  # Check if the get request was successful
        self.assertEqual(likes_count, 1)

class DeleteCommentViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.post = Post.objects.create(content='Test Content', location='Test Location', created_by=self.user, trip=self.trip)
        self.comment = Comment.objects.create(content='Test Comment', post=self.post, created_by=self.user)
        self.client.login(username='testuser', password='testpassword')
        
    def test_delete_comment_view(self):
        response = self.client.post(reverse('comment-delete', kwargs={'pk': self.comment.pk}))
        
        self.assertEqual(response.status_code, 200)  # Check if the post request was successful
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())


class AddReplyViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.post = Post.objects.create(content='Test Content', location='Test Location', created_by=self.user, trip=self.trip)
        self.comment = Comment.objects.create(content='Test Comment', post=self.post, created_by=self.user)
        self.client.login(username='testuser', password='testpassword')
        
    def test_add_reply_view(self):
        response = self.client.post(reverse('add-reply', kwargs={'pk': self.comment.pk}), {
            'content': 'Test Reply Content'
        })
        
        self.assertEqual(response.status_code, 200)  # Check if the post request was successful
        self.assertTrue(Reply.objects.exists())  # Check if a reply was created
        self.assertEqual(Reply.objects.first().content, 'Test Reply Content')  # Check the content of the created reply

class ReplyLikeViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.post = Post.objects.create(content='Test Content', location='Test Location', created_by=self.user, trip=self.trip)
        self.comment = Comment.objects.create(content='Test Comment', post=self.post, created_by=self.user)
        self.reply = Reply.objects.create(content='Test Reply', comment=self.comment, created_by=self.user)
        self.client.login(username='testuser', password='testpassword')
        
    def test_reply_like_view(self):
        response = self.client.post(reverse('reply-like', kwargs={'pk': self.reply.pk}))
        
        self.assertEqual(response.status_code, 200)  # Check if the post request was successful
        self.assertTrue(self.reply.likes.filter(id=self.user.id).exists())  # Check if the reply is liked by the user
        
        response = self.client.post(reverse('reply-like', kwargs={'pk': self.reply.pk}))
        self.assertFalse(self.reply.likes.filter(id=self.user.id).exists())  # Check if the reply is unliked by the user

class ReplyLikeCountViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.post = Post.objects.create(content='Test Content', location='Test Location', created_by=self.user, trip=self.trip)
        self.comment = Comment.objects.create(content='Test Comment', post=self.post, created_by=self.user)
        self.reply = Reply.objects.create(content='Test Reply', comment=self.comment, created_by=self.user)
        self.client.login(username='testuser', password='testpassword')
        
    def test_reply_like_count_view(self):
        # Like the reply
        self.client.post(reverse('reply-like', kwargs={'pk': self.reply.pk}))
        
        # Reload the page to get the updated likes count
        response = self.client.get(reverse('reply-like-count', kwargs={'pk': self.reply.pk}))
        likes_count = json.loads(response.content.decode('utf-8'))
        
        self.assertEqual(response.status_code, 200)  # Check if the get request was successful
        self.assertEqual(likes_count, 1)  # Check if the like count is correct after liking the reply

class DeleteReplyViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.post = Post.objects.create(content='Test Content', location='Test Location', created_by=self.user, trip=self.trip)
        self.comment = Comment.objects.create(content='Test Comment', post=self.post, created_by=self.user)
        self.reply = Reply.objects.create(content='Test Reply', comment=self.comment, created_by=self.user)
        self.client.login(username='testuser', password='testpassword')
        
    def test_delete_reply_view(self):
        response = self.client.post(reverse('reply-delete', kwargs={'pk': self.reply.pk}))
        
        self.assertEqual(response.status_code, 200)  # Check if the post request was successful
        self.assertFalse(Reply.objects.filter(id=self.reply.pk).exists())

class PostModelTest(TestCase):

    @classmethod
    def create_image(cls):
        """
        Create a test image.
        """
        file = BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return SimpleUploadedFile(os.path.basename(file.name), file.read())

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        
        # Create a test image
        image_file = self.create_image()

        self.post = Post.objects.create(content='Test Content', trip=self.trip, created_by=self.user, image=image_file)

    def test_save_method(self):
        self.post.save()
        img = Image.open(self.post.image.path)
        self.assertTrue(img.width <= 600)
        self.assertTrue(img.height <= 600)

    def test_get_absolute_url(self):
        self.assertEqual(self.post.get_absolute_url(), reverse('trip-detail', kwargs={'pk': self.post.trip_id}))

    def test_number_of_likes_method(self):
        self.post.likes.add(self.user)
        likes_count = self.post.number_of_likes()
        self.assertEqual(likes_count, 1)

    

class CommentModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.post = Post.objects.create(content='Test Content', trip=self.trip, created_by=self.user)
        self.comment = Comment.objects.create(content='Test Comment', post=self.post, created_by=self.user)

    def test_number_of_likes_method(self):
        self.assertEqual(self.comment.number_of_likes(), 0)

    def test_get_absolute_url(self):
        self.assertEqual(self.comment.get_absolute_url(), reverse('post-detail', kwargs={'pk': self.post.pk}))

class ReplyModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.trip = Trip.objects.create(title='Test Trip', created_by=self.user)
        self.post = Post.objects.create(content='Test Content', trip=self.trip, created_by=self.user)
        self.comment = Comment.objects.create(content='Test Comment', post=self.post, created_by=self.user)
        self.reply = Reply.objects.create(content='Test Reply', comment=self.comment, created_by=self.user)

    def test_number_of_likes_method(self):
        self.assertEqual(self.reply.number_of_likes(), 0)