import sys
import inspect

# -------- NODE ----------
class Node:
    def __init__(self, name, params):
        self.name = name
        self.params = params
        self.return_val = None
        self.children = []


# -------- TRACER ----------
class CallTracer:
    def __init__(self):
        self.call_stack = []
        self.root = None
        self.enabled = False

    def tracer(self, frame, event, arg):
        if not self.enabled:
            return

        func_name = frame.f_code.co_name

        # ignore internal/system calls
        if func_name.startswith("<"):
            return self.tracer

        if event == "call":
            arg_info = inspect.getargvalues(frame)
            params = {a: arg_info.locals[a] for a in arg_info.args}

            node = Node(func_name, params)

            if self.call_stack:
                self.call_stack[-1].children.append(node)
            else:
                self.root = node

            self.call_stack.append(node)

        elif event == "return":
            if self.call_stack:
                node = self.call_stack.pop()
                node.return_val = arg

        return self.tracer

    # -------- START ----------
    def start(self):
        self.enabled = True
        sys.settrace(self.tracer)

    # -------- END ----------
    def end(self):
        sys.settrace(None)
        self.enabled = False
        self.print_tree()

    # -------- PRINT ----------
    def print_tree(self, node=None, indent=0):
        if node is None:
            node = self.root
            print("\nCALL TRACE:\n")

        if node is None:
            print("No calls traced.")
            return

        space = "  " * indent
        param_str = ", ".join(f"{k}={v}" for k,v in node.params.items())
        print(f"{space}{node.name}({param_str}) -> {node.return_val}")

        for child in node.children:
            self.print_tree(child, indent+1)


# -------- GLOBAL INSTANCE ----------
trace = CallTracer()
