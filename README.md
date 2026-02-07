# 🔍 pytrace-method

> Trace every function call. Visualize execution. Debug faster.

`pytrace-method` is a lightweight Python developer tool that traces function calls, parameters, return values, and execution flow — then generates beautiful interactive HTML or clean text reports.

Built for developers who want to **understand code execution clearly**, debug faster, and visualize how functions interact internally.

---

# ✨ Why pytrace-method?

Debugging large codebases or understanding nested function calls can be painful.

This library helps you:

* See which function called which
* Track parameters passed
* View return values
* Understand nested execution flow
* Generate clean visual HTML trace reports

Perfect for:

* Debugging complex logic
* Understanding legacy code
* Teaching Python execution flow
* Interview preparation
* Developer tooling enthusiasts

---

# ⚡ Installation

```bash
pip install pytrace-method
```

---

# 🚀 Quick Start (HTML Interactive Trace)

```python
from pytrace_method import trace

def add(a, b):
    return a + b

def multiply(x, y):
    return x * y

def calculate_total(num1, num2):
    sum_result = add(num1, num2)
    final_result = multiply(sum_result, 2)
    return final_result

def main():
    a = 5
    b = 3
    result = calculate_total(a, b)
    print("Final result:", result)

trace.interactive("trace.html")   # Generate interactive HTML
trace.start()

main()

trace.end()
```

Open `trace.html` in browser → see full execution flow visually.

---

# 🧾 Text Output Trace (Terminal/File)

You can also save call trace to a text file.

```python
from pytrace_method import trace

trace.save("trace.txt")   # Save to text file
trace.start()

main()

trace.end()
```

Example output:

```
CALL TRACE:

main() => None
  calculate_total(num1=5, num2=3) => 16
    add(a=5, b=3) => 8
    multiply(x=8, y=2) => 16
```

---

# 📸 Visual Examples

## 🧩 Sample Python Code

Simple connected functions used for tracing.

![Code Example](PASTE_IMAGE_LINK_HERE)

---

## 🌐 Interactive HTML Call Trace

Beautiful nested visualization with:

* Parameters
* Return values
* File references
* Call hierarchy

![HTML Output](PASTE_IMAGE_LINK_HERE)

---

## 🖥️ Terminal/Text Output

Clean readable trace in terminal or `.txt` file.

![Text Output](PASTE_IMAGE_LINK_HERE)

---

# 🧠 Features

* Trace function calls automatically
* Supports nested calls
* Tracks parameters & return values
* Works with objects and methods
* Interactive HTML visualization
* Text/terminal output support
* Zero complex setup
* Lightweight & fast

---

# 🛠️ Use Cases

### 🐞 Debugging

Understand exactly where logic breaks.

### 🧑‍🏫 Teaching

Show students how functions execute internally.

### 🧠 Code Understanding

Visualize flow of unfamiliar codebases.

### ⚙️ Developer Tools

Useful for building debugging/analysis tools.

---

# 🧪 Works With

* Functions
* Nested calls
* Classes & objects
* Large codebases
* Any Python project

---

# 🗺️ Roadmap

Planned features:

* Call time profiling
* Export to JSON
* VSCode extension
* Flask/Django tracing
* Decorator-based tracing
* Call graph visualization

---

# 🤝 Contributing

Contributions welcome.

1. Fork repo
2. Create feature branch
3. Commit changes
4. Open PR

---

# 👨‍💻 Author

**Chaitanya**
Developer • Builder • Tooling Enthusiast

GitHub: [https://github.com/Chaitu5210](https://github.com/Chaitu5210)
Email: [chaitanyarudraraju5210@gmail.com](mailto:chaitanyarudraraju5210@gmail.com)

If you're interested in collaborating on projects or need help, feel free to reach out.

---

# 📜 License

MIT License

---

# ⭐ Support

If this project helps you:

* ⭐ Star the repo
* 🐛 Report issues
* 💡 Suggest features
* 🚀 Share with developers

**Build tools. Help developers. Ship fast.**
