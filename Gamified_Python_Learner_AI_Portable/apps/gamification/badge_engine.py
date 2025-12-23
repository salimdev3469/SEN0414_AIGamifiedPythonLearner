"""
Badge Engine - Handles badge criteria checking and awarding
"""

from .models import Badge, UserBadge
from apps.coding.models import UserSubmission
from apps.learning.models import UserProgress


class BadgeEngine:
    """
    Engine for checking badge criteria and awarding badges to users.
    """
    
    @staticmethod
    def check_and_award_badges(user, trigger_type=None):
        """
        Check all badges and award any that the user has earned.
        
        Args:
            user: User object
            trigger_type: Optional trigger type to filter badges (e.g., 'exercise_solved')
        
        Returns:
            list: List of newly awarded badges
        """
        newly_awarded = []
        
        # Get all active badges
        badges = Badge.objects.filter(is_active=True)
        
        # Get badges user already has
        earned_badge_ids = UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
        
        # Check each badge
        for badge in badges:
            if badge.id in earned_badge_ids:
                continue  # User already has this badge
            
            # Check if user meets criteria
            if BadgeEngine._check_criteria(user, badge.criteria):
                # Award badge
                UserBadge.objects.create(
                    user=user,
                    badge=badge,
                    progress=100
                )
                
                # Award XP
                if badge.xp_reward > 0:
                    user.add_xp(badge.xp_reward)
                
                newly_awarded.append(badge)
        
        return newly_awarded
    
    @staticmethod
    def _check_criteria(user, criteria):
        """
        Check if user meets badge criteria.
        
        Args:
            user: User object
            criteria: Dictionary with criteria rules
        
        Returns:
            bool: True if criteria met
        """
        criteria_type = criteria.get('type')
        
        if criteria_type == 'exercises_solved':
            count = criteria.get('count', 1)
            user_count = UserSubmission.objects.filter(
                user=user,
                is_correct=True
            ).values('exercise').distinct().count()
            return user_count >= count
        
        elif criteria_type == 'lessons_completed':
            count = criteria.get('count', 1)
            user_count = UserProgress.objects.filter(
                user=user,
                status='completed'
            ).count()
            return user_count >= count
        
        elif criteria_type == 'xp_earned':
            target_xp = criteria.get('xp', 1000)
            return user.xp >= target_xp
        
        elif criteria_type == 'level_reached':
            target_level = criteria.get('level', 5)
            return user.level >= target_level
        
        elif criteria_type == 'streak_days':
            target_days = criteria.get('days', 7)
            if hasattr(user, 'streak'):
                return user.streak.current_streak >= target_days
            return False
        
        elif criteria_type == 'friends_count':
            target_count = criteria.get('count', 5)
            from .models import Friendship
            friend_count = Friendship.objects.filter(
                user=user,
                status='accepted'
            ).count()
            return friend_count >= target_count
        
        elif criteria_type == 'perfect_exercise':
            # Solve an exercise on first try
            exercise_id = criteria.get('exercise_id')
            if exercise_id:
                submissions = UserSubmission.objects.filter(
                    user=user,
                    exercise_id=exercise_id
                ).order_by('submitted_at')
                
                if submissions.exists():
                    first_submission = submissions.first()
                    return first_submission.is_correct
            return False
        
        elif criteria_type == 'module_master':
            # Complete all lessons in a module
            module_id = criteria.get('module_id')
            if module_id:
                from apps.learning.models import Module, Lesson
                module = Module.objects.filter(id=module_id).first()
                if module:
                    total_lessons = module.lessons.count()
                    completed_lessons = UserProgress.objects.filter(
                        user=user,
                        lesson__module=module,
                        status='completed'
                    ).count()
                    return total_lessons > 0 and total_lessons == completed_lessons
            return False
        
        return False
    
    @staticmethod
    def get_badge_progress(user, badge):
        """
        Get user's progress toward a specific badge.
        
        Args:
            user: User object
            badge: Badge object
        
        Returns:
            dict: Progress information
        """
        criteria = badge.criteria
        criteria_type = criteria.get('type')
        
        progress = {
            'current': 0,
            'target': 0,
            'percentage': 0,
            'earned': False
        }
        
        # Check if already earned
        if UserBadge.objects.filter(user=user, badge=badge).exists():
            progress['earned'] = True
            progress['percentage'] = 100
            return progress
        
        if criteria_type == 'exercises_solved':
            target = criteria.get('count', 1)
            current = UserSubmission.objects.filter(
                user=user,
                is_correct=True
            ).values('exercise').distinct().count()
            progress['current'] = current
            progress['target'] = target
        
        elif criteria_type == 'lessons_completed':
            target = criteria.get('count', 1)
            current = UserProgress.objects.filter(
                user=user,
                status='completed'
            ).count()
            progress['current'] = current
            progress['target'] = target
        
        elif criteria_type == 'xp_earned':
            target = criteria.get('xp', 1000)
            current = user.xp
            progress['current'] = current
            progress['target'] = target
        
        elif criteria_type == 'level_reached':
            target = criteria.get('level', 5)
            current = user.level
            progress['current'] = current
            progress['target'] = target
        
        elif criteria_type == 'streak_days':
            target = criteria.get('days', 7)
            current = user.streak.current_streak if hasattr(user, 'streak') else 0
            progress['current'] = current
            progress['target'] = target
        
        elif criteria_type == 'friends_count':
            target = criteria.get('count', 5)
            from .models import Friendship
            current = Friendship.objects.filter(
                user=user,
                status='accepted'
            ).count()
            progress['current'] = current
            progress['target'] = target
        
        # Calculate percentage
        if progress['target'] > 0:
            progress['percentage'] = min(100, int((progress['current'] / progress['target']) * 100))
        
        return progress
    
    @staticmethod
    def create_default_badges():
        """Create default badges for the system"""
        default_badges = [
            {
                'name': 'First Steps',
                'description': 'Complete your first exercise',
                'icon': '🎯',
                'badge_type': 'achievement',
                'criteria': {'type': 'exercises_solved', 'count': 1},
                'xp_reward': 50
            },
            {
                'name': 'Quick Learner',
                'description': 'Complete 10 exercises',
                'icon': '⚡',
                'badge_type': 'achievement',
                'criteria': {'type': 'exercises_solved', 'count': 10},
                'xp_reward': 100
            },
            {
                'name': 'Century Club',
                'description': 'Complete 100 exercises',
                'icon': '💯',
                'badge_type': 'milestone',
                'criteria': {'type': 'exercises_solved', 'count': 100},
                'xp_reward': 500
            },
            {
                'name': 'Knowledge Seeker',
                'description': 'Complete 5 lessons',
                'icon': '📚',
                'badge_type': 'achievement',
                'criteria': {'type': 'lessons_completed', 'count': 5},
                'xp_reward': 100
            },
            {
                'name': 'Perfect Week',
                'description': 'Maintain a 7-day learning streak',
                'icon': '🔥',
                'badge_type': 'achievement',
                'criteria': {'type': 'streak_days', 'days': 7},
                'xp_reward': 200
            },
            {
                'name': 'Unstoppable',
                'description': 'Maintain a 30-day learning streak',
                'icon': '🚀',
                'badge_type': 'milestone',
                'criteria': {'type': 'streak_days', 'days': 30},
                'xp_reward': 1000
            },
            {
                'name': 'Social Butterfly',
                'description': 'Add 5 friends',
                'icon': '🦋',
                'badge_type': 'achievement',
                'criteria': {'type': 'friends_count', 'count': 5},
                'xp_reward': 150
            },
            {
                'name': 'Rising Star',
                'description': 'Reach level 5',
                'icon': '⭐',
                'badge_type': 'milestone',
                'criteria': {'type': 'level_reached', 'level': 5},
                'xp_reward': 250
            },
            {
                'name': 'Python Master',
                'description': 'Reach level 10',
                'icon': '🐍',
                'badge_type': 'milestone',
                'criteria': {'type': 'level_reached', 'level': 10},
                'xp_reward': 500
            },
            {
                'name': 'XP Collector',
                'description': 'Earn 5,000 XP',
                'icon': '💎',
                'badge_type': 'milestone',
                'criteria': {'type': 'xp_earned', 'xp': 5000},
                'xp_reward': 300
            },
        ]
        
        created_count = 0
        for badge_data in default_badges:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                created_count += 1
        
        return created_count


# Convenience function
def check_badges(user):
    """Check and award badges for a user"""
    return BadgeEngine.check_and_award_badges(user)

