import random
def lev1():
    scr=0
    for i in range(10):
        m1=random.randint(0,10)
        m2=random.randint(0,10)
        print(str(m1), "*", str(m2))
        rep=int(input("="))
        res=m1*m2
        if rep==res:
          print("juste")
          scr+=1
        else:
          print("faux")
          print("la vraie réponse était : ",str(res))
    if scr==10:
      print("Bravo tu as fait un score parfait : ", scr, "/10")
    else:
      print("Voilà ton score : ", scr, "/10")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def lev2():
  scr=0
  for i in range(20):
    m1=random.randint(0,11)
    m2=random.randint(0,10)
    print(str(m1), "*", str(m2))
    rep=int(input("= "))
    res=m1*m2
    if rep==res:
      print("juste")
      scr+=1
    else:
      print("faux")
      print("la vraie réponse était : ",str(res))
  if scr==20:
    print("Bravo tu as fait un score parfait : ", scr, "/10")
  else:
    print("Voilà ton score : ", scr, "/20")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def lev3():
  scr=0
  for i in range(30):
    m1=random.randint(6,12)
    m2=random.randint(6,12)
    print(str(m1), "*", str(m2))
    rep=int(input("= "))
    res=m1*m2
    if rep==res:
      print("juste")
      scr+=1
    else:
      print("faux")
      print("la vraie réponse était : ",str(res))
  if scr==30:
    print("Bravo tu as fait un score parfait : ", scr, "/10")
  else:
    print("Voilà ton score : ", scr, "/30")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
level=input("choisis ton niveau : 1,2 ou 3, (Tape 1, 2 ou 3): ")
if level=="1":
  lev1()
elif level=="2":
  lev2()
else:
  lev3()
  
  
