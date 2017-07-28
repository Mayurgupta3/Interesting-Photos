from django.db import models
import uuid


class User(models.Model):
	email = models.EmailField(default='')
	name = models.CharField(max_length=120, default='')
	username = models.CharField(max_length=120,default='')
	password = models.CharField(max_length=40, default='')
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)


class SessionToken(models.Model):

    user = models.ForeignKey(User)
    session_token = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)
    def create_token(self):
        self.session_token = uuid.uuid4()


class PostModel(models.Model):
  user = models.ForeignKey(User)
  image = models.FileField(upload_to='user_images')
  image_url = models.CharField(max_length=255)
  caption = models.CharField(max_length=240)
  category = models.CharField(max_length=200, default="others")
  created_on = models.DateTimeField(auto_now_add=True)
  updated_on = models.DateTimeField(auto_now=True)

  def like_count(self):
     return len(LikeModel.objects.filter(post=self))

  def comments(self):
      return CommentModel.objects.filter(post=self).order_by('created_on')


class LikeModel(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(PostModel)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class CommentModel(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(PostModel)
    comment_text = models.CharField(max_length=555)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    has_liked = False

class CommentLike(models.Model):
    comment = models.ForeignKey(CommentModel)
    user = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class Search(models.Model):
    category = models.CharField(max_length=30)