import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Testing Firebase Configuration")
print("=" * 40)

# Check .env file
if os.path.exists('.env'):
    print("✅ .env file exists")
    
    with open('.env', 'r') as f:
        content = f.read()
        
    if 'your_' in content or 'example' in content:
        print("❌ .env still has placeholder values!")
        print("   Please update with real values from Firebase Console")
    else:
        print("✅ .env appears to have real values")
else:
    print("❌ .env file not found")

# Check Firebase JSON
if os.path.exists('firebase/service-account.json'):
    print("✅ Firebase service account exists")
    
    # Check if it's the old compromised file
    with open('firebase/service-account.json', 'r') as f:
        content = f.read()
        
    if 'e8ef115421010bfc76e1952cd77b0948f847eeac' in content:
        print("❌❌❌ CRITICAL: OLD COMPROMISED KEY STILL PRESENT!")
        print("   DELETE THIS FILE IMMEDIATELY!")
        print("   Generate NEW key from Firebase Console")
    else:
        print("✅ Firebase service account appears to be new")
else:
    print("⚠️  Firebase service account not found")
    print("   Run: firebase/service-account.json")

print("=" * 40)
print("📝 Next steps:")
print("1. Regenerate ALL Firebase keys")
print("2. Update .env with new keys")
print("3. Download new service-account.json")
print("4. Run: python app.py")