# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Course, Category, Enrollment, Lesson
from progress.models import CourseProgress, LessonProgress

def home(request):
    featured_courses = Course.objects.filter(is_active=True)[:6]
    categories = Category.objects.all()
    return render(request, 'courses/home.html', {
        'featured_courses': featured_courses,
        'categories': categories
    })

def course_list(request):
    courses = Course.objects.filter(is_active=True)
    categories = Category.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        courses = courses.filter(category_id=category_id)
    
    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'categories': categories,
        'search_query': search_query
    })

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, is_active=True)
    lessons = course.lessons.all()
    is_enrolled = False
    
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            student=request.user, 
            course=course
        ).exists()
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled
    })

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)
    
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )
    
    if created:
        messages.success(request, f'Successfully enrolled in {course.title}!')
    else:
        messages.info(request, f'You are already enrolled in {course.title}.')
    
    return redirect('course_detail', pk=course_id)

@login_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    progress_data = []
    
    for enrollment in enrollments:
        progress, created = CourseProgress.objects.get_or_create(
            student=request.user,
            course=enrollment.course
        )
        progress_data.append({
            'enrollment': enrollment,
            'progress': progress
        })
    
    return render(request, 'courses/dashboard.html', {
        'progress_data': progress_data
    })

@login_required
def lesson_detail(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    # Check if user is enrolled
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.error(request, 'You must be enrolled in this course to access lessons.')
        return redirect('course_detail', pk=course_id)
    
    # Get or create lesson progress
    lesson_progress, created = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson
    )
    
    return render(request, 'courses/lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'lesson_progress': lesson_progress
    })

@login_required
def lesson_detail(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    # Check if user is enrolled
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.error(request, 'You must be enrolled in this course to access lessons.')
        return redirect('course_detail', pk=course_id)
    
    # Get or create lesson progress
    lesson_progress, created = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson
    )
    
    # Handle marking lesson as complete
    if request.method == 'POST' and 'mark_complete' in request.POST:
        if not lesson_progress.completed:
            lesson_progress.completed = True
            lesson_progress.completed_at = timezone.now()
            lesson_progress.save()
            
            # Update course progress
            from progress.views import update_course_progress
            update_course_progress(request.user, course)
            
            messages.success(request, f'Lesson "{lesson.title}" marked as completed!')
        
        return redirect('lesson_detail', course_id=course_id, lesson_id=lesson_id)
    
    # Get course progress for sidebar
    try:
        course_progress = CourseProgress.objects.get(student=request.user, course=course)
    except CourseProgress.DoesNotExist:
        course_progress = None
    
    # Get all lesson progress for this course
    lesson_progress_data = LessonProgress.objects.filter(
        student=request.user,
        lesson__course=course
    ).values_list('lesson_id', 'completed')
    
    completed_lessons = dict(lesson_progress_data)
    
    return render(request, 'courses/lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'lesson_progress': lesson_progress,
        'course_progress': course_progress,
        'completed_lessons': completed_lessons
    })