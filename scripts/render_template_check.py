import os
import django
from django.template.loader import render_to_string
from django.template import TemplateSyntaxError, TemplateDoesNotExist

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
try:
    # Ensure project root is on sys.path so 'core' module can be imported
    import sys
    project_root = os.getcwd()
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    django.setup()
except Exception as e:
    print('Django setup error:', e)
    raise

ctx = {'components': [], 'business': {}}

for name in ('nexus_preview.html', 'storefront/nexus_preview.html'):
    try:
        s = render_to_string(name, ctx)
        print('Rendered', name, 'OK. length:', len(s))
        break
    except TemplateSyntaxError as e:
        print('TEMPLATE SYNTAX ERROR for', name, ':', e)
    except TemplateDoesNotExist as e:
        print('TemplateDoesNotExist:', e)
    except Exception as e:
        print('Error rendering', name, ':', e)
