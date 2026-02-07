# 🔍 pytrace-method

**Trace every function call. Visualize execution. Debug faster.**

`pytrace-method` is a lightweight Python tracing utility that records
function calls, parameters, return values, and call flow --- then
generates an interactive HTML report to visualize execution.

Perfect for debugging complex codebases, understanding execution flow,
and teaching how programs run internally.

------------------------------------------------------------------------

## ✨ Features

-   📌 Trace function & method calls automatically\
-   📥 Capture parameters passed to functions\
-   📤 Capture return values\
-   🧠 Understand nested and object method calls\
-   🌐 Generate interactive HTML call reports\
-   ⚡ Minimal setup, easy integration\
-   🪶 Lightweight with no heavy dependencies

------------------------------------------------------------------------

## 📦 Installation

``` bash
pip install pytrace-method
```

------------------------------------------------------------------------

## 🚀 Quick Start

### Basic Example

``` python
from pytrace_method.tracer import trace

def greet(name):
    return f"Hello {name}"

trace.interactive("trace_output.html")  # HTML output file
trace.start()

greet("Chaitanya")

trace.end()
```

After running, open **trace_output.html** in your browser to view the
execution trace.

------------------------------------------------------------------------

## 🧩 Example with Objects & Methods

``` python
from pytrace_method.tracer import trace

class User:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return self.say_hello()

    def say_hello(self):
        return f"Hello {self.name}"

def process_user(user):
    return user.greet()

trace.interactive("user_trace.html")
trace.start()

u = User("Chaitanya")
process_user(u)

trace.end()
```

The generated HTML will show: - Function call hierarchy\
- Object method calls\
- Parameters passed\
- Return values

------------------------------------------------------------------------

## 📊 Output

The HTML report includes:

-   Structured call trace\
-   Nested call visualization\
-   Parameters and return values\
-   Clean readable format

Great for: - Debugging large systems\
- Understanding legacy code\
- Teaching programming flow\
- Interview preparation

------------------------------------------------------------------------

## ⚙️ How It Works

`pytrace-method` hooks into Python execution and logs:

-   Function calls\
-   Method calls\
-   Arguments\
-   Return values\
-   Call hierarchy

It then generates a readable interactive HTML trace file.

------------------------------------------------------------------------

## 💡 Use Cases

-   Debug complex nested calls\
-   Visualize execution flow\
-   Teaching Python internals\
-   Performance understanding\
-   Code auditing

------------------------------------------------------------------------

## 🛠️ Contributing

Contributions are welcome!

1.  Fork the repo\
2.  Create your feature branch\
3.  Commit changes\
4.  Push and open PR

------------------------------------------------------------------------

## 🧑‍💻 Author

**Chaitanya**

GitHub: https://github.com/Chaitu5210

------------------------------------------------------------------------

## 📜 License

MIT License

------------------------------------------------------------------------

## ⭐ Support

If this project helps you:

-   ⭐ Star the repo\
-   🐛 Report issues\
-   💡 Suggest features\
-   🤝 Contribute

Happy Debugging 🚀
