"""
Base test fixtures for all tests
"""
import pytest
from apps.authentication.models import User
from apps.learning.models import Module, Lesson
from apps.coding.models import Exercise, TestCase


@pytest.fixture
def test_user(db):
    """Create a test user"""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!'
    )
    return user


@pytest.fixture
def test_user_with_xp(db):
    """Create a test user with some XP"""
    user = User.objects.create_user(
        username='testuser_xp',
        email='testxp@example.com',
        password='TestPass123!'
    )
    user.xp = 150
    user.save()
    return user


@pytest.fixture
def test_module(db):
    """Create a test module"""
    return Module.objects.create(
        title='Test Module',
        description='This is a test module for unit testing',
        order=1,
        is_published=True
    )


@pytest.fixture
def test_lesson(db, test_module):
    """Create a test lesson"""
    return Lesson.objects.create(
        module=test_module,
        title='Test Lesson',
        content='# Test Lesson Content\n\nThis is a test lesson.',
        order=1,
        is_published=True,
        xp_reward=50  # Set XP reward to 50 for tests
    )


@pytest.fixture
def test_exercise(db, test_lesson):
    """Create a test exercise"""
    return Exercise.objects.create(
        lesson=test_lesson,
        title='Test Exercise',
        description='Write a function that adds two numbers',
        difficulty='beginner',
        starter_code='# Write your code here\n',
        solution_code='def add(a, b):\n    return a + b'
    )


@pytest.fixture
def test_testcase(db, test_exercise):
    """Create a test case for exercise"""
    return TestCase.objects.create(
        exercise=test_exercise,
        input_data='2, 3',
        expected_output='5',
        is_hidden=False
    )


@pytest.fixture
def authenticated_client(client, test_user):
    """Return a client with authenticated test user"""
    client.force_login(test_user)
    return client

