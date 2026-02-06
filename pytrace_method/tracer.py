import sys
import inspect
import threading
import json
import atexit
import os


# ---------- NODE ----------
class Node:
    def __init__(self, name, params, file):
        self.name = name
        self.params = params
        self.file = file
        self.return_val = None
        self.children = []


# ---------- TRACER ----------
class CallTracer:
    def __init__(self):
        self.call_stack = []
        self.root = None
        self.enabled = False
        self.save_file = None  # file path if saving enabled
        self.max_depth = 100  # prevent stack overflow
        self.exclude_patterns = ['site-packages', 'threading.py', 'atexit.py']
        self.max_param_len = 50  # max length for parameter display
        self.expand_objects = False  # whether to expand object details
        self.expand_depth = 2  # how deep to expand nested objects
        self.interactive_html = False  # whether to generate interactive HTML
        self.auto_end_registered = False
        self.trace_stdlib = False  # whether to trace standard library calls
        
        # Get Python's standard library path
        self.stdlib_path = os.path.dirname(os.__file__)

    # ---------- AUTO-END ON EXIT ----------
    def _register_auto_end(self):
        """Register automatic end on program exit"""
        if not self.auto_end_registered:
            atexit.register(self._auto_end)
            self.auto_end_registered = True

    def _auto_end(self):
        """Automatically end tracing when program exits"""
        if self.enabled:
            self.end()

    # ---------- ENABLE FILE SAVE ----------
    def save(self, filename="call_trace.txt"):
        """Enable saving trace to file"""
        self.save_file = filename
        self._register_auto_end()
        self.start()
        return self  # allow chaining

    # ---------- ENABLE INTERACTIVE HTML ----------
    def interactive(self, filename="call_trace.html"):
        """Enable interactive HTML output with collapsible objects"""
        self.interactive_html = True
        self.save_file = filename
        self._register_auto_end()
        self.start()
        return self

    # ---------- ENABLE OBJECT EXPANSION ----------
    def expand(self, depth=2):
        """Enable detailed object expansion"""
        self.expand_objects = True
        self.expand_depth = depth
        self._register_auto_end()
        self.start()
        return self  # allow chaining

    # ---------- INCLUDE STDLIB ----------
    def include_stdlib(self):
        """Include standard library calls in trace"""
        self.trace_stdlib = True
        return self

    # ---------- FORMAT VALUE ----------
    def _format_value(self, val, max_len=None, current_depth=0):
        """Format value for readable display"""
        if max_len is None:
            max_len = self.max_param_len
        
        # If expansion is enabled and we haven't exceeded depth
        if self.expand_objects and current_depth < self.expand_depth:
            return self._expand_object(val, current_depth)
        
        # Default behavior: simple repr with truncation
        s = repr(val)
        if len(s) > max_len:
            return s[:max_len] + "..."
        return s

    # ---------- EXPAND OBJECT ----------
    def _expand_object(self, obj, current_depth=0):
        """Recursively expand object details"""
        indent = "  " * current_depth
        next_indent = "  " * (current_depth + 1)
        
        # Handle None
        if obj is None:
            return "None"
        
        # Handle primitive types
        if isinstance(obj, (int, float, bool, str)):
            if isinstance(obj, str) and len(obj) > 100:
                return f"'{obj[:100]}...'"
            return repr(obj)
        
        # Handle lists
        if isinstance(obj, list):
            if not obj:
                return "[]"
            if current_depth >= self.expand_depth - 1:
                return f"[{len(obj)} items]"
            
            items = []
            for i, item in enumerate(obj[:10]):  # limit to first 10 items
                formatted = self._expand_object(item, current_depth + 1)
                items.append(f"{next_indent}[{i}]: {formatted}")
            
            if len(obj) > 10:
                items.append(f"{next_indent}... ({len(obj) - 10} more items)")
            
            return "[\n" + ",\n".join(items) + f"\n{indent}]"
        
        # Handle tuples
        if isinstance(obj, tuple):
            if not obj:
                return "()"
            if current_depth >= self.expand_depth - 1:
                return f"({len(obj)} items)"
            
            items = []
            for i, item in enumerate(obj[:10]):
                formatted = self._expand_object(item, current_depth + 1)
                items.append(f"{next_indent}[{i}]: {formatted}")
            
            if len(obj) > 10:
                items.append(f"{next_indent}... ({len(obj) - 10} more items)")
            
            return "(\n" + ",\n".join(items) + f"\n{indent})"
        
        # Handle dictionaries
        if isinstance(obj, dict):
            if not obj:
                return "{}"
            if current_depth >= self.expand_depth - 1:
                return f"{{{len(obj)} keys}}"
            
            items = []
            for i, (key, value) in enumerate(list(obj.items())[:10]):  # limit to first 10
                formatted_value = self._expand_object(value, current_depth + 1)
                items.append(f"{next_indent}{repr(key)}: {formatted_value}")
            
            if len(obj) > 10:
                items.append(f"{next_indent}... ({len(obj) - 10} more keys)")
            
            return "{\n" + ",\n".join(items) + f"\n{indent}}}"
        
        # Handle sets
        if isinstance(obj, set):
            if not obj:
                return "set()"
            if current_depth >= self.expand_depth - 1:
                return f"{{{len(obj)} items}}"
            return "{" + ", ".join(repr(item) for item in list(obj)[:10]) + "}"
        
        # Handle custom objects
        try:
            if hasattr(obj, '__dict__'):
                if current_depth >= self.expand_depth - 1:
                    return f"<{obj.__class__.__name__} object>"
                
                attrs = {}
                for key, value in obj.__dict__.items():
                    if not key.startswith('_'):  # skip private attributes
                        attrs[key] = self._expand_object(value, current_depth + 1)
                
                if not attrs:
                    return f"<{obj.__class__.__name__} object>"
                
                items = [f"{next_indent}{key}: {value}" for key, value in list(attrs.items())[:10]]
                return f"<{obj.__class__.__name__}>\n" + "\n".join(items) + f"\n{indent}"
        except:
            pass
        
        # Fallback to repr
        s = repr(obj)
        if len(s) > 200:
            return s[:200] + "..."
        return s

    # ---------- CONVERT TO JSON-SERIALIZABLE ----------
    def _to_serializable(self, obj, current_depth=0, max_depth=10):
        """Convert object to JSON-serializable format for interactive viewer"""
        if current_depth > max_depth:
            return {"type": "max_depth", "value": "..."}
        
        # Handle None
        if obj is None:
            return {"type": "null", "value": None}
        
        # Handle primitives
        if isinstance(obj, bool):
            return {"type": "boolean", "value": obj}
        if isinstance(obj, (int, float)):
            return {"type": "number", "value": obj}
        if isinstance(obj, str):
            return {"type": "string", "value": obj}
        
        # Handle lists
        if isinstance(obj, list):
            return {
                "type": "array",
                "length": len(obj),
                "value": [self._to_serializable(item, current_depth + 1, max_depth) for item in obj]
            }
        
        # Handle tuples
        if isinstance(obj, tuple):
            return {
                "type": "tuple",
                "length": len(obj),
                "value": [self._to_serializable(item, current_depth + 1, max_depth) for item in obj]
            }
        
        # Handle dictionaries
        if isinstance(obj, dict):
            return {
                "type": "object",
                "keys": list(obj.keys()),
                "value": {str(k): self._to_serializable(v, current_depth + 1, max_depth) for k, v in obj.items()}
            }
        
        # Handle sets
        if isinstance(obj, set):
            return {
                "type": "set",
                "length": len(obj),
                "value": [self._to_serializable(item, current_depth + 1, max_depth) for item in obj]
            }
        
        # Handle custom objects
        try:
            if hasattr(obj, '__dict__'):
                attrs = {k: self._to_serializable(v, current_depth + 1, max_depth) 
                        for k, v in obj.__dict__.items() if not k.startswith('_')}
                return {
                    "type": "custom",
                    "class": obj.__class__.__name__,
                    "value": attrs
                }
        except:
            pass
        
        # Fallback to string representation
        return {"type": "unknown", "value": str(obj)}

    # ---------- SHOULD IGNORE ----------
    def _should_ignore(self, file_name, func_name):
        """Check if call should be ignored"""
        # Ignore built-in functions (start with '<')
        if func_name.startswith("<"):
            return True
        
        # Ignore internal tracer methods
        if func_name in ['tracer', '_should_ignore', '_format_value', '_expand_object',
                         'start', 'end', '__enter__', '__exit__', 'expand', 'interactive',
                         'print_tree', 'write_to_file', '_write_tree', '_to_serializable',
                         'save', 'include_stdlib', '_node_to_dict', '_generate_html', 
                         '_register_auto_end', '_auto_end']:
            return True
        
        # Ignore patterns in file path
        if any(pattern in file_name for pattern in self.exclude_patterns):
            return True
        
        # Ignore standard library unless explicitly enabled
        if not self.trace_stdlib:
            # Check if file is in standard library
            if file_name.startswith(self.stdlib_path):
                return True
        
        return False

    # ---------- TRACER CORE ----------
    def tracer(self, frame, event, arg):
        if not self.enabled:
            return self.tracer

        func_name = frame.f_code.co_name
        file_name = frame.f_code.co_filename

        # ignore internal/system calls
        if self._should_ignore(file_name, func_name):
            return self.tracer

        # prevent stack overflow
        if len(self.call_stack) > self.max_depth:
            return None

        # ---------- FUNCTION CALL ----------
        if event == "call":
            frame.f_trace = self.tracer  # ⭐ critical for nested tracing

            arg_info = inspect.getargvalues(frame)
            
            # Store raw values for interactive mode
            if self.interactive_html:
                params = {a: arg_info.locals[a] for a in arg_info.args}
            else:
                params = {a: self._format_value(arg_info.locals[a]) for a in arg_info.args}

            node = Node(func_name, params, file_name)

            if self.call_stack:
                self.call_stack[-1].children.append(node)
            else:
                self.root = node

            self.call_stack.append(node)
            return self.tracer

        # ---------- FUNCTION RETURN ----------
        elif event == "return":
            if self.call_stack:
                node = self.call_stack.pop()
                if self.interactive_html:
                    node.return_val = arg
                else:
                    node.return_val = self._format_value(arg)

            return self.tracer

        return self.tracer

    # ---------- START TRACING ----------
    def start(self):
        if not self.enabled:  # Only start if not already enabled
            self.call_stack = []
            self.root = None
            self.enabled = True
            sys.settrace(self.tracer)
        return self  # allow chaining

    # ---------- END TRACING ----------
    def end(self):
        if not self.enabled:
            return
            
        sys.settrace(None)
        self.enabled = False

        if self.interactive_html:
            self._generate_html(self.save_file)
        else:
            self.print_tree()
            if self.save_file:
                self.write_to_file(self.save_file)
        
        # Reset settings for next trace
        self.expand_objects = False
        self.interactive_html = False
        self.trace_stdlib = False

    # ---------- CONTEXT MANAGER ----------
    def __enter__(self):
        """Enable use with 'with' statement"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically end tracing when exiting context"""
        self.end()
        return False  # don't suppress exceptions

    # ---------- PRINT TREE ----------
    def print_tree(self, node=None, indent=0):
        if node is None:
            node = self.root
            print("\nCALL TRACE:\n")

        if node is None:
            print("No calls traced.")
            return

        space = "  " * indent
        param_str = ", ".join(f"{k}={v}" for k, v in node.params.items())
        file_short = node.file.split("/")[-1]

        print(f"{space}{node.name}({param_str}) -> {node.return_val} [{file_short}]")

        for child in node.children:
            self.print_tree(child, indent + 1)

    # ---------- WRITE TO FILE ----------
    def write_to_file(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write("CALL TRACE:\n\n")
            self._write_tree(self.root, f)

    def _write_tree(self, node, file, indent=0):
        if node is None:
            file.write("No calls traced.\n")
            return

        space = "  " * indent
        param_str = ", ".join(f"{k}={v}" for k, v in node.params.items())
        file_short = node.file.split("/")[-1]

        file.write(f"{space}{node.name}({param_str}) -> {node.return_val} [{file_short}]\n")

        for child in node.children:
            self._write_tree(child, file, indent + 1)

    # ---------- NODE TO DICT ----------
    def _node_to_dict(self, node):
        """Convert node tree to dictionary for JSON serialization"""
        if node is None:
            return None
        
        return {
            "name": node.name,
            "file": node.file.split("/")[-1],
            "params": {k: self._to_serializable(v) for k, v in node.params.items()},
            "return_val": self._to_serializable(node.return_val),
            "children": [self._node_to_dict(child) for child in node.children]
        }

    # ---------- GENERATE HTML ----------
    def _generate_html(self, filename):
        """Generate interactive HTML with collapsible objects"""
        tree_data = self._node_to_dict(self.root)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Call Trace - Interactive</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            font-size: 14px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        h1 {{
            color: #4ec9b0;
            margin-bottom: 20px;
            font-size: 24px;
        }}
        
        .call-tree {{
            background: #252526;
            border-radius: 8px;
            padding: 20px;
        }}
        
        .call-node {{
            margin: 8px 0;
            margin-left: 20px;
        }}
        
        .call-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 10px;
            background: #2d2d30;
            border-radius: 4px;
            border-left: 3px solid #007acc;
            cursor: pointer;
            transition: background 0.2s;
        }}
        
        .call-header:hover {{
            background: #3e3e42;
        }}
        
        .toggle {{
            color: #858585;
            user-select: none;
            width: 16px;
            text-align: center;
        }}
        
        .func-name {{
            color: #dcdcaa;
            font-weight: bold;
        }}
        
        .params {{
            color: #9cdcfe;
        }}
        
        .return-arrow {{
            color: #858585;
            margin: 0 8px;
        }}
        
        .return-value {{
            color: #ce9178;
        }}
        
        .file {{
            color: #858585;
            font-size: 12px;
            margin-left: auto;
        }}
        
        .object-viewer {{
            margin: 10px 0 10px 40px;
            background: #1e1e1e;
            border-radius: 4px;
            padding: 10px;
            border-left: 2px solid #3e3e42;
        }}
        
        .object-viewer.collapsed {{
            display: none;
        }}
        
        .obj-line {{
            margin: 4px 0;
            display: flex;
            align-items: flex-start;
        }}
        
        .obj-key {{
            color: #9cdcfe;
            margin-right: 8px;
        }}
        
        .obj-value {{
            color: #ce9178;
        }}
        
        .obj-type {{
            color: #4ec9b0;
            font-style: italic;
        }}
        
        .obj-expand {{
            color: #858585;
            cursor: pointer;
            user-select: none;
            margin-right: 8px;
        }}
        
        .obj-expand:hover {{
            color: #d4d4d4;
        }}
        
        .obj-content {{
            margin-left: 20px;
        }}
        
        .obj-content.collapsed {{
            display: none;
        }}
        
        .primitive {{
            color: #b5cea8;
        }}
        
        .string {{
            color: #ce9178;
        }}
        
        .number {{
            color: #b5cea8;
        }}
        
        .boolean {{
            color: #569cd6;
        }}
        
        .null {{
            color: #569cd6;
        }}
        
        .children {{
            margin-left: 0px;
        }}
        
        .children.collapsed {{
            display: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Interactive Call Trace</h1>
        <div class="call-tree" id="callTree"></div>
    </div>

    <script>
        const traceData = {json.dumps(tree_data, indent=2)};
        
        function renderValue(value, key = null) {{
            if (!value) return '<span class="null">null</span>';
            
            const type = value.type;
            
            if (type === 'null') {{
                return '<span class="null">null</span>';
            }}
            
            if (type === 'string') {{
                const escaped = escapeHtml(value.value);
                return `<span class="string">"${{escaped}}"</span>`;
            }}
            
            if (type === 'number') {{
                return `<span class="number">${{value.value}}</span>`;
            }}
            
            if (type === 'boolean') {{
                return `<span class="boolean">${{value.value}}</span>`;
            }}
            
            if (type === 'array' || type === 'tuple') {{
                const id = 'obj_' + Math.random().toString(36).substr(2, 9);
                const typeName = type === 'tuple' ? 'tuple' : 'Array';
                let html = `<div class="obj-line">`;
                html += `<span class="obj-expand" onclick="toggleObj('${{id}}')">▶</span>`;
                html += `<span class="obj-type">${{typeName}}(${{value.length}})</span>`;
                html += `<div class="obj-content collapsed" id="${{id}}">`;
                
                value.value.forEach((item, i) => {{
                    html += `<div class="obj-line">`;
                    html += `<span class="obj-key">${{i}}:</span>`;
                    html += renderValue(item);
                    html += `</div>`;
                }});
                
                html += `</div></div>`;
                return html;
            }}
            
            if (type === 'object') {{
                const id = 'obj_' + Math.random().toString(36).substr(2, 9);
                let html = `<div class="obj-line">`;
                html += `<span class="obj-expand" onclick="toggleObj('${{id}}')">▶</span>`;
                html += `<span class="obj-type">Object(${{value.keys.length}})</span>`;
                html += `<div class="obj-content collapsed" id="${{id}}">`;
                
                for (const [k, v] of Object.entries(value.value)) {{
                    html += `<div class="obj-line">`;
                    html += `<span class="obj-key">${{k}}:</span>`;
                    html += renderValue(v);
                    html += `</div>`;
                }}
                
                html += `</div></div>`;
                return html;
            }}
            
            if (type === 'custom') {{
                const id = 'obj_' + Math.random().toString(36).substr(2, 9);
                let html = `<div class="obj-line">`;
                html += `<span class="obj-expand" onclick="toggleObj('${{id}}')">▶</span>`;
                html += `<span class="obj-type">${{value.class}}</span>`;
                html += `<div class="obj-content collapsed" id="${{id}}">`;
                
                for (const [k, v] of Object.entries(value.value)) {{
                    html += `<div class="obj-line">`;
                    html += `<span class="obj-key">${{k}}:</span>`;
                    html += renderValue(v);
                    html += `</div>`;
                }}
                
                html += `</div></div>`;
                return html;
            }}
            
            if (type === 'set') {{
                const id = 'obj_' + Math.random().toString(36).substr(2, 9);
                let html = `<div class="obj-line">`;
                html += `<span class="obj-expand" onclick="toggleObj('${{id}}')">▶</span>`;
                html += `<span class="obj-type">Set(${{value.length}})</span>`;
                html += `<div class="obj-content collapsed" id="${{id}}">`;
                
                value.value.forEach((item, i) => {{
                    html += `<div class="obj-line">`;
                    html += renderValue(item);
                    html += `</div>`;
                }});
                
                html += `</div></div>`;
                return html;
            }}
            
            return `<span class="obj-value">${{escapeHtml(String(value.value))}}</span>`;
        }}
        
        function renderNode(node, level = 0) {{
            if (!node) return '';
            
            const nodeId = 'node_' + Math.random().toString(36).substr(2, 9);
            const childrenId = 'children_' + Math.random().toString(36).substr(2, 9);
            const paramsId = 'params_' + Math.random().toString(36).substr(2, 9);
            
            let html = `<div class="call-node">`;
            
            // Call header
            html += `<div class="call-header" onclick="toggleNode('${{childrenId}}', '${{paramsId}}', this)">`;
            html += `<span class="toggle">▼</span>`;
            html += `<span class="func-name">${{node.name}}()</span>`;
            html += `<span class="return-arrow">→</span>`;
            html += `<span class="return-value">${{getValuePreview(node.return_val)}}</span>`;
            html += `<span class="file">[${{node.file}}]</span>`;
            html += `</div>`;
            
            // Parameters viewer
            if (Object.keys(node.params).length > 0) {{
                html += `<div class="object-viewer" id="${{paramsId}}">`;
                html += `<div style="color: #4ec9b0; margin-bottom: 8px; font-weight: bold;">Parameters:</div>`;
                for (const [key, value] of Object.entries(node.params)) {{
                    html += `<div class="obj-line">`;
                    html += `<span class="obj-key">${{key}}:</span>`;
                    html += renderValue(value);
                    html += `</div>`;
                }}
                html += `</div>`;
            }}
            
            // Children
            if (node.children && node.children.length > 0) {{
                html += `<div class="children" id="${{childrenId}}">`;
                node.children.forEach(child => {{
                    html += renderNode(child, level + 1);
                }});
                html += `</div>`;
            }}
            
            html += `</div>`;
            return html;
        }}
        
        function getValuePreview(value) {{
            if (!value) return 'null';
            
            const type = value.type;
            
            if (type === 'null') return 'null';
            if (type === 'string') return `"${{value.value.substring(0, 30)}}${{value.value.length > 30 ? '...' : ''}}"`;
            if (type === 'number') return String(value.value);
            if (type === 'boolean') return String(value.value);
            if (type === 'array') return `Array(${{value.length}})`;
            if (type === 'tuple') return `tuple(${{value.length}})`;
            if (type === 'object') return `Object(${{value.keys.length}})`;
            if (type === 'custom') return value.class;
            if (type === 'set') return `Set(${{value.length}})`;
            
            return String(value.value).substring(0, 30);
        }}
        
        function toggleNode(childrenId, paramsId, header) {{
            const children = document.getElementById(childrenId);
            const params = document.getElementById(paramsId);
            const toggle = header.querySelector('.toggle');
            
            if (children) {{
                children.classList.toggle('collapsed');
            }}
            if (params) {{
                params.classList.toggle('collapsed');
            }}
            
            toggle.textContent = toggle.textContent === '▼' ? '▶' : '▼';
        }}
        
        function toggleObj(id) {{
            const el = document.getElementById(id);
            const toggle = el.previousElementSibling;
            
            el.classList.toggle('collapsed');
            toggle.textContent = toggle.textContent === '▶' ? '▼' : '▶';
        }}
        
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        // Render the tree
        document.getElementById('callTree').innerHTML = renderNode(traceData);
    </script>
</body>
</html>"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n✓ Interactive trace saved to {filename}")
        print(f"  Open it in your browser to explore the call tree!")


# ---------- GLOBAL INSTANCE ----------
trace = CallTracer()
