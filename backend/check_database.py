#!/usr/bin/env python
"""
Simple script to check database entries and verify user login
Run with: python check_database.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import UserProfile, Skill, Message, Connection

print("=" * 60)
print("USER LOGIN VERIFICATION")
print("=" * 60)

# Check for Anish_Nale user
username_to_check = "Anish_Nale"
user = User.objects.filter(username=username_to_check).first()

if user:
    print(f"\n✅ User '{username_to_check}' EXISTS")
    print(f"   - ID: {user.id}")
    print(f"   - Email: {user.email}")
    print(f"   - Is active: {user.is_active}")
    print(f"   - Has usable password: {user.has_usable_password()}")
    
    # Test password
    test_password = "bh123456"
    password_valid = user.check_password(test_password)
    print(f"   - Password 'bh123456' valid: {password_valid}")
    
    if not password_valid:
        print("\n⚠️ PASSWORD MISMATCH!")
        print("   Resetting password to 'bh123456'...")
        user.set_password(test_password)
        user.save()
        print("   ✅ Password reset complete. Try logging in again.")
else:
    print(f"\n❌ User '{username_to_check}' NOT FOUND")
    print("\nAvailable users:")
    for u in User.objects.all():
        print(f"   - {u.username}")

print("\n" + "=" * 60)
print("DATABASE CONTENTS")
print("=" * 60)

# Check Users
users = User.objects.all()
print(f"\n📊 USERS ({users.count()}):")
print("-" * 60)
for user in users:
    print(f"  ✓ {user.username} ({user.email})")
    print(f"    - ID: {user.id}")
    print(f"    - Date joined: {user.date_joined.strftime('%Y-%m-%d %H:%M')}")
    
    # Check UserProfile
    try:
        profile = UserProfile.objects.get(user=user)
        print(f"    - Profile: Bio={profile.bio[:50] if profile.bio else 'None'}...")
    except UserProfile.DoesNotExist:
        print(f"    - Profile: Not created")
    print()

# Check Skills
skills = Skill.objects.all()
print(f"\n🎯 SKILLS ({skills.count()}):")
print("-" * 60)
for skill in skills[:10]:  # Show first 10
    print(f"  ✓ {skill.name} - {skill.user.username} (Level: {skill.proficiency_level})")

# Check Messages
messages = Message.objects.all()
print(f"\n💬 MESSAGES ({messages.count()}):")
print("-" * 60)
for msg in messages[:10]:  # Show first 10
    content_preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
    print(f"  ✓ {msg.sender.username} → {msg.receiver.username}: {content_preview}")
    print(f"    - Time: {msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"    - Read: {msg.read}")

# Check Connections
connections = Connection.objects.all()
print(f"\n🔗 CONNECTIONS ({connections.count()}):")
print("-" * 60)
for conn in connections:
    print(f"  ✓ {conn.requester.username} → {conn.receiver.username}")
    print(f"    - Status: {conn.status}")
    print(f"    - Created: {conn.created_at.strftime('%Y-%m-%d %H:%M')}")

print("\n" + "=" * 60)
print("END OF DATABASE REPORT")
print("=" * 60)
