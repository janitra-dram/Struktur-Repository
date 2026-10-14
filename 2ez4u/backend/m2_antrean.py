import csv
from backend.m1_pesanan import Pesanan

class Stack:
    def __init__(self):
        self.items = []

    def push(self, val):
        self.items.append(val)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None

    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        return None

    def is_empty(self):
        return len(self.items) == 0

    @property
    def size(self):
        return len(self.items)

    def clear(self):
        self.items = []


def tokenize(expr):
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit():
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            tokens.append(expr[i:j])
            i = j
        elif c in "+-*/()":
            tokens.append(c)
            i += 1
        else:
            i += 1
    return tokens


def get_precedence(op):
    if op in ("*", "/"):
        return 2
    if op in ("+", "-"):
        return 1
    return 0


def infix_to_postfix(expr):
    tokens = tokenize(expr)
    stack = Stack()
    output = []
    steps = []

    for token in tokens:
        if token.isdigit():
            output.append(token)
            steps.append((token, "number, output directly", " ".join(stack.items), " ".join(output)))
        elif token == "(":
            stack.push(token)
            steps.append((token, "push (", " ".join(stack.items), " ".join(output)))
        elif token == ")":
            while not stack.is_empty() and stack.peek() != "(":
                output.append(stack.pop())
            if not stack.is_empty() and stack.peek() == "(":
                stack.pop()
            steps.append((token, "pop until (, discard (", " ".join(stack.items), " ".join(output)))
        elif token in "+-*/":
            actions = []
            while (not stack.is_empty() and stack.peek() != "(" and
                   get_precedence(stack.peek()) >= get_precedence(token)):
                op = stack.pop()
                output.append(op)
                actions.append(f"pop {op}")
            stack.push(token)
            actions.append(f"push {token}")
            steps.append((token, ", ".join(actions), " ".join(stack.items), " ".join(output)))

    while not stack.is_empty():
        op = stack.pop()
        output.append(op)
        steps.append(("end", f"pop {op}", " ".join(stack.items), " ".join(output)))

    return output, " ".join(output), steps


def evaluate_postfix(postfix_tokens):
    stack = Stack()
    steps = []

    for token in postfix_tokens:
        if token.isdigit():
            stack.push(int(token))
            steps.append((token, f"push {token}", " ".join(str(x) for x in stack.items)))
        elif token in "+-*/":
            b = stack.pop()
            a = stack.pop()
            if a is None or b is None:
                continue
            if token == "+":
                res = a + b
            elif token == "-":
                res = a - b
            elif token == "*":
                res = a * b
            elif token == "/":
                res = a // b if b != 0 else 0
            stack.push(res)
            steps.append((token, f"pop {b} and {a} -> {a} {token} {b} = {res}", " ".join(str(x) for x in stack.items)))

    total = stack.pop() if not stack.is_empty() else 0
    return total, steps


class NaiveQueue:
    def __init__(self):
        self.data = []
        self.total_shifts = 0

    @property
    def size(self):
        return len(self.data)

    def enqueue(self, item):
        self.data.append(item)

    def dequeue(self):
        if not self.data:
            return None, 0
        val = self.data[0]
        shifts = len(self.data) - 1
        for i in range(1, len(self.data)):
            self.data[i - 1] = self.data[i]
        self.data.pop()
        self.total_shifts += shifts
        return val, shifts

    def dequeue_batch(self, k):
        results = []
        batch_shifts = 0
        for _ in range(k):
            if not self.data:
                break
            val, s = self.dequeue()
            results.append(val)
            batch_shifts += s
        return results, batch_shifts

    def push_front_batch(self, items):
        self.data = list(items) + self.data

    def pop_rear(self):
        if self.data:
            return self.data.pop()
        return None

    def get(self, i):
        if 0 <= i < len(self.data):
            return self.data[i]
        return None

    # Aliases
    kembalikan_ke_depan = push_front_batch
    keluarkan_dari_belakang = pop_rear
    dequeue_banyak = dequeue_batch


class CircularQueue:
    def __init__(self, capacity=32768):
        self.capacity = capacity
        self.data = [None] * capacity
        self.front = 0
        self.rear = 0
        self.count = 0

    @property
    def size(self):
        return self.count

    def is_empty(self):
        return self.count == 0

    def is_full(self):
        return self.count == self.capacity

    def _resize(self, new_cap):
        new_data = [None] * new_cap
        for i in range(self.count):
            new_data[i] = self.data[(self.front + i) % self.capacity]
        self.data = new_data
        self.front = 0
        self.rear = self.count
        self.capacity = new_cap

    def enqueue(self, item):
        if self.is_full():
            self._resize(self.capacity * 2)
        self.data[self.rear] = item
        self.rear = (self.rear + 1) % self.capacity
        self.count += 1

    def dequeue(self):
        if self.is_empty():
            return None, 0
        val = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.count -= 1
        return val, 0

    def dequeue_batch(self, k):
        results = []
        for _ in range(k):
            if self.is_empty():
                break
            val, _ = self.dequeue()
            results.append(val)
        return results, 0

    def push_front_batch(self, items):
        for item in reversed(items):
            if self.is_full():
                self._resize(self.capacity * 2)
            self.front = (self.front - 1 + self.capacity) % self.capacity
            self.data[self.front] = item
            self.count += 1

    def pop_rear(self):
        if self.is_empty():
            return None
        self.rear = (self.rear - 1 + self.capacity) % self.capacity
        val = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return val

    def get(self, i):
        if 0 <= i < self.count:
            return self.data[(self.front + i) % self.capacity]
        return None

    # Aliases
    kembalikan_ke_depan = push_front_batch
    keluarkan_dari_belakang = pop_rear
    dequeue_banyak = dequeue_batch


def load_queue_csv(filepath):
    q_naive = NaiveQueue()
    q_circ = CircularQueue(32768)

    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            next(reader)
        except StopIteration:
            return q_naive, q_circ

        for row in reader:
            if not row or len(row) <= 8:
                continue
            status = row[8].strip()
            if status == "ANTRE":
                p = Pesanan(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4] if len(row) > 4 else 0,
                    row[5] if len(row) > 5 else 3,
                    row[6] if len(row) > 6 else 0,
                    row[7] if len(row) > 7 else 0,
                    status
                )
                q_naive.enqueue(p)
                q_circ.enqueue(p)

    return q_naive, q_circ


# Aliases
tokenisasi = tokenize
prioritas_operator = get_precedence
ke_postfix = infix_to_postfix
hitung_postfix = evaluate_postfix
AntreanNaif = NaiveQueue
AntreanMelingkar = CircularQueue
muat_antrean_csv = load_queue_csv
