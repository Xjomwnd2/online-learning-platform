# courses/management/commands/create_sample_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import Category, Course, Lesson
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Create sample data for testing'
    
    def handle(self, *args, **options):
        # Create categories
        categories_data = [
            {'name': 'Programming', 'description': 'Learn programming languages and development skills'},
            {'name': 'Design', 'description': 'Master design principles and tools'},
            {'name': 'Business', 'description': 'Develop business and entrepreneurship skills'},
            {'name': 'Marketing', 'description': 'Learn digital marketing strategies'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(**cat_data)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create sample instructor
        instructor, created = User.objects.get_or_create(
            username='instructor1',
            defaults={
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'instructor@example.com'
            }
        )
        if created:
            instructor.set_password('instructor123')
            instructor.save()
            UserProfile.objects.create(user=instructor, user_type='instructor')
            self.stdout.write(f'Created instructor: {instructor.username}')
        
        # Create sample courses
        programming_cat = Category.objects.get(name='Programming')
        
        course_data = {
            'title': 'Python for Beginners',
            'description': 'Learn Python programming from scratch. This comprehensive course covers all the fundamentals you need to start coding in Python.',
            'instructor': instructor,
            'category': programming_cat,
            'difficulty': 'beginner',
            'duration_weeks': 8,
            'price': 0.00
        }
        
        course, created = Course.objects.get_or_create(**course_data)
        if created:
            # Create lessons for the course
            lessons_data = [
                {'title': 'Introduction to Python', 'content': 'Learn what Python is and why it\'s popular', 'order': 1, 'duration_minutes': 45},
                {'title': 'Variables and Data Types', 'content': 'Understanding Python variables and basic data types', 'order': 2, 'duration_minutes': 60},
                {'title': 'Control Structures', 'content': 'Learn about if statements, loops, and conditional logic', 'order': 3, 'duration_minutes': 75},
                {'title': 'Functions and Modules', 'content': 'Creating reusable code with functions and modules', 'order': 4, 'duration_minutes': 90},
            ]
            
            for lesson_data in lessons_data:
                lesson_data['course'] = course
                Lesson.objects.create(**lesson_data)
            
            self.stdout.write(f'Created course: {course.title} with {len(lessons_data)} lessons')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))