from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from course_app.models import Course, Lesson, Question, Choice, Submission
from django.contrib.auth.models import User

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'course_app/course_details_bootstrap.html', {'course': course})

@login_required
def start_exam(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    questions = lesson.questions.all()
    
    if not questions:
        messages.warning(request, "No questions available for this lesson.")
        return redirect('course_detail', course_id=lesson.course.id)
    
    return render(request, 'course_app/exam.html', {
        'lesson': lesson,
        'questions': questions,
    })

@login_required
def submit(request, lesson_id):
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)
        user = request.user
        total_score = 0
        max_score = 0
        submissions = []
        
        # Get all questions for this lesson
        questions = lesson.questions.all()
        
        for question in questions:
            max_score += question.points
            
            # Get selected choice ID from form
            choice_id = request.POST.get(f'question_{question.id}')
            
            if choice_id:
                try:
                    selected_choice = Choice.objects.get(id=choice_id, question=question)
                    
                    # Create submission
                    submission = Submission.objects.create(
                        user=user,
                        question=question,
                        selected_choice=selected_choice
                    )
                    submissions.append(submission)
                    
                    # Add to score if correct
                    if selected_choice.is_correct:
                        total_score += question.points
                except Choice.DoesNotExist:
                    # If choice doesn't exist or doesn't belong to question, skip
                    continue
        
        # Calculate percentage
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        # Store results in session
        request.session['exam_results'] = {
            'lesson_id': lesson_id,
            'total_score': total_score,
            'max_score': max_score,
            'percentage': percentage,
            'submission_count': len(submissions),
        }
        
        # Redirect to results page
        return redirect('show_exam_result', lesson_id=lesson_id)
    
    return redirect('start_exam', lesson_id=lesson_id)

@login_required
def show_exam_result(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    user = request.user
    
    # Get results from session or calculate
    exam_results = request.session.get('exam_results', {})
    
    # If no session data, calculate from database
    if not exam_results or exam_results.get('lesson_id') != lesson_id:
        # Get user's submissions for this lesson
        user_submissions = Submission.objects.filter(
            user=user,
            question__lesson=lesson
        ).order_by('-submitted_at')
        
        if not user_submissions:
            messages.info(request, "You haven't taken this exam yet.")
            return redirect('start_exam', lesson_id=lesson_id)
        
        # Calculate scores from latest submissions
        latest_submissions = {}
        for submission in user_submissions:
            if submission.question_id not in latest_submissions:
                latest_submissions[submission.question_id] = submission
        
        total_score = 0
        max_score = 0
        
        for question in lesson.questions.all():
            max_score += question.points
            if question.id in latest_submissions:
                if latest_submissions[question.id].selected_choice.is_correct:
                    total_score += question.points
        
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        exam_results = {
            'lesson_id': lesson_id,
            'total_score': total_score,
            'max_score': max_score,
            'percentage': percentage,
            'submission_count': len(latest_submissions),
        }
    
    # Get detailed results for display
    detailed_results = []
    questions = lesson.questions.all()
    
    for question in questions:
        # Get user's latest submission for this question
        latest_submission = Submission.objects.filter(
            user=user,
            question=question
        ).order_by('-submitted_at').first()
        
        detailed_results.append({
            'question': question,
            'user_answer': latest_submission.selected_choice if latest_submission else None,
            'is_correct': latest_submission.selected_choice.is_correct if latest_submission else False,
            'points': question.points,
        })
    
    # Determine if user passed (70% or higher)
    passed = exam_results['percentage'] >= 70
    
    context = {
        'lesson': lesson,
        'total_score': exam_results['total_score'],
        'max_score': exam_results['max_score'],
        'percentage': exam_results['percentage'],
        'passed': passed,
        'detailed_results': detailed_results,
        'submission_count': exam_results['submission_count'],
    }
    
    return render(request, 'course_app/exam_result.html', context)

def exam_statistics(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Calculate statistics
    total_submissions = Submission.objects.filter(question__lesson=lesson).count()
    unique_users = Submission.objects.filter(question__lesson=lesson).values('user').distinct().count()
    
    # Average score calculation
    user_scores = []
    users = User.objects.filter(submissions__question__lesson=lesson).distinct()
    
    for user in users:
        user_submissions = Submission.objects.filter(
            user=user,
            question__lesson=lesson
        ).order_by('-submitted_at')
        
        # Get latest submission per question
        latest_submissions = {}
        for submission in user_submissions:
            if submission.question_id not in latest_submissions:
                latest_submissions[submission.question_id] = submission
        
        user_score = 0
        max_score = 0
        
        for question in lesson.questions.all():
            max_score += question.points
            if question.id in latest_submissions:
                if latest_submissions[question.id].selected_choice.is_correct:
                    user_score += question.points
        
        if max_score > 0:
            percentage = (user_score / max_score * 100)
            user_scores.append(percentage)
    
    average_score = sum(user_scores) / len(user_scores) if user_scores else 0
    
    return JsonResponse({
        'total_submissions': total_submissions,
        'unique_users': unique_users,
        'average_score': round(average_score, 2),
        'questions_count': lesson.questions.count(),
    })