from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor')
    bio = models.TextField()
    expertise = models.CharField(max_length=200)
    
    def __str__(self):
        return self.user.username

class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learner')
    enrolled_courses = models.ManyToManyField(Course, through='Enrollment')
    
    def __str__(self):
        return self.user.username

class Enrollment(models.Model):
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['learner', 'course']
    
    def __str__(self):
        return f"{self.learner.user.username} - {self.course.name}"

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.course.name} - {self.title}"
    
    class Meta:
        ordering = ['order']

class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    points = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.lesson.title}: {self.question_text[:50]}..."

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.question.question_text[:30]}: {self.choice_text}"

class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='submissions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def is_correct(self):
        return self.selected_choice.is_correct
    
    def __str__(self):
        return f"{self.enrollment.learner.user.username} - {self.question.question_text[:30]}"
    
    class Meta:
        ordering = ['-submitted_at']
