"""
AutoCraftCV Theme System Test
Test file to verify the implementation of the modern theme system
"""

import os
import sys
import time
from pathlib import Path

# Test results tracking
test_results = {
    'css_files': {},
    'js_files': {},
    'template_updates': {},
    'functionality': {}
}

def test_file_exists(file_path, description):
    """Test if a file exists and return its size"""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        test_results['css_files' if file_path.endswith('.css') else 'js_files'][description] = {
            'exists': True,
            'size': size,
            'path': file_path
        }
        print(f"✅ {description}: EXISTS ({size} bytes)")
        return True
    else:
        test_results['css_files' if file_path.endswith('.css') else 'js_files'][description] = {
            'exists': False,
            'size': 0,
            'path': file_path
        }
        print(f"❌ {description}: NOT FOUND")
        return False

def test_file_content(file_path, search_strings, description):
    """Test if a file contains specific content"""
    if not os.path.exists(file_path):
        print(f"❌ {description}: FILE NOT FOUND")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_strings = []
        found_strings = []
        
        for search_string in search_strings:
            if search_string in content:
                found_strings.append(search_string)
            else:
                missing_strings.append(search_string)
        
        if missing_strings:
            print(f"❌ {description}: MISSING CONTENT - {missing_strings}")
            test_results['template_updates'][description] = {
                'success': False,
                'found': found_strings,
                'missing': missing_strings
            }
            return False
        else:
            print(f"✅ {description}: ALL CONTENT FOUND")
            test_results['template_updates'][description] = {
                'success': True,
                'found': found_strings,
                'missing': []
            }
            return True
    except Exception as e:
        print(f"❌ {description}: ERROR READING FILE - {e}")
        return False

def main():
    print("🎨 AutoCraftCV Theme System Implementation Test")
    print("=" * 60)
    
    # Define base path
    base_path = Path(__file__).parent
    
    print("\n📂 Testing Core Theme Files:")
    print("-" * 30)
    
    # Test CSS files
    css_tests = [
        (base_path / 'static/css/main.css', 'Main Theme CSS'),
        (base_path / 'static/css/progress-tracker.css', 'Progress Tracker CSS'),
    ]
    
    for file_path, description in css_tests:
        test_file_exists(str(file_path), description)
    
    # Test JavaScript files
    js_tests = [
        (base_path / 'static/js/main.js', 'Main Theme JavaScript'),
        (base_path / 'static/js/progress-tracker.js', 'Progress Tracker JavaScript'),
    ]
    
    for file_path, description in js_tests:
        test_file_exists(str(file_path), description)
    
    print("\n🎨 Testing CSS Custom Properties:")
    print("-" * 35)
    
    # Test CSS custom properties
    main_css_path = base_path / 'static/css/main.css'
    css_variables = [
        '--bg-primary',
        '--bg-secondary',
        '--text-primary',
        '--text-secondary',
        '--btn-primary-bg',
        '--btn-primary-hover',
        '--card-bg',
        '--card-border',
        '--progress-bg',
        '--progress-fill',
        '[data-theme="dark"]'
    ]
    
    test_file_content(str(main_css_path), css_variables, 'CSS Custom Properties')
    
    print("\n🎯 Testing JavaScript Theme Management:")
    print("-" * 38)
    
    # Test JavaScript theme management
    main_js_path = base_path / 'static/js/main.js'
    js_functions = [
        'class ThemeManager',
        'setTheme(theme)',
        'toggleTheme()',
        'localStorage.getItem',
        'document.documentElement.setAttribute',
        'window.matchMedia',
        'ThemeAwareProgressTracker',
        'ThemedNotificationManager'
    ]
    
    test_file_content(str(main_js_path), js_functions, 'JavaScript Theme Management')
    
    print("\n📄 Testing Template Updates:")
    print("-" * 28)
    
    # Test base template updates
    base_template_path = base_path / 'templates/jobassistant/base.html'
    template_features = [
        'data-theme="light"',
        'class="theme-loading"',
        'id="themeToggle"',
        'theme-icon-light',
        'theme-icon-dark',
        'main.css',
        'main.js',
        'mobileThemeToggle'
    ]
    
    test_file_content(str(base_template_path), template_features, 'Base Template Updates')
    
    print("\n🎨 Testing Progress Tracker Theme Integration:")
    print("-" * 45)
    
    # Test progress tracker CSS theme integration
    progress_css_path = base_path / 'static/css/progress-tracker.css'
    progress_variables = [
        'var(--card-bg)',
        'var(--card-border)',
        'var(--text-primary)',
        'var(--btn-primary-bg)',
        'var(--success-state)',
        'var(--error-state)',
        'var(--transition-fast)'
    ]
    
    test_file_content(str(progress_css_path), progress_variables, 'Progress Tracker Theme Variables')
    
    print("\n🔧 Testing Accessibility Features:")
    print("-" * 32)
    
    # Test accessibility features
    accessibility_features = [
        '@media (prefers-reduced-motion: reduce)',
        '@media (prefers-contrast: high)',
        'aria-label',
        'title=',
        'role='
    ]
    
    # Check main CSS for accessibility
    test_file_content(str(main_css_path), accessibility_features[:2], 'CSS Accessibility Features')
    
    # Check base template for accessibility
    test_file_content(str(base_template_path), accessibility_features[2:], 'Template Accessibility Features')
    
    print("\n📱 Testing Responsive Design:")
    print("-" * 28)
    
    # Test responsive design features
    responsive_features = [
        '@media (max-width: 768px)',
        'd-lg-none',
        'mobileThemeToggle',
        'flex-wrap',
        'justify-content-center'
    ]
    
    test_file_content(str(main_css_path), responsive_features[:1], 'CSS Responsive Design')
    test_file_content(str(base_template_path), responsive_features[1:3], 'Template Responsive Features')
    
    print("\n📊 Test Results Summary:")
    print("=" * 25)
    
    # Count successes and failures
    total_tests = 0
    passed_tests = 0
    
    for category, tests in test_results.items():
        for test_name, result in tests.items():
            total_tests += 1
            if isinstance(result, dict):
                if result.get('exists', False) or result.get('success', False):
                    passed_tests += 1
    
    print(f"✅ Passed: {passed_tests}/{total_tests} tests")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests} tests")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Theme system successfully implemented!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Please review the implementation.")
    
    print("\n🚀 Next Steps:")
    print("-" * 12)
    print("1. Start the Django development server: python manage.py runserver")
    print("2. Visit http://127.0.0.1:8000 to test the theme toggle")
    print("3. Test keyboard shortcut: Ctrl+D (or Cmd+D on Mac)")
    print("4. Test mobile responsive theme toggle")
    print("5. Verify theme persistence after page refresh")
    print("6. Test with system dark mode preference")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
