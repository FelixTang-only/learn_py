# 函数的参数详细解读
# 位置参数
# def power(x):
#     return x * x
# power(4)
# power(x, n)
# def power(x, n):
#     s = 1
#     while n > 0:
#         n = n - 1
#         s = s * x
#     return s
# print(power(5, 2))
# 默认参数
# power(5)
# def power(x, n = 2):
#     s = 1
#     while n > 0:
#         n = n - 1
#         s = s * x
#     return s
# power(5)
# print(power(n = 1, x = 2))
# power(2, 1)
# def add_end(l=[]):
#     l.append('end')
#     return l
# print(add_end())
# print(add_end())
# def add_end(l=None):
#     if l is None:
#         l = []
#     l.append('end')
#     return l
# print(add_end())
# print(add_end())
# 可变参数
# def calc(numbers):
#     sum = 0
#     for n in numbers:
#         sum = sum + n * n
#     return sum
# calc([1, 2, 3])
# calc((1, 2, 3))
# def calc(*numbers):
#     sum = 0
#     for n in numbers:
#         sum = sum + n * n
#     return sum
# nums = [1, 2, 3]
# calc(nums[0], nums[1], nums[2])
# calc(*nums)
# 关键字参数
# dict
# def preson(name, age, **kw):
#     print('name:', name, 'age:', age, 'other:', kw)
# print(preson('kim', 18))
# print(preson('jim', 30, city='beijing', jod='teacher'))

# extre = {'city': 'beijinng', 'job': 'teacher'}
# preson('jack', 24, city=extre['city'], job=extre['job'])
# preson('jack', 24, **extre)
# 命名关键字参数
# city age
# def preson(name, age, *, city, job):
#     print(name, age, city, job)
# **kw
# * 
# preson('jack', 24, city='beijing', job='teacher')

# def preson(name, age, *args, city, job):
#     print(name, age, city, job)
# print(preson('jack', 24, 'beijing', 'teacher'))

# def preson(name, age, *, city, job='teacher'):
#     print(name, age, city, job)
# preson('kim', 21, city='beijing')
# 参数组合
def f1(a, b, c=0, *args, **kw):
    print(a, b, c, args, kw)