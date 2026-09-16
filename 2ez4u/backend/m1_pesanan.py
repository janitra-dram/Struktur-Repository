class Array:
    def __init__(self, capacity=4):
        self.capacity = capacity
        self.size = 0
        self.data = [None] * self.capacity

    def get(self, i):
        if 0 <= i < self.size:
            return self.data[i]
        raise IndexError("Index out of bounds")

    def _resize(self, new_capacity):
        new_data = [None] * new_capacity
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_capacity

    def append(self, v):
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        self.data[self.size] = v
        self.size += 1

    def insert(self, i, v):
        if i < 0 or i > self.size:
            raise IndexError("Index out of bounds")
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        
        for j in range(self.size, i, -1):
            self.data[j] = self.data[j - 1]
        
        self.data[i] = v
        self.size += 1

    def delete(self, i):
        if 0 <= i < self.size:
            val = self.data[i]
            for j in range(i, self.size - 1):
                self.data[j] = self.data[j + 1]
            self.data[self.size - 1] = None
            self.size -= 1
            return val
        raise IndexError("Index out of bounds")

    def tambah_reguler(self, v):
        self.append(v)

    def tambah_prioritas(self, v):
        self.insert(self.size // 2, v)

    def tambah_vip(self, v):
        self.insert(0, v)


class Node:
    def __init__(self, val):
        self.val = val
        self.next = None


class LinkList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def get(self, i):
        if 0 <= i < self.size:
            curr = self.head
            for _ in range(i):
                curr = curr.next
            return curr.val
        raise IndexError("Index out of bounds")

    def append(self, v):
        new_node = Node(v)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def insert(self, i, v):
        if i < 0 or i > self.size:
            raise IndexError("Index out of bounds")
            
        new_node = Node(v)
        if i == 0:
            new_node.next = self.head
            self.head = new_node
            if self.size == 0:
                self.tail = new_node
        else:
            curr = self.head
            for _ in range(i - 1):
                curr = curr.next
            new_node.next = curr.next
            curr.next = new_node
            if new_node.next is None:
                self.tail = new_node
        self.size += 1

    def delete(self, i):
        if 0 <= i < self.size:
            if i == 0:
                val = self.head.val
                self.head = self.head.next
                if self.head is None:
                    self.tail = None
            else:
                curr = self.head
                for _ in range(i - 1):
                    curr = curr.next
                val = curr.next.val
                curr.next = curr.next.next
                if curr.next is None:
                    self.tail = curr
            self.size -= 1
            return val
        raise IndexError("Index out of bounds")

    def tambah_reguler(self, v):
        self.append(v)

    def tambah_prioritas(self, v):
        self.insert(self.size // 2, v)

    def tambah_vip(self, v):
        self.insert(0, v)
