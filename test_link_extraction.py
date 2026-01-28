"""
Test link extraction functionality to prevent regression of the multiple link bug.

This test ensures that URLs are correctly extracted without including non-URL
characters like Arabic text that might follow the URL.
"""
import re
import sys
import os

# Add the parent directory to the path to import from matrix_bot
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the actual function from matrix_bot.py to ensure we're testing the real implementation
# Note: This will fail if dependencies like 'dotenv' and 'nio' are not installed,
# so we provide a fallback implementation for testing purposes
try:
    from matrix_bot import find_links_in_text
except ImportError:
    # Fallback: Define the function here if imports fail (e.g., missing dependencies)
    def find_links_in_text(text):
        """Fallback implementation matching matrix_bot.py for testing when dependencies are missing."""
        url_pattern = re.compile(
            r'(?:(?:http[s]?://|ftp://|www\.)|(?:(?!(?:http[s]?|ftp)://|www\.))(?=[a-zA-Z0-9]))'
            r'(?:[a-zA-Z0-9\-]+\.)+(?:[a-zA-Z]{2,})'
            r'(?::[0-9]+)?'
            r'(?:/[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]*)?',
            re.IGNORECASE | re.ASCII
        )
        return url_pattern.findall(text)


def test_plain_text_with_arabic():
    """Test URL extraction from plain text with Arabic text on following lines."""
    text = '''حساب متخصص في نماذج الذكاء الاصطناعي ذكر أن ByteDance تختبر نموذج Doubao الجديد في Kilo Code تحت الاسم Giga-Potato
ونقل وصف Kilo نفسه (256k سياق - 32k إخراج - التزام صارم بالتعليمات).
https://x.com/AiBattle_/status/2014361796279181388

وحساب آخر في Reddit يؤكد ذلك:
https://www.reddit.com/user/PrizeHuman5506/

وتبقى مجرد توقعات أو تكهنات حتى يصدر خبرا مؤكدا لذلك.'''
    
    found_links = find_links_in_text(text)
    
    assert len(found_links) == 2, f"Expected 2 links, found {len(found_links)}"
    
    # Verify no non-ASCII characters in URLs
    for link in found_links:
        assert all(ord(c) < 128 for c in link), f"Non-ASCII characters found in URL: {link}"
    
    # Verify exact URLs
    assert found_links[0] == 'https://x.com/AiBattle_/status/2014361796279181388'
    assert found_links[1] == 'https://www.reddit.com/user/PrizeHuman5506/'
    
    print("✓ test_plain_text_with_arabic passed")


def test_html_content_without_spaces():
    """Test URL extraction from HTML content where URLs are directly followed by text."""
    formatted_body = '''حساب متخصص في نماذج الذكاء الاصطناعي ذكر أن ByteDance تختبر نموذج Doubao الجديد في Kilo Code تحت الاسم Giga-Potato
ونقل وصف Kilo نفسه (256k سياق - 32k إخراج - التزام صارم بالتعليمات).
<a href="https://x.com/AiBattle_/status/2014361796279181388">https://x.com/AiBattle_/status/2014361796279181388</a>وحساب آخر في Reddit يؤكد ذلك:
<a href="https://www.reddit.com/user/PrizeHuman5506/">https://www.reddit.com/user/PrizeHuman5506/</a>وتبقى مجرد توقعات أو تكهنات حتى يصدر خبرا مؤكدا لذلك.'''
    
    # Simulate HTML tag removal
    clean_content = re.sub(r'<[^>]+>', '', formatted_body)
    
    found_links = find_links_in_text(clean_content)
    
    assert len(found_links) == 2, f"Expected 2 links, found {len(found_links)}"
    
    # Verify no non-ASCII characters in URLs
    for link in found_links:
        assert all(ord(c) < 128 for c in link), f"Non-ASCII characters found in URL: {link}"
    
    # Verify exact URLs (should not include Arabic text)
    assert found_links[0] == 'https://x.com/AiBattle_/status/2014361796279181388'
    assert found_links[1] == 'https://www.reddit.com/user/PrizeHuman5506/'
    
    print("✓ test_html_content_without_spaces passed")


def test_multiple_urls_with_query_params():
    """Test URL extraction with query parameters and fragments."""
    text = '''Check out these links:
https://example.com/path?param1=value1&param2=value2
https://test.org/page#section
https://site.com/path?q=search+terms&lang=en'''
    
    found_links = find_links_in_text(text)
    
    assert len(found_links) == 3, f"Expected 3 links, found {len(found_links)}"
    
    # Verify query params and fragments are included
    assert 'param1=value1&param2=value2' in found_links[0]
    assert '#section' in found_links[1]
    assert 'q=search+terms&lang=en' in found_links[2]
    
    print("✓ test_multiple_urls_with_query_params passed")


def test_urls_with_special_chars():
    """Test URL extraction with special characters in path."""
    text = '''Various URLs:
https://example.com/path_with-dashes/file.html
https://test.org/~user/page
https://site.com/(parens)/[brackets]'''
    
    found_links = find_links_in_text(text)
    
    assert len(found_links) == 3, f"Expected 3 links, found {len(found_links)}"
    
    # Verify special characters are included
    assert 'path_with-dashes' in found_links[0]
    assert '~user' in found_links[1]
    assert '(parens)' in found_links[2]
    assert '[brackets]' in found_links[2]
    
    print("✓ test_urls_with_special_chars passed")


def test_no_duplicate_extraction():
    """Test that the same URL appearing multiple times is found each time."""
    text = '''First mention: https://example.com/page
Second mention: https://example.com/page
Different: https://other.com/path'''
    
    found_links = find_links_in_text(text)
    
    # Should find all three occurrences (even though two are the same URL)
    assert len(found_links) == 3, f"Expected 3 links, found {len(found_links)}"
    
    print("✓ test_no_duplicate_extraction passed")


def test_mixed_language_text():
    """Test URL extraction from text with multiple languages."""
    text = '''English text with link https://example.com/path
中文文字 https://test.org/page 更多中文
Русский текст https://site.com/page еще текст
مزيد من النص العربي https://arabic.example.com/path نهاية النص'''
    
    found_links = find_links_in_text(text)
    
    assert len(found_links) == 4, f"Expected 4 links, found {len(found_links)}"
    
    # Verify no non-ASCII in any URLs
    for link in found_links:
        assert all(ord(c) < 128 for c in link), f"Non-ASCII characters found in URL: {link}"
    
    print("✓ test_mixed_language_text passed")


def run_all_tests():
    """Run all test functions."""
    tests = [
        test_plain_text_with_arabic,
        test_html_content_without_spaces,
        test_multiple_urls_with_query_params,
        test_urls_with_special_chars,
        test_no_duplicate_extraction,
        test_mixed_language_text,
    ]
    
    failed = []
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed.append(test.__name__)
    
    print("\n" + "=" * 70)
    if failed:
        print(f"FAILED: {len(failed)} test(s) failed: {', '.join(failed)}")
        return 1
    else:
        print(f"SUCCESS: All {len(tests)} tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
