import pathlib
import re

test_path = pathlib.Path('c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/test_whatsapp_gateway.py')
code = test_path.read_text(encoding='utf-8')

# Revert previous manual replacements or patch them cleanly
code = re.sub(r'(?<!def )get_session\("', 'get_session(MagicMock(), "', code)
code = re.sub(r'(?<!def )create_session\("', 'create_session(MagicMock(), "', code)
code = re.sub(r'(?<!def )save_session\("', 'save_session(MagicMock(), "', code)
code = re.sub(r'(?<!def )delete_session\("', 'delete_session(MagicMock(), "', code)

code = re.sub(r'handle_system_command\("', 'handle_system_command(MagicMock(), "', code)

test_path.write_text(code, encoding='utf-8')
print("Patched test_whatsapp_gateway.py with MagicMock() for db parameter")
