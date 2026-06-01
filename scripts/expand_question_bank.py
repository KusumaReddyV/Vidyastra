"""Generate expanded local question bank (run once: python scripts/expand_question_bank.py)."""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "question_bank.json"

TOPICS = {
    "python": {
        "easy": [
            ("What keyword defines a function in Python?", ["func", "def", "function", "lambda"], "def"),
            ("Which type is mutable?", ["tuple", "str", "list", "int"], "list"),
            ("Which symbol starts a comment?", ["//", "#", "--", "/*"], "#"),
            ("What is the output type of len([1,2,3])?", ["str", "int", "float", "list"], "int"),
            ("Which method adds an item to a list?", ["push", "add", "append", "insert_only"], "append"),
        ],
        "medium": [
            ("What does list comprehension create?", ["A loop", "A new list", "A tuple only", "A dict"], "A new list"),
            ("Which keyword handles exceptions?", ["catch", "except", "error", "handle"], "except"),
            ("What is a decorator?", ["A variable", "A function wrapping another", "A class only", "A module"], "A function wrapping another"),
            ("Which module is used for JSON?", ["pickle", "json", "marshal", "csv"], "json"),
            ("What does *args collect?", ["Keyword args", "Positional args", "Global vars", "Classes"], "Positional args"),
        ],
        "hard": [
            ("What does GIL stand for?", ["Global Interpreter Lock", "General Interface Loop", "Graph IO Layer", "Global IO Lock"], "Global Interpreter Lock"),
            ("Which protocol do context managers use?", ["__iter__/__next__", "__enter__/__exit__", "__call__", "__new__"], "__enter__/__exit__"),
            ("What is a generator?", ["A list", "An iterator from yield", "A thread", "A decorator only"], "An iterator from yield"),
            ("Which is true about sets?", ["Ordered duplicates", "Unordered unique elements", "Mutable keys", "Indexed access"], "Unordered unique elements"),
            ("What does asyncio provide?", ["Sync IO", "Concurrent IO model", "Only threading", "Only multiprocessing"], "Concurrent IO model"),
        ],
    },
    "javascript": {
        "easy": [
            ("Which declares block-scoped variable?", ["var", "let", "define", "const_only"], "let"),
            ("typeof [] in JavaScript?", ["array", "object", "list", "undefined"], "object"),
            ("Which compares value and type?", ["==", "=", "===", "!="], "==="),
            ("DOM method to select by id?", ["getElement", "queryById", "getElementById", "selectId"], "getElementById"),
            ("Array method to iterate?", ["map", "forEach", "Both map and forEach", "Neither"], "Both map and forEach"),
        ],
        "medium": [
            ("What is a closure?", ["A CSS class", "Function with lexical env", "A loop", "A promise"], "Function with lexical env"),
            ("Promise state not included?", ["pending", "settled", "fulfilled", "rejected"], "settled"),
            ("Event loop handles?", ["Sync stack only", "Async callbacks", "CSS", "SQL"], "Async callbacks"),
            ("spread operator does?", ["Copies/enumerates iterable", "Deletes keys", "Throws error", "Locks thread"], "Copies/enumerates iterable"),
            ("JSON.parse expects?", ["XML string", "Valid JSON string", "HTML", "Binary"], "Valid JSON string"),
        ],
        "hard": [
            ("Prototype chain used for?", ["Styling", "Inheritance", "Networking", "Parsing"], "Inheritance"),
            ("WeakMap keys must be?", ["Strings only", "Objects", "Numbers only", "Symbols only"], "Objects"),
            ("Temporal dead zone relates to?", ["let/const hoisting", "var only", "functions", "classes in C++"], "let/const hoisting"),
            ("Microtasks run when?", ["Before next macrotask", "After paint always", "Never", "Only on load"], "Before next macrotask"),
            ("Module type in script tag?", ["module", "es6", "import", "package"], "module"),
        ],
    },
    "flask": {
        "easy": [
            ("Flask is a?", ["Database", "Python web framework", "Browser", "OS"], "Python web framework"),
            ("Default Flask template engine?", ["Jinja2", "Mako", "Django", "React"], "Jinja2"),
            ("Route decorator in Flask?", ["@app.route", "@flask.url", "@path", "@http.get"], "@app.route"),
            ("How to return JSON?", ["jsonify", "to_json", "return_json", "dump_html"], "jsonify"),
            ("Development server run?", ["flask run", "python manage.py", "npm start", "gunicorn dev"], "flask run"),
        ],
        "medium": [
            ("Blueprint purpose?", ["Modular routes", "Database ORM", "Caching only", "Auth only"], "Modular routes"),
            ("request object holds?", ["HTTP request data", "DB connection", "Template cache", "Config file"], "HTTP request data"),
            ("session requires?", ["Secret key", "Redis only", "Docker", "GraphQL"], "Secret key"),
            ("g object is?", ["Request-global proxy", "Graph DB", "Gateway", "Generator"], "Request-global proxy"),
            ("before_request runs?", ["Before each request handler", "After response", "On shutdown only", "Never"], "Before each request handler"),
        ],
        "hard": [
            ("Application factory pattern helps?", ["Testing & config flexibility", "Faster CSS", "SQL only", "No blueprints"], "Testing & config flexibility"),
            ("WSGI stands for?", ["Web Server Gateway Interface", "Web Socket Global IO", "Wide Secure Gateway", "Web Static Gateway"], "Web Server Gateway Interface"),
            ("Flask-Login manages?", ["User session auth", "SQL migrations", "Redis cluster", "Webpack"], "User session auth"),
            ("url_for generates?", ["URL for endpoint", "SQL query", "JWT", "PDF"], "URL for endpoint"),
            ("Production server often?", ["Gunicorn/uWSGI", "Flask dev only", "Apache only", "None"], "Gunicorn/uWSGI"),
        ],
    },
    "dbms": {
        "easy": [
            ("SQL stands for?", ["Structured Query Language", "Simple Query", "Standard Queue", "System Query"], "Structured Query Language"),
            ("Filter rows with?", ["WHERE", "FILTER", "HAVING only", "SELECT"], "WHERE"),
            ("Primary key is?", ["Unique row identifier", "Foreign link", "Index name", "View"], "Unique row identifier"),
            ("DELETE removes?", ["Rows", "Database only", "Columns only", "Indexes only"], "Rows"),
            ("COUNT(*) returns?", ["Number of rows", "Sum of values", "Average", "Schema"], "Number of rows"),
        ],
        "medium": [
            ("Normalization reduces?", ["Redundancy", "Security", "Speed always", "Users"], "Redundancy"),
            ("INNER JOIN returns?", ["Matching rows both sides", "All left rows", "Cartesian only", "No rows"], "Matching rows both sides"),
            ("ACID: A stands for?", ["Atomicity", "Availability", "Association", "Audit"], "Atomicity"),
            ("Index speeds up?", ["Reads/lookups", "All writes only", "Deletes only", "Nothing"], "Reads/lookups"),
            ("Foreign key ensures?", ["Referential integrity", "Encryption", "Replication", "Sharding"], "Referential integrity"),
        ],
        "hard": [
            ("2PL prevents?", ["Some anomalies via locking", "All deadlocks always", "Indexes", "Views"], "Some anomalies via locking"),
            ("B+ tree used in?", ["Indexes", "Only logs", "Only triggers", "Only views"], "Indexes"),
            ("Deadlock detection uses?", ["Wait-for graph", "Only timeouts", "Only backups", "Only triggers"], "Wait-for graph"),
            ("MVCC helps?", ["Concurrent reads/writes", "Only backups", "Only deletes", "Only inserts"], "Concurrent reads/writes"),
            ("Sharding is?", ["Horizontal partition", "Vertical only", "Backup", "View"], "Horizontal partition"),
        ],
    },
    "sql": {
        "easy": [
            ("Select columns with?", ["SELECT", "GET", "COLUMNS", "SHOW"], "SELECT"),
            ("Sort results?", ["ORDER BY", "SORT", "GROUP", "RANK"], "ORDER BY"),
            ("Aggregate with GROUP BY needs?", ["Often HAVING for filter", "Always WHERE on aggregate", "No rules", "Only JOIN"], "Often HAVING for filter"),
            ("DISTINCT does?", ["Removes duplicate rows", "Sorts", "Joins", "Indexes"], "Removes duplicate rows"),
            ("LIKE is for?", ["Pattern matching", "Math", "Joins", "Locks"], "Pattern matching"),
        ],
        "medium": [
            ("Window function example?", ["ROW_NUMBER", "PRIMARY KEY", "FOREIGN KEY", "CHECK"], "ROW_NUMBER"),
            ("Subquery in WHERE is?", ["Nested SELECT", "Only JOIN", "Only VIEW", "TRIGGER"], "Nested SELECT"),
            ("UNION combines?", ["Result sets", "Tables physically", "Indexes", "Schemas"], "Result sets"),
            ("COALESCE returns?", ["First non-null", "Always null", "Max value", "Count"], "First non-null"),
            ("EXPLAIN shows?", ["Query plan", "Password", "Users", "Triggers only"], "Query plan"),
        ],
        "hard": [
            ("CTE with keyword?", ["WITH", "AS OF", "TEMP", "CTE"], "WITH"),
            ("Correlated subquery?", ["References outer query", "Never runs", "Only in INSERT", "Only DELETE"], "References outer query"),
            ("Isolation serializable?", ["Strictest isolation", "Weakest", "Default everywhere", "No transactions"], "Strictest isolation"),
            ("Covering index?", ["Includes queried columns", "Only PK", "Only FK", "No index"], "Includes queried columns"),
            ("N+1 problem in ORMs?", ["Many queries per loop", "One query only", "No joins ever", "Only views"], "Many queries per loop"),
        ],
    },
    "dsa": {
        "easy": [
            ("Binary search complexity?", ["O(log n)", "O(n)", "O(n^2)", "O(1)"], "O(log n)"),
            ("Stack is?", ["LIFO", "FIFO", "Random", "Sorted"], "LIFO"),
            ("Queue is?", ["FIFO", "LIFO", "Tree", "Graph"], "FIFO"),
            ("Array access by index?", ["O(1)", "O(log n)", "O(n^2)", "O(n log n)"], "O(1)"),
            ("Linked list insert at head?", ["O(1)", "O(n^2)", "O(log n)", "O(n log n)"], "O(1)"),
        ],
        "medium": [
            ("BFS uses?", ["Queue", "Stack only", "Heap only", "Hash only"], "Queue"),
            ("DFS uses?", ["Stack/recursion", "Queue only", "Sort", "Greedy only"], "Stack/recursion"),
            ("Hash collision handled by?", ["Chaining/open addressing", "Deleting table", "Only sort", "Only BFS"], "Chaining/open addressing"),
            ("Heap property?", ["Parent-child order", "Sorted array", "FIFO", "LIFO only"], "Parent-child order"),
            ("Merge sort complexity?", ["O(n log n)", "O(n^2)", "O(n)", "O(1)"], "O(n log n)"),
        ],
        "hard": [
            ("Dijkstra needs?", ["Non-negative weights", "Negative cycles", "Unsorted graph only", "No graph"], "Non-negative weights"),
            ("DP optimal substructure?", ["Subproblems compose solution", "Always greedy", "Never overlapping", "No memo"], "Subproblems compose solution"),
            ("Trie used for?", ["Prefix strings", "Sorting only", "Graph shortest path", "Hash only"], "Prefix strings"),
            ("Topological sort on?", ["DAG", "Any graph", "Tree only", "Cycle"], "DAG"),
            ("Red-black tree ensures?", ["Approx balance", "Always complete", "No rotations", "O(1) search"], "Approx balance"),
        ],
    },
    "os": {
        "easy": [
            ("OS manages?", ["Hardware resources", "Only browsers", "Only compilers", "Only networks"], "Hardware resources"),
            ("Process is?", ["Program in execution", "A file", "A thread only", "A driver"], "Program in execution"),
            ("Thread shares?", ["Address space of process", "Nothing", "Only disk", "Only CPU id"], "Address space of process"),
            ("CPU scheduling decides?", ["Which process runs", "File names", "IP address", "UI theme"], "Which process runs"),
            ("Paging uses?", ["Disk as virtual memory", "Only cache", "Only registers", "Only GPU"], "Disk as virtual memory"),
        ],
        "medium": [
            ("Mutex is for?", ["Mutual exclusion", "Memory allocation", "File delete", "DNS"], "Mutual exclusion"),
            ("Deadlock needs?", ["Circular wait among resources", "Only one process", "No locks", "Only SSD"], "Circular wait among resources"),
            ("Thrashing means?", ["Excessive paging", "Fast CPU", "No I/O", "High cache hit"], "Excessive paging"),
            ("Semaphore can?", ["Signal/wait", "Only read files", "Only compile", "Only draw UI"], "Signal/wait"),
            ("Context switch saves?", ["CPU state", "Only RAM size", "Only disk", "Only user name"], "CPU state"),
        ],
        "hard": [
            ("Banker's algorithm?", ["Deadlock avoidance", "Page replacement", "Scheduling FCFS", "File allocation"], "Deadlock avoidance"),
            ("LRU approximates?", ["Recent use for pages", "FIFO only", "Random only", "No replacement"], "Recent use for pages"),
            ("Kernel mode allows?", ["Privileged instructions", "Only user apps", "Only CSS", "Only HTML"], "Privileged instructions"),
            ("Copy-on-write used in?", ["fork optimization", "Only disks", "Only NIC", "Only GPU"], "fork optimization"),
            ("Spooling relates to?", ["I/O queueing", "CPU only", "RAM only", "UI only"], "I/O queueing"),
        ],
    },
    "aptitude": {
        "easy": [
            ("25% of 200?", ["25", "50", "75", "100"], "50"),
            ("Next: 2,4,8,16,?", ["24", "32", "20", "18"], "32"),
            ("Average of 10 and 30?", ["15", "20", "25", "40"], "20"),
            ("If A>B and B>C then?", ["A>C", "C>A", "A=C", "None"], "A>C"),
            ("Days in leap year?", ["365", "366", "364", "367"], "366"),
        ],
        "medium": [
            ("Profit 20% on cost 500?", ["100", "80", "120", "600"], "100"),
            ("Speed 60km/h for 2h distance?", ["30", "120", "60", "90"], "120"),
            ("Ratio 3:5 total 40 first part?", ["15", "25", "10", "20"], "15"),
            ("Compound: principal matters for?", ["Interest growth", "Only color", "Only spelling", "Only font"], "Interest growth"),
            ("Clock 90° hour hand moves?", ["3 hours", "2 hours", "1 hour", "6 hours"], "3 hours"),
        ],
        "hard": [
            ("Permutation P(5,2)?", ["20", "10", "25", "15"], "20"),
            ("Probability fair coin 3 heads?", ["1/8", "1/4", "1/2", "3/8"], "1/8"),
            ("Work: A 6 days alone, together?", ["Depends on B", "Always 3", "Always 6", "Always 1"], "Depends on B"),
            ("Mixture 30% acid 10L pure acid add?", ["Conceptual", "0L", "Always 5L", "Always 10L"], "Conceptual"),
            ("Series sum 1+2+...+10?", ["55", "45", "50", "60"], "55"),
        ],
    },
}


def expand_templates(templates, topic, level, target=28):
    out = []
    for i, (q, opts, ans) in enumerate(templates):
        out.append({
            "id": f"{topic[:3]}-{level[0]}-{i+1}",
            "type": "mcq",
            "question": q,
            "options": opts,
            "answer": ans,
            "explanation": f"Review {topic} fundamentals at {level} level.",
        })
    # duplicate variants with suffix for volume
    base_len = len(out)
    idx = 0
    while len(out) < target:
        src = out[idx % base_len]
        n = len(out) + 1
        out.append({
            **src,
            "id": f"{topic[:3]}-{level[0]}-x{n}",
            "question": src["question"] + f" (Practice {n})",
        })
        idx += 1
    return out[:target]


def main():
    bank = {}
    for topic, levels in TOPICS.items():
        bank[topic] = {}
        for level, templates in levels.items():
            bank[topic][level] = expand_templates(templates, topic, level, target=28)
    OUT.write_text(json.dumps(bank, indent=2), encoding="utf-8")
    total = sum(len(bank[t][l]) for t in bank for l in bank[t])
    print(f"Wrote {OUT} with {total} questions across {len(bank)} topics")


if __name__ == "__main__":
    main()
