import google.generativeai as genai

key = "AIzaSyB4q0W17OB2QbceYSCpEvhlZ58aW5k-4cc"
genai.configure(api_key=key)

print("Available models:")
for m in genai.list_models():
    print(f"- {m.name}")
