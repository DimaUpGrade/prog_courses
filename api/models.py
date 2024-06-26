from django.db import models

#
# Default Django User model (i.e. auth.models.User class)
# has atributes:
#
# username
# email
# first_name
# last_name
# date_joined
# last_login
#


class Author(models.Model):
    # Author's username in sourse of courses
    username = models.CharField(max_length=50)
    link = models.URLField(max_length=400)

    def __str__(self):
        return self.username


class Platform(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=15)
    description = models.CharField(max_length=600)
    
    def __str__(self):
        return self.title


class SearchWord(models.Model):
    title = models.CharField(max_length=25)
    weight = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(max_length=70)
    search_words = models.ManyToManyField("SearchWord", related_name="search_words")
    description = models.TextField()
    author = models.ForeignKey("Author", related_name='author_courses', on_delete=models.CASCADE)
    platform = models.ForeignKey("Platform", related_name="platform_courses", on_delete=models.CASCADE)
    publisher = models.ForeignKey("auth.User", related_name="user_published", on_delete=models.CASCADE)
    link = models.URLField(max_length=400)
    paid = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    price = models.IntegerField(default=0)
    tags = models.ManyToManyField("Tag", related_name="course_tags", blank=True)
    rating = models.FloatField(default=0)
    users = models.ManyToManyField("auth.User", related_name="course_users", blank=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    user = models.ForeignKey("auth.User", related_name="user_rewiews", on_delete=models.CASCADE)
    id_course = models.ForeignKey("Course", related_name="reviews", on_delete=models.CASCADE)
    rating = models.IntegerField()
    text_review = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField("auth.User", blank=True, related_name="review_likes")

    def __str__(self):
        return self.text_review


class Comment(models.Model):
    user = models.ForeignKey("auth.User", related_name="user_comments", on_delete=models.CASCADE)
    id_course = models.ForeignKey("Course", related_name="comments", on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    commentary_text = models.TextField()
    likes = models.ManyToManyField("auth.User", blank=True, related_name="comment_likes")

    def __str__(self):
        return self.commentary_text
    

class Report(models.Model):
    header = models.CharField(max_length=70)
    report_text = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.header


class NewsPost(models.Model):
    header = models.CharField(max_length=70)
    post_text = models.TextField()
    user = user = models.ForeignKey("auth.User", related_name="user_posts", on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.header
