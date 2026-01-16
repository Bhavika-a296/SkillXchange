"""
Initialize Django app and pre-load ML models
"""
# Removed: We'll load the model on-demand instead of at startup
# to avoid import issues during migrations and management commands