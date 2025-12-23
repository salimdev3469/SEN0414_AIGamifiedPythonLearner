"""
Challenge Manager - Handles challenge generation and progress tracking
"""

from datetime import date, timedelta, datetime
from django.utils import timezone
import pytz
from .models import Challenge, UserChallenge
from apps.coding.models import UserSubmission
from apps.learning.models import UserProgress
import random

# Istanbul timezone
ISTANBUL_TZ = pytz.timezone('Europe/Istanbul')


class ChallengeManager:
    """
    Manager for creating and tracking challenges.
    """
    
    @staticmethod
    def get_istanbul_date():
        """
        Get current date in Istanbul timezone.
        
        Returns:
            date: Current date in Istanbul timezone
        """
        istanbul_now = timezone.now().astimezone(ISTANBUL_TZ)
        return istanbul_now.date()
    
    @staticmethod
    def reset_and_generate_daily_challenges():
        """
        Reset expired daily challenges and generate new ones for today (Istanbul time).
        
        Returns:
            list: Created challenges
        """
        today = ChallengeManager.get_istanbul_date()
        
        # Deactivate expired daily challenges
        expired_daily = Challenge.objects.filter(
            challenge_type='daily',
            end_date__lt=today,
            is_active=True
        )
        expired_daily.update(is_active=False)
        
        # Check if daily challenges already exist for today
        existing = Challenge.objects.filter(
            challenge_type='daily',
            start_date=today,
            is_active=True
        ).exists()
        
        if existing:
            return []
        
        # Define challenge templates
        templates = [
            {
                'title': 'Daily Exercise Sprint',
                'description': 'Complete 3 coding exercises today',
                'target_metric': 'exercises_solved',
                'target_value': 3,
                'xp_reward': 150
            },
            {
                'title': 'Quick Learner',
                'description': 'Complete 1 lesson today',
                'target_metric': 'lessons_completed',
                'target_value': 1,
                'xp_reward': 100
            },
            {
                'title': 'XP Hunter',
                'description': 'Earn 200 XP today',
                'target_metric': 'xp_earned',
                'target_value': 200,
                'xp_reward': 100
            },
            {
                'title': 'Code Warrior',
                'description': 'Submit 5 code solutions today',
                'target_metric': 'code_submissions',
                'target_value': 5,
                'xp_reward': 120
            },
        ]
        
        # Select 3 random challenges
        selected = random.sample(templates, min(3, len(templates)))
        
        created_challenges = []
        for template in selected:
            challenge = Challenge.objects.create(
                title=template['title'],
                description=template['description'],
                challenge_type='daily',
                start_date=today,
                end_date=today,
                target_metric=template['target_metric'],
                target_value=template['target_value'],
                xp_reward=template['xp_reward'],
                is_active=True
            )
            created_challenges.append(challenge)
        
        return created_challenges
    
    @staticmethod
    def generate_daily_challenges():
        """
        Generate daily challenges for today (Istanbul time).
        Alias for reset_and_generate_daily_challenges for backward compatibility.
        
        Returns:
            list: Created challenges
        """
        return ChallengeManager.reset_and_generate_daily_challenges()
    
    @staticmethod
    def reset_and_generate_weekly_challenges():
        """
        Reset expired weekly challenges and generate new ones for this week (Istanbul time).
        
        Returns:
            list: Created challenges
        """
        today = ChallengeManager.get_istanbul_date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # Deactivate expired weekly challenges
        expired_weekly = Challenge.objects.filter(
            challenge_type='weekly',
            end_date__lt=today,
            is_active=True
        )
        expired_weekly.update(is_active=False)
        
        # Check if weekly challenges already exist for this week
        existing = Challenge.objects.filter(
            challenge_type='weekly',
            start_date=start_of_week,
            is_active=True
        ).exists()
        
        if existing:
            return []
        
        # Define weekly challenge templates
        templates = [
            {
                'title': 'Weekly Marathon',
                'description': 'Complete 15 exercises this week',
                'target_metric': 'exercises_solved',
                'target_value': 15,
                'xp_reward': 500
            },
            {
                'title': 'Knowledge Seeker',
                'description': 'Complete 5 lessons this week',
                'target_metric': 'lessons_completed',
                'target_value': 5,
                'xp_reward': 400
            },
            {
                'title': 'XP Master',
                'description': 'Earn 1,000 XP this week',
                'target_metric': 'xp_earned',
                'target_value': 1000,
                'xp_reward': 300
            },
        ]
        
        # Select 2 random challenges
        selected = random.sample(templates, min(2, len(templates)))
        
        created_challenges = []
        for template in selected:
            challenge = Challenge.objects.create(
                title=template['title'],
                description=template['description'],
                challenge_type='weekly',
                start_date=start_of_week,
                end_date=end_of_week,
                target_metric=template['target_metric'],
                target_value=template['target_value'],
                xp_reward=template['xp_reward'],
                is_active=True
            )
            created_challenges.append(challenge)
        
        return created_challenges
    
    @staticmethod
    def generate_weekly_challenges():
        """
        Generate weekly challenges for this week (Istanbul time).
        Alias for reset_and_generate_weekly_challenges for backward compatibility.
        
        Returns:
            list: Created challenges
        """
        return ChallengeManager.reset_and_generate_weekly_challenges()
    
    @staticmethod
    def update_challenge_progress(user, metric_type, increment=1):
        """
        Update user's progress on active challenges.
        
        Args:
            user: User object
            metric_type: Type of metric (exercises_solved, lessons_completed, etc.)
            increment: Amount to increment (default 1)
        
        Returns:
            list: Completed challenges
        """
        today = ChallengeManager.get_istanbul_date()
        
        # Get active challenges for this metric
        active_challenges = Challenge.objects.filter(
            target_metric=metric_type,
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        )
        
        completed_challenges = []
        
        for challenge in active_challenges:
            # Get or create user challenge
            user_challenge, created = UserChallenge.objects.get_or_create(
                user=user,
                challenge=challenge,
                defaults={'progress': 0}
            )
            
            if not user_challenge.completed:
                # Update progress
                user_challenge.progress += increment
                user_challenge.save()
                
                # Check if completed
                if user_challenge.check_completion():
                    # Award XP
                    user.add_xp(challenge.xp_reward)
                    completed_challenges.append(challenge)
        
        return completed_challenges
    
    @staticmethod
    def get_active_challenges(user):
        """
        Get active challenges for a user with their progress.
        
        Args:
            user: User object
        
        Returns:
            list: Challenges with progress
        """
        today = ChallengeManager.get_istanbul_date()
        
        # Get active challenges
        active_challenges = Challenge.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).order_by('challenge_type', 'start_date')
        
        challenges_with_progress = []
        
        for challenge in active_challenges:
            # Get user's progress
            try:
                user_challenge = UserChallenge.objects.get(
                    user=user,
                    challenge=challenge
                )
                progress = user_challenge.progress
                completed = user_challenge.completed
                progress_percentage = user_challenge.get_progress_percentage()
            except UserChallenge.DoesNotExist:
                progress = 0
                completed = False
                progress_percentage = 0
            
            challenges_with_progress.append({
                'challenge': challenge,
                'progress': progress,
                'completed': completed,
                'progress_percentage': progress_percentage
            })
        
        return challenges_with_progress
    
    @staticmethod
    def deactivate_expired_challenges():
        """
        Deactivate challenges that have expired (Istanbul time).
        
        Returns:
            int: Number of challenges deactivated
        """
        today = ChallengeManager.get_istanbul_date()
        
        expired = Challenge.objects.filter(
            is_active=True,
            end_date__lt=today
        )
        
        count = expired.count()
        expired.update(is_active=False)
        
        return count


# Convenience functions
def update_challenge(user, metric_type, increment=1):
    """Update user's challenge progress"""
    return ChallengeManager.update_challenge_progress(user, metric_type, increment)


def get_user_challenges(user):
    """Get active challenges for user"""
    return ChallengeManager.get_active_challenges(user)

