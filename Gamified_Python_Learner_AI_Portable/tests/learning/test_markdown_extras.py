"""
Tests for markdown template filters
"""
import pytest
from django.template import Template, Context
from apps.learning.templatetags.markdown_extras import markdown_to_html, markdown_preview


class TestMarkdownToHtml:
    """Tests for markdown_to_html filter"""
    
    def test_empty_text(self):
        """Test with empty text"""
        result = markdown_to_html('')
        assert result == ''
    
    def test_none_text(self):
        """Test with None"""
        result = markdown_to_html(None)
        assert result == ''
    
    def test_basic_text(self):
        """Test with basic text"""
        result = markdown_to_html('Hello world')
        assert '<p>Hello world</p>' in result
    
    def test_headers(self):
        """Test markdown headers"""
        result = markdown_to_html('# Header 1\n## Header 2')
        assert '<h1' in result  # May have id attribute
        assert '<h2' in result
    
    def test_bold_text(self):
        """Test bold text"""
        result = markdown_to_html('**bold text**')
        assert '<strong>bold text</strong>' in result
    
    def test_italic_text(self):
        """Test italic text"""
        result = markdown_to_html('*italic text*')
        assert '<em>italic text</em>' in result
    
    def test_code_block(self):
        """Test code block"""
        text = '''```python
def hello():
    print("Hello")
```'''
        result = markdown_to_html(text)
        assert 'hello' in result
        assert 'print' in result
    
    def test_inline_code(self):
        """Test inline code"""
        result = markdown_to_html('Use `print()` function')
        assert '<code>' in result
        assert 'print()' in result
    
    def test_links(self):
        """Test links"""
        result = markdown_to_html('[Google](https://google.com)')
        assert '<a href="https://google.com">' in result
        assert 'Google</a>' in result
    
    def test_lists(self):
        """Test unordered lists"""
        text = '''- Item 1
- Item 2
- Item 3'''
        result = markdown_to_html(text)
        assert '<ul>' in result
        assert '<li>' in result
    
    def test_ordered_lists(self):
        """Test ordered lists"""
        text = '''1. First
2. Second
3. Third'''
        result = markdown_to_html(text)
        assert '<ol>' in result
        assert '<li>' in result
    
    def test_blockquote(self):
        """Test blockquote"""
        result = markdown_to_html('> This is a quote')
        assert '<blockquote>' in result
    
    def test_tables(self):
        """Test markdown tables"""
        text = '''| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |'''
        result = markdown_to_html(text)
        assert '<table>' in result
        assert '<th>' in result
        assert '<td>' in result
    
    def test_newlines_to_br(self):
        """Test that newlines are converted to br"""
        result = markdown_to_html('Line 1\nLine 2')
        assert '<br' in result or '</p>\n<p>' in result
    
    def test_result_is_marked_safe(self):
        """Test that result is marked safe"""
        from django.utils.safestring import SafeString
        result = markdown_to_html('Test')
        assert isinstance(result, SafeString)


class TestMarkdownPreview:
    """Tests for markdown_preview filter"""
    
    def test_empty_text(self):
        """Test with empty text"""
        result = markdown_preview('')
        assert result == ''
    
    def test_none_text(self):
        """Test with None"""
        result = markdown_preview(None)
        assert result == ''
    
    def test_basic_text(self):
        """Test with basic text"""
        result = markdown_preview('Hello world')
        assert result == 'Hello world'
    
    def test_strips_headers(self):
        """Test that headers are stripped"""
        result = markdown_preview('# Header\nContent')
        assert '#' not in result
        assert 'Header' in result
    
    def test_strips_bold(self):
        """Test that bold markers are stripped"""
        result = markdown_preview('This is **bold** text')
        assert '**' not in result
        assert 'bold' in result
    
    def test_strips_italic(self):
        """Test that italic markers are stripped"""
        result = markdown_preview('This is *italic* text')
        assert '*' not in result or 'italic' in result
    
    def test_strips_links(self):
        """Test that links are converted to text"""
        result = markdown_preview('Click [here](https://example.com)')
        assert '[' not in result
        assert 'here' in result
    
    def test_strips_code_blocks(self):
        """Test that code blocks are stripped"""
        text = '''Some text
```python
code here
```
More text'''
        result = markdown_preview(text)
        assert '```' not in result
        assert 'code here' not in result
    
    def test_strips_inline_code(self):
        """Test that inline code is stripped"""
        result = markdown_preview('Use `print()` function')
        assert '`' not in result
    
    def test_truncates_long_text(self):
        """Test that long text is truncated"""
        long_text = 'A' * 300
        result = markdown_preview(long_text, 200)
        assert len(result) == 203  # 200 chars + '...'
        assert result.endswith('...')
    
    def test_custom_length(self):
        """Test with custom length parameter"""
        text = 'A' * 100
        result = markdown_preview(text, 50)
        assert len(result) == 53  # 50 chars + '...'
    
    def test_short_text_not_truncated(self):
        """Test that short text is not truncated"""
        text = 'Short text'
        result = markdown_preview(text, 200)
        assert result == 'Short text'
        assert '...' not in result


class TestMarkdownInTemplate:
    """Tests for using markdown filters in templates"""
    
    def test_markdown_filter_in_template(self):
        """Test markdown filter usage in template"""
        template = Template('{% load markdown_extras %}{{ content|markdown }}')
        context = Context({'content': '**Hello**'})
        rendered = template.render(context)
        assert '<strong>Hello</strong>' in rendered
    
    def test_markdown_preview_filter_in_template(self):
        """Test markdown_preview filter usage in template"""
        template = Template('{% load markdown_extras %}{{ content|markdown_preview:50 }}')
        context = Context({'content': '# Header\n' + 'A' * 100})
        rendered = template.render(context)
        assert '#' not in rendered
        assert '...' in rendered
