import json

with open('JSON Files/dibellas_nutrition.json', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's find why json.loads fails
try:
    data = json.loads(text)
    print("Direct parse success!")
except Exception as e:
    print(f"Error: {e}")
    # Let's count open/close braces
    open_b = text.count('{')
    close_b = text.count('}')
    print(f"Open braces: {open_b}, Close braces: {close_b}")
    open_sq = text.count('[')
    close_sq = text.count(']')
    print(f"Open brackets: {open_sq}, Close brackets: {close_sq}")
    
    # If braces mismatched, let's fix
    if open_b > close_b:
        text = text + ('}' * (open_b - close_b))
    elif close_b > open_b:
        # maybe extra closing brace
        pass
    
    try:
        data = json.loads(text)
        with open('JSON Files/dibellas_nutrition.json', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Fixed and saved dibellas!")
    except Exception as e2:
        print(f"Second attempt error: {e2}")
