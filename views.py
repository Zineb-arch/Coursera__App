from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Course, Lesson, Question, Choice, Submission, Enrollment

@login_required
def submit(request, course_id):
    """
    Submit exam answers and calculate score
    """
    if request.method == 'POST':
        # Get course and user's enrollment
        course = get_object_or_404(Course, id=course_id)
        enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
        
        # Get all questions for this course
        questions = Question.objects.filter(lesson__course=course)
        
        total_score = 0
        max_score = questions.aggregate(total=Sum('points'))['total'] or 0
        
        # Process each question
        for question in questions:
            choice_id = request.POST.get(f'question_{question.id}')
            
            if choice_id:
                try:
                    selected_choice = Choice.objects.get(id=choice_id, question=question)
                    
                    # Create submission record
                    submission = Submission.objects.create(
                        enrollment=enrollment,
                        question=question,
                        choice=selected_choice
                    )
                    
                    # Add to score if correct
                    if selected_choice.is_correct:
                        total_score += question.points
                        
                except Choice.DoesNotExist:
                    # Invalid choice selected
                    continue
        
        # Calculate percentage
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        # Store results in session
        request.session['exam_results'] = {
            'course_id': course_id,
            'total_score': total_score,
            'max_score': max_score,
            'percentage': percentage,
        }
        
        # Redirect to results page
        return redirect('show_exam_result', course_id=course_id)
    
    # If not POST, redirect to course page
    return redirect('course_detail', course_id=course_id)

@login_required
def show_exam_result(request, course_id):
    """
    Display exam results with score and correct/incorrect answers
    """
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Get results from session or calculate
    exam_results = request.session.get('exam_results', {})
    
    # If no session data, calculate from database
    if not exam_results or exam_results.get('course_id') != course_id:
        # Get latest submissions for this enrollment
        submissions = Submission.objects.filter(
            enrollment=enrollment
        ).order_by('question__id', '-submitted_at')
        
        # Deduplicate - keep only latest per question
        latest_submissions = {}
        for submission in submissions:
            if submission.question.id not in latest_submissions:
                latest_submissions[submission.question.id] = submission
        
        # Calculate scores
        total_score = 0
        max_score = 0
        questions = Question.objects.filter(lesson__course=course)
        
        for question in questions:
            max_score += question.points
            if question.id in latest_submissions:
                if latest_submissions[question.id].choice.is_correct:
                    total_score += question.points
        
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        exam_results = {
            'course_id': course_id,
            'total_score': total_score,
            'max_score': max_score,
            'percentage': percentage,
        }
    
    # Get detailed results for template
    detailed_results = []
    questions = Question.objects.filter(lesson__course=course)
    
    for question in questions:
        # Get latest submission for this question
        latest_submission = Submission.objects.filter(
            enrollment=enrollment,
            question=question
        ).order_by('-submitted_at').first()
        
        detailed_results.append({
            'question': question,
            'user_choice': latest_submission.choice if latest_submission else None,
            'is_correct': latest_submission.choice.is_correct if latest_submission else False,
            'points': question.points,
            'earned_points': question.points if latest_submission and latest_submission.choice.is_correct else 0,
        })
    
    # Check if passed (70% or higher)
    passed = exam_results['percentage'] >= 70
    
    context = {
        'course': course,
        'total_score': exam_results['total_score'],
        'max_score': exam_results['max_score'],
        'percentage': round(exam_results['percentage'], 2),
        'passed': passed,
        'detailed_results': detailed_results,
        'enrollment': enrollment,
    }
    
    return render(request, 'course_app/exam_result.html', context)
