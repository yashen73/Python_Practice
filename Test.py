class Student:
    def __init__(self, name,age):
        self.name = name
        self.age = age

s1: Student = Student('yashen', 3)

print(s1.name)
print(s1.age)