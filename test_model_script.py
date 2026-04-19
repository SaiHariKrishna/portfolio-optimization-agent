import google.generativeai as genai
genai.configure(api_key='AIzaSyA63ddy-pLRjCd6I6FOSx1TG_1RdEmqVe0')
try:
    with open('test_models.txt', 'w') as f:
        m = genai.GenerativeModel('models/gemini-2.5-flash')
        f.write("2.5 flash: " + m.generate_content('hi').text[:20] + "\n")
        m2 = genai.GenerativeModel('models/gemini-flash-latest')
        f.write("flash latest: " + m2.generate_content('hi').text[:20])
except Exception as e:
    with open('test_models.txt', 'w') as f:
        f.write(f"Error: {str(e)}")
