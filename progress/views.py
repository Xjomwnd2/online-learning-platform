# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from courses.models import Course, Lesson, Enrollment
from .models import CourseProgress, LessonProgress
from django.utils import timezone

def index(request):
    return HttpResponse("Welcome to the progress page.")
@login_required
def update_lesson_progress(request, lesson_id):
    """Mark a lesson as completed and update course progress"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Check if user is enrolled in the course
    if not Enrollment.objects.filter(student=request.user, course=lesson.course).exists():
        messages.error(request, 'You must be enrolled in this course.')
        return redirect('course_detail', pk=lesson.course.id)
    
    # Get or create lesson progress
    lesson_progress, created = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson,
        defaults={'completed': True, 'completed_at': timezone.now()}
    )
    
    if not lesson_progress.completed:
        lesson_progress.completed = True
        lesson_progress.completed_at = timezone.now()
        lesson_progress.save()
        messages.success(request, f'Lesson "{lesson.title}" marked as completed!')
    
    # Update course progress
    update_course_progress(request.user, lesson.course)
    
    return redirect('lesson_detail', course_id=lesson.course.id, lesson_id=lesson.id)

def update_course_progress(user, course):
    """Calculate and update course progress percentage"""
    total_lessons = course.lessons.count()
    if total_lessons == 0:
        return
    
    completed_lessons = LessonProgress.objects.filter(
        student=user,
        lesson__course=course,
        completed=True
    ).count()
    
    progress_percentage = (completed_lessons / total_lessons) * 100
    
    course_progress, created = CourseProgress.objects.get_or_create(
        student=user,
        course=course,
        defaults={'progress_percentage': progress_percentage}
    )
    
    course_progress.progress_percentage = progress_percentage
    course_progress.save()
    
    # Check if course is completed
    if progress_percentage == 100:
        enrollment = Enrollment.objects.get(student=user, course=course)
        if not enrollment.completed:
            enrollment.completed = True
            enrollment.completion_date = timezone.now()
            enrollment.save()

@login_required
def progress_api(request, course_id):
    """API endpoint to get course progress data"""
    course = get_object_or_404(Course, id=course_id)
    
    try:
        course_progress = CourseProgress.objects.get(student=request.user, course=course)
        lesson_progress = LessonProgress.objects.filter(
            student=request.user,
            lesson__course=course
        ).values('lesson_id', 'completed', 'completed_at')
        
        return JsonResponse({
            'course_progress': course_progress.progress_percentage,
            'lesson_progress': list(lesson_progress)
        })
    except CourseProgress.DoesNotExist:
        return JsonResponse({'course_progress': 0, 'lesson_progress': []})