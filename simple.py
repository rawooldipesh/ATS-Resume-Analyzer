import google.generativeai as genai

# Replace with your actual API key
genai.configure(api_key="AIzaSyCyWC7fM5bx2eK2Wx93XwfWsx-ZNt0ldRI")

# Use the correct model name
model = genai.GenerativeModel("gemini-1.5-pro")  # Use gemini-1.5-pro instead of gemini-pro

# Generate AI suggestions
response = model.generate_content("How can I improve my resume?")
print(response.text)
