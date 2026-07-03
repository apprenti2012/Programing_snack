import random
a = [0,1,2,3,4,5,6,7,8,9,10]
b = [str(i) for i in a]
print(b)
c = b[random.randint(0,10)]                                                            
print(c)
print(ord(c))