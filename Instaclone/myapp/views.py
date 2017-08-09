
from __future__ import unicode_literals
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm, commentlikeform, searchform
from models import User ,SessionToken,PostModel,LikeModel, CommentModel, CommentLike, SearchModel
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from Instaclone.settings import BASE_DIR
from imgurpython import ImgurClient
from clarifai import rest
from clarifai.rest import ClarifaiApp



# Create your views here.

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User(email=email, name=name, username=username, password=make_password(password))
            user.save()
            return render(request, 'success.html')
    elif request.method == 'GET':
        form = SignUpForm()

    return render(request, 'index.html', {'form' : form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = User.objects.filter(username= username).first()

            if user:
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('/post/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    print 'User is invalid'
    elif request.method == "GET":
        form = LoginForm()


    return render(request, 'login.html', {'form': form})


def feed_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('created_on')
        return render(request, 'feed.html', {'posts': posts})
    else:
        return redirect('/login/')


def post_view(request):
  user = check_validation(request)

  if user:

      if request.method == 'POST':
          form = PostForm(request.POST, request.FILES)
          if form.is_valid():
              image = form.cleaned_data.get('image')
              caption = form.cleaned_data.get('caption')

              post = PostModel(user=user, image=image, caption=caption)
              post.save()

              client = ImgurClient('0c6d3f3ca84e472', 'cd7fc1fabc96a5ade35cdcebcb6b77c3a6f21670')
              path = str(BASE_DIR + '//' + post.image.url)
              post.image_url = client.upload_from_path(path, anon=True)['link']
              print(post.image_url)
              post.save()
              app = ClarifaiApp(api_key='c68ba2b17ce44ecdb42d94117d48a4ca')
              model = app.models.get('general-v1.3')
              response = model.predict_by_url(url=post.image_url)

              arr = response['outputs'][0]['data']['concepts']
              print arr
              for i in range(0, 10):
                  category = arr[i]['name']
                  print category
                  if category == 'nature':
                      post.category_post = category

                      break
                  elif category == 'technology':
                      post.category_post = category

                      break
                  elif category == 'food':
                      post.category_post = category
                      break
                  elif category == 'sports':
                      post.category_post = category

                      break
                  elif category == 'vehicle':
                      post.category_post = category

              post.save()

              return redirect('/feed/')
      else:
          form = PostForm()
      return render(request, 'post.html', {'form': form})
  else:
      return redirect('/login/')


def like_view(request):

    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            print existing_like

            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
            else:
                existing_like.delete()

            return redirect('/feed/')

    else:
        return redirect('/login/')


def comment_view(request):
  user = check_validation(request)
  if user and request.method == 'POST':
    form = CommentForm(request.POST)
    if form.is_valid():
      post_id = form.cleaned_data.get('post').id
      comment_text = form.cleaned_data.get('comment_text')
      comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
      comment.save()
      return redirect('/feed/')
    else:
      return redirect('/feed/')
  else:
    return redirect('/login')


def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            return session.user
    else:
        return None


def logout_view(request):
    user = check_validation(request)
    if user is not None:
        latest_session = SessionToken.objects.filter(user=user).last()
        if latest_session:
            latest_session.delete()

    return redirect("/login/")


def commentlike_view(request):

    user = check_validation(request)
    if user and request.method == 'POST':
        form = commentlikeform(request.POST)
        if form.is_valid():
            comment_id = form.cleaned_data.get('comment').id

            existing_like = CommentLike.objects.filter(comment_id=comment_id, user=user).first()

            if not existing_like:
                CommentLike.objects.create(comment_id=comment_id, user=user)
            else:
                existing_like.delete()

            return redirect('/feed/')

    else:
        return redirect('/login/')


def search_view(request):
    if request.method == "POST":
        print 'POST'
        form = searchform(request.POST)
        print form
        if form.is_valid():
            print 'valid'
            search = form.cleaned_data.get('category')
            print search
            search1 = SearchModel(category=search)
            print search1.category
            search1.save()
            posts = PostModel.objects.filter(category_post = search1.category)
            print posts
            if posts:
                return render(request, 'category.html', {'posts': posts})
            else:
                return redirect('/login/')

        else:
            print 'INVALID'
            return render(request,'search.html',{'form':form})
    elif request.method == "GET":
        form = searchform()
        return render(request,'search.html',{'form': form})


def category_view(request):
    return render(request,'category.html')