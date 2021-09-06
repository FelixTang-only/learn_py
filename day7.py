# dict
# obj
names = {
    'kim': 17,
    'jan': 18
}
# names['kim'] = 19
# names['kim'] 17
    # in
    # 'mark' in names
    # get()
    # names.get('mark')
result = names.get('mark')
# None
# print(result)
    # pop(key)
names.pop('kim')
# print(names)
# set
s = set([1, 2, 3, 3, 2, 1, 4])
# print(s)
    # add(key)
s.add(5)
s.add(5)
# print(s)
    # remove(key)
s.remove(5)
# print(s)
s1 = set([1, 2, 3])
s2 = set([2, 3, 4])
# s3 = s1 & s2
# print(s3)
s4 = s1 | s2
print(s4)