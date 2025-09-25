import random
scr=0
for i in range(10):
  random.seed()
  m1=random.randint(0,10)
  random.seed()
  m2=random.randint(0,10)
  print(m1,"*",m2, end=" ")
  rep=int(input("= "))
  res=m1*m2
  if rep==res:
    print("juste")
    scr+=1
  else:
    print("faux")
    print(f"la vraie réponse était: {str(res)}")
if scr==10:
  print("Bravo tu as fait u score parfait : ", scr, "/10")
else:
  print("Voilà ton score : ", scr, "/10")
