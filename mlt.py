import random
def lev1():
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
            print("Bravo tu as fait un score parfait : ", scr, "/10")
        else:
            print("Voilà ton score : ", scr, "/10")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def lev2():
  scr=0
  for i in range(20):
    random.seed()
    m1=random.randint(0,11)
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def lev3():
  scr=0
  for i in range(30):
    random.seed()
    m1=random.randint(6,12)
    random.seed()
    m2=random.randint(6,12)
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
level=input("choisi ton niveau : 1,2 ou 3, (Tape 1, 2 ou 3): ")
if level=="1":
  lev1()
elif level=="2":
  lev2()
else:
  lev3()
  
  
