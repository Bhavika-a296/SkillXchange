"""
Force load the SkillMatch model when Django starts up.
This ensures the model is loaded immediately rather than on first request.
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

print("=" * 60)
print("FORCE LOADING SKILLMATCH MODEL...")
print("=" * 60)

from api.utils_safe import get_model

model = get_model(force_reload=True)
if model:
    print(f"✓ Model loaded successfully: {type(model)}")
else:
    print("✗ Model failed to load!")
    
print("=" * 60)
