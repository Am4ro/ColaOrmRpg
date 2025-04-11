from Exceptions import OwnEmpty  # Asegúrate de tener esta excepción definida

class ColaMisiones:
    DEFAULT_CAPACITY = 100

    def __init__(self):
        self.data = [None] * ColaMisiones.DEFAULT_CAPACITY
        self.size = 0
        self.front = 0

    def __len__(self):
        return self.size

    def is_empty(self):
        return self.size == 0

    def first(self):
        if self.is_empty():
            raise OwnEmpty("La cola está vacía")
        return self.data[self.front]

    def dequeue(self):
        if self.is_empty():
            raise OwnEmpty("La cola está vacía")
        valor = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % len(self.data)
        self.size -= 1
        return valor

    def enqueue(self, mision):
        if self.size == len(self.data):
            self._resize(2 * len(self.data))
        idx = (self.front + self.size) % len(self.data)
        self.data[idx] = mision
        self.size += 1

    def _resize(self, capacidad):
        viejo = self.data
        self.data = [None] * capacidad
        walk = self.front
        for k in range(self.size):
            self.data[k] = viejo[walk]
            walk = (walk + 1) % len(viejo)
        self.front = 0

    def size(self):
        return self.size