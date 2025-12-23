"""
Utility functions for the learning app.
"""

import google.generativeai as genai
from django.conf import settings
from apps.ai_tutor.rate_limiter import check_gemini_rate_limit
import time


class GeminiContentGenerator:
    """Generate educational content using Google Gemini API."""
    
    def __init__(self):
        """Initialize Gemini API with API key from settings."""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    def generate_lesson_content(self, topic, difficulty='beginner', estimated_time=15):
        """
        Generate comprehensive lesson content for a given topic.
        
        Args:
            topic (str): The topic to generate content for
            difficulty (str): Difficulty level (beginner, intermediate, advanced)
            estimated_time (int): Estimated time in minutes
        
        Returns:
            str: Markdown formatted lesson content
        """
        prompt = f"""
You are an expert Python programming instructor creating engaging, comprehensive educational content.

Create a detailed Python lesson on: **{topic}**
Difficulty Level: {difficulty}
Target Duration: {estimated_time} minutes

Format the content in **MARKDOWN** with the following structure:

# {topic}

[Brief engaging introduction - 2-3 sentences explaining why this topic matters]

## What You'll Learn

- Key concept 1
- Key concept 2
- Key concept 3

## Core Concepts

[Detailed explanation of the main concepts]

### Concept 1: [Name]

[Explanation with examples]

```python
# Clear, runnable code example
# With comments explaining each line
```

**Output:**
```
[Expected output]
```

### Concept 2: [Name]

[Continue with more concepts...]

## Practical Examples

### Example 1: [Real-world Scenario]

[Problem description]

```python
# Solution code with detailed comments
```

[Explanation of the solution]

### Example 2: [Another Scenario]

[Continue with more examples...]

## Common Patterns & Best Practices

- ✅ Do: [Best practice 1]
- ✅ Do: [Best practice 2]
- ❌ Avoid: [Common mistake 1]
- ❌ Avoid: [Common mistake 2]

## 🎯 Key Takeaways

- Main point 1
- Main point 2
- Main point 3

## 💡 Practice Challenge

[Describe a challenge that tests understanding]

**Challenge:**
Create a program that [specific task]

**Requirements:**
1. Requirement 1
2. Requirement 2
3. Requirement 3

**Hints:**
- Hint 1
- Hint 2

## Next Steps

[What to learn next after mastering this topic]

---

**IMPORTANT GUIDELINES:**
1. Use clear, beginner-friendly language
2. Include AT LEAST 5-7 runnable code examples
3. Add comments to explain complex parts
4. Use emojis sparingly for visual interest (🎯, 💡, ✅, ❌)
5. Make examples practical and relatable
6. Include expected output for code examples
7. Keep explanations concise but thorough
8. Use proper markdown formatting (headers, code blocks, lists, bold)
9. Ensure all code examples are syntactically correct
10. Make it engaging and encourage learning

Generate the COMPLETE lesson content now:
"""

        try:
            # Check rate limit
            allowed, remaining, reset_time = check_gemini_rate_limit()
            if not allowed:
                return None  # Rate limit exceeded
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'top_k': 40,
                    'max_output_tokens': 4096,
                }
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                return None
                
        except Exception as e:
            print(f"Error generating content: {e}")
            return None
    
    def generate_module_description(self, module_title, lesson_topics):
        """
        Generate a compelling module description.
        
        Args:
            module_title (str): Title of the module
            lesson_topics (list): List of lesson titles in the module
        
        Returns:
            str: Module description
        """
        prompt = f"""
Create a compelling, concise description (2-3 sentences) for a Python learning module titled: **{module_title}**

The module contains these lessons:
{chr(10).join(f'- {topic}' for topic in lesson_topics)}

Make it engaging and explain what learners will achieve. Keep it under 150 characters if possible.
"""

        try:
            # Check rate limit
            allowed, remaining, reset_time = check_gemini_rate_limit()
            if not allowed:
                return f"Learn essential concepts in {module_title}"  # Fallback
            
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
            return f"Learn essential concepts in {module_title}"
        except Exception as e:
            print(f"Error generating description: {e}")
            return f"Master {module_title} step by step"
    
    def enhance_existing_content(self, existing_content, enhancement_type='expand'):
        """
        Enhance existing lesson content.
        
        Args:
            existing_content (str): The current lesson content
            enhancement_type (str): Type of enhancement (expand, simplify, add_examples)
        
        Returns:
            str: Enhanced content
        """
        if enhancement_type == 'expand':
            instruction = "Expand this content with more detailed explanations, additional examples, and practical use cases."
        elif enhancement_type == 'simplify':
            instruction = "Simplify this content for absolute beginners while keeping all key concepts."
        elif enhancement_type == 'add_examples':
            instruction = "Add 3-5 more practical, real-world code examples to this content."
        else:
            instruction = "Improve the overall quality and engagement of this content."
        
        prompt = f"""
{instruction}

Keep the markdown formatting and structure. Here's the content:

---
{existing_content}
---

Provide the ENHANCED version:
"""

        try:
            # Check rate limit
            allowed, remaining, reset_time = check_gemini_rate_limit()
            if not allowed:
                return existing_content  # Return existing content if rate limited
            
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
            return existing_content
        except Exception as e:
            print(f"Error enhancing content: {e}")
            return existing_content


class GeminiExerciseGenerator:
    """Generate coding exercises using Google Gemini API."""
    
    def __init__(self):
        """Initialize Gemini API with API key from settings."""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    def generate_exercises_for_lesson(self, lesson_title, lesson_content, num_exercises=None):
        """
        Generate coding exercises based on lesson content.
        
        Args:
            lesson_title (str): Title of the lesson
            lesson_content (str): Full content of the lesson
            num_exercises (int): Number of exercises to generate (auto-determined if None)
        
        Returns:
            list: List of exercise dictionaries with all necessary fields
        """
        prompt = f"""
You are an expert Python programming instructor creating coding exercises.

**Lesson Title:** {lesson_title}

**Lesson Content Summary:**
{lesson_content[:2000]}... [truncated for context]

**Task:**
Analyze the lesson content and generate {"5-10" if num_exercises is None else num_exercises} high-quality coding exercises that comprehensively cover ALL topics taught in this lesson.

**Exercise Distribution:**
- Determine appropriate difficulty levels based on lesson complexity
- For beginner lessons: More Easy exercises, few Medium
- For intermediate lessons: Mix of Easy, Medium, and some Hard
- For advanced lessons: More Medium/Hard exercises

**For EACH exercise, provide a JSON object with these exact fields:**

```json
{{
  "title": "Clear, specific exercise title",
  "description": "Detailed problem description in Markdown. Explain what code to write, provide examples of input/output. Be clear and comprehensive.",
  "difficulty": "easy|medium|hard",
  "xp_reward": 50-150 (based on difficulty: easy=50, medium=100, hard=150),
  "starter_code": "# Write your code here\\n",
  "solution_code": "Complete, working solution code (simple and direct, no unnecessary function wrappers)",
  "hints": ["Hint 1", "Hint 2", "Hint 3"],
  "expected_approach": "Brief description of the expected algorithm/approach",
  "test_cases": [
    {{
      "input": "Test input as JSON string",
      "expected_output": "Expected output as string",
      "is_hidden": false
    }}
  ]
}}
```

**Requirements:**
1. Cover ALL major topics from the lesson
2. Exercises should progressively build on each other
3. Include 3-5 test cases per exercise (mix of visible and hidden)
4. Starter code should have clear function signature
5. Solution code must be complete and correct
6. Hints should guide without giving away the solution
7. Make descriptions clear and beginner-friendly
8. Use real-world, relatable examples

**Output Format:**
Return a valid JSON array of exercise objects. ONLY JSON, no markdown code blocks or explanations.

Generate exercises now:
"""

        try:
            # Check rate limit
            allowed, remaining, reset_time = check_gemini_rate_limit()
            if not allowed:
                return []  # Return empty list if rate limited
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.8,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 8192,
                }
            )
            
            if response and response.text:
                import json
                import re
                
                # Clean response - remove markdown code blocks if present
                text = response.text.strip()
                text = re.sub(r'```json\s*', '', text)
                text = re.sub(r'```\s*$', '', text)
                text = text.strip()
                
                # Parse JSON
                exercises = json.loads(text)
                return exercises
            else:
                return []
                
        except Exception as e:
            print(f"Error generating exercises: {e}")
            print(f"Response text: {response.text if response else 'No response'}")
            return []


class GeminiCodeEvaluator:
    """Evaluate user code submissions using Google Gemini API."""
    
    def __init__(self):
        """Initialize Gemini API with API key from settings."""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    def evaluate_submission(self, exercise_description, user_code, test_cases):
        """
        Evaluate user's code submission.
        
        Args:
            exercise_description (str): Description of the exercise
            user_code (str): User's submitted code
            test_cases (list): List of TestCase objects or dictionaries
        
        Returns:
            dict: Evaluation results with feedback, correctness, etc.
        """
        # Handle both TestCase objects and dictionaries
        test_cases_list = []
        for i, tc in enumerate(test_cases):
            if hasattr(tc, 'input_data'):
                # It's a TestCase object
                input_val = tc.input_data
                expected_val = tc.expected_output
            else:
                # It's a dictionary
                input_val = tc.get('input_data', tc.get('input', ''))
                expected_val = tc.get('expected_output', tc.get('expected', ''))
            test_cases_list.append(f"Test {i+1}: Input={input_val}, Expected={expected_val}")
        
        test_cases_str = "\n".join(test_cases_list)
        
        prompt = f"""
You are an expert Python code reviewer and educator.

**Exercise:**
{exercise_description}

**Test Cases:**
{test_cases_str}

**User's Code:**
```python
{user_code}
```

**Task:**
Evaluate this code submission thoroughly and provide detailed feedback.

**Your evaluation must include:**

1. **Correctness Analysis:**
   - Does the code solve the problem correctly?
   - Run through each test case mentally
   - Check for logic errors, edge cases

2. **Code Quality:**
   - Is the code clean and readable?
   - Are variable names meaningful?
   - Is it properly structured?

3. **Efficiency:**
   - Is the algorithm efficient?
   - Any unnecessary operations?

4. **Best Practices:**
   - Follows Python conventions?
   - Proper use of Python features?

**Output Format (JSON):**
```json
{{
  "is_correct": true/false,
  "passed_tests": number (0-{len(test_cases)}),
  "total_tests": {len(test_cases)},
  "feedback": "Comprehensive feedback explaining what works and what doesn't. Be encouraging and educational.",
  "suggestions": "Specific suggestions for improvement. If correct, suggest optimizations or alternative approaches.",
  "error_message": "If there are errors, explain them clearly. Empty string if no errors.",
  "test_results": [
    {{
      "test_number": 1,
      "passed": true/false,
      "details": "Why it passed/failed"
    }}
  ],
  "code_quality_score": 0-100 (integer),
  "encouragement": "Positive, encouraging message regardless of correctness"
}}
```

Return ONLY the JSON object, no markdown code blocks or explanations.

Evaluate now:
"""

        try:
            # Check rate limit
            allowed, remaining, reset_time = check_gemini_rate_limit()
            if not allowed:
                return {
                    'correct': False,
                    'feedback': f"⚠️ Günlük API limitine ulaşıldı. Lütfen {reset_time.strftime('%H:%M')} saatinden sonra tekrar deneyin.",
                    'score': 0,
                    'test_results': []
                }
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            
            if response and response.text:
                import json
                import re
                
                # Clean response
                text = response.text.strip()
                text = re.sub(r'```json\s*', '', text)
                text = re.sub(r'```\s*$', '', text)
                text = text.strip()
                
                # Parse JSON
                result = json.loads(text)
                return result
            else:
                return self._default_error_response()
                
        except Exception as e:
            error_str = str(e)
            print(f"Error evaluating code: {e}")
            
            # Check for quota/rate limit errors
            if '429' in error_str or 'quota' in error_str.lower() or 'rate limit' in error_str.lower():
                return self._quota_exceeded_response()
            
            return self._default_error_response()
    
    def _default_error_response(self):
        """Return default error response if AI fails."""
        return {
            "is_correct": False,
            "passed_tests": 0,
            "total_tests": 0,
            "feedback": "Unable to evaluate code at this time. Please try again.",
            "suggestions": "Make sure your code is syntactically correct and try submitting again.",
            "error_message": "Evaluation service temporarily unavailable.",
            "test_results": [],
            "code_quality_score": 0,
            "encouragement": "Don't give up! Keep trying!"
        }
    
    def _quota_exceeded_response(self):
        """Return response when API quota is exceeded."""
        return {
            "is_correct": False,
            "passed_tests": 0,
            "total_tests": 0,
            "feedback": "⚠️ AI evaluation service is currently unavailable due to quota limits. Your code will be evaluated based on test cases only.",
            "suggestions": "Please wait a few minutes and try again. In the meantime, check your code against the test cases manually.",
            "error_message": "API quota exceeded. Please try again in a few minutes.",
            "test_results": [],
            "code_quality_score": 0,
            "encouragement": "Your code will still be tested! Keep coding! 💪"
        }


# Singleton instances
_generator = None
_exercise_generator = None
_code_evaluator = None

def get_gemini_generator():
    """Get or create Gemini content generator instance."""
    global _generator
    if _generator is None:
        _generator = GeminiContentGenerator()
    return _generator

def get_exercise_generator():
    """Get or create Gemini exercise generator instance."""
    global _exercise_generator
    if _exercise_generator is None:
        _exercise_generator = GeminiExerciseGenerator()
    return _exercise_generator

def get_code_evaluator():
    """Get or create Gemini code evaluator instance."""
    global _code_evaluator
    if _code_evaluator is None:
        _code_evaluator = GeminiCodeEvaluator()
    return _code_evaluator

