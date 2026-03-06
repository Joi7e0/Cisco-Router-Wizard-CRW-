import re
import glob

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We look for "vty_password=..." and then insert password_encryption_type string on the next line.
    # Note: test kwargs have `vty_password="...",\n            dhcp_network=`
    new_content = re.sub(
        r'(vty_password=.*?,\s*)(\s*dhcp_network=)',
        r'\g<1>\g<2>'.replace('\\g<2>', 'password_encryption_type="7",\n\\g<2>'),
        content
    )
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Patched {filepath}")

for path in glob.glob("tests/test_*.py"):
    patch_file(path)
