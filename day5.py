# 循环
# for in
names = ['张三', '李四']
for item in names:
    name = '我的名字叫：' + item
    print(name)
# while
# 100以内所有奇数之和
sum = 0
n = 99
while n > 0:
    sum = sum + n
    n = n - 2
    # n 97
    # n -1
print(sum)
# break
# ages = [15, 16, 17, 18, 19]
# age = 0
# for item in ages:
#     age = item
#     if item == 18:
#         break
    # print(age)
# print(age)
# continue
ages = [15, 16, 17, 18, 19]
for item in ages:
    age = item
    if age == 18:
        continue
    print(age)
# print(age)
