"""
Custom Django template filters for rendering Markdown content.
"""

from django import template
from django.utils.safestring import mark_safe
import markdown as md
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension

register = template.Library()


@register.filter(name='markdown')
def markdown_to_html(text):
    """
    Convert Markdown text to HTML with syntax highlighting support.
    
    Usage in templates:
        {{ lesson.content|markdown }}
    """
    if not text:
        return ''
    
    # Configure markdown extensions
    extensions = [
        'markdown.extensions.extra',      # Tables, fenced code, etc.
        'markdown.extensions.codehilite', # Syntax highlighting
        'markdown.extensions.nl2br',      # Convert newlines to <br>
        'markdown.extensions.sane_lists', # Better list handling
        'markdown.extensions.toc',        # Table of contents
    ]
    
    extension_configs = {
        'markdown.extensions.codehilite': {
            'css_class': 'highlight',
            'linenums': False,
            'guess_lang': True,
        }
    }
    
    # Convert markdown to HTML
    html = md.markdown(
        text,
        extensions=extensions,
        extension_configs=extension_configs
    )
    
    # Mark as safe HTML (won't be escaped by Django)
    return mark_safe(html)


@register.filter(name='markdown_preview')
def markdown_preview(text, length=200):
    """
    Convert Markdown to plain text preview.
    
    Usage:
        {{ lesson.content|markdown_preview:100 }}
    """
    if not text:
        return ''
    
    # Strip markdown syntax (basic)
    import re
    
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    
    # Remove headers
    text = re.sub(r'#+\s+', '', text)
    
    # Remove bold/italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    
    # Remove links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Trim to length
    if len(text) > length:
        text = text[:length] + '...'
    
    return text

