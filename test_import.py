import sys
sys.path.insert(0, '/Users/dhyana/clawd/products/rv-toolkit-gumroad')
try:
    import rv_toolkit
    print('✓ rv_toolkit import works')
except Exception as e:
    print(f'✗ rv_toolkit import error: {e}')
    import traceback
    traceback.print_exc()