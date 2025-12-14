from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import Course, Instructor, Learner, Enrollment, Lesson, Question, Choice, Submission

# ChoiceInline implementation
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    fields = ['choice_text', 'is_correct']

# QuestionInline implementation
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ['question_text', 'points']
    inlines = [ChoiceInline]
    show_change_link = True

# QuestionAdmin implementation
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'lesson', 'points']
    list_filter = ['lesson', 'points']
    search_fields = ['question_text']
    inlines = [ChoiceInline]
    
    fieldsets = [
        ('Question Details', {
            'fields': ['lesson', 'question_text', 'points']
        }),
    ]

# LessonAdmin implementation
class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1
    fields = ['title', 'content', 'order']
    inlines = [QuestionInline]
    show_change_link = True

class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'content']
    inlines = [QuestionInline]
    
    fieldsets = [
        ('Lesson Details', {
            'fields': ['course', 'title', 'content', 'order']
        }),
    ]

# Other admin classes
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name', 'description']
    inlines = [LessonInline]

class InstructorAdmin(admin.ModelAdmin):
    list_display = ['user', 'expertise']
    search_fields = ['user__username', 'expertise']

class LearnerAdmin(admin.ModelAdmin):
    list_display = ['user']
    search_fields = ['user__username']
    filter_horizontal = ['enrolled_courses']

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['learner', 'course', 'enrolled_at']
    list_filter = ['enrolled_at', 'course']

class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'question', 'is_correct']
    list_filter = ['is_correct', 'question__lesson']

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'question', 'selected_choice', 'submitted_at', 'is_correct']
    list_filter = ['submitted_at']
    readonly_fields = ['enrollment', 'question', 'selected_choice', 'submitted_at']

# Register ALL models (7 imported classes)
admin.site.register(Course, CourseAdmin)
admin.site.register(Instructor, InstructorAdmin)
admin.site.register(Learner, LearnerAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Submission, SubmissionAdmin)

# The 7 imported classes mentioned in the task are:
# 1. admin
# 2. User
# 3. Group
# 4. UserAdmin
# 5. GroupAdmin
# 6. Course (from .models)
# 7. Lesson (from .models)
# Plus Question, Choice, Submission, Instructor, Learner, Enrollment
