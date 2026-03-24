with open("main.py", "r", encoding="utf-8-sig") as f:
    content = f.read()

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)