# list
# Python内置的一种数据类型是列表：list。list是一种有序的集合，可以随时添加和删除其中的元素。
names = ['1', '2', '3'] 
# 0 1 2
# names[1]
# names[3]
# names[-1]
    # len()
    # append
    # names.append('4')
    # insert
    # names.insert(1, 'kim')
    # pop()
    # names.pop()
    # pop(i)
    # names.pop(1)
# names[0] = 4
    # 二维数组，类似的还有三维、四维……数组
    # age = [17, 18, 19]
    # names = [1, 2, 3, age]

# tuple
# 另一种有序列表叫元组：tuple。tuple和list非常类似，但是tuple一旦初始化就不能修改
# tuple不能变，它也没有append()，insert()这样的方法。其他获取元素的方法和list是一样的，你可以正常地读取数值，但不能赋值成另外的元素。
# 不可变的tuple有什么意义？
# names = (1, 2, 3)
# names[0]
# names[-1]
# names = ()
# names = (1,)
# names.append()
# names.insert()
# a = (1, 2, [3, 4])
# a[2][0] = 5
