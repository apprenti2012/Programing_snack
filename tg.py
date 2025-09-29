import time
import sys
debut = input("Nombre de début : ")
while len(sys.argv)<1:
  time.sleep(0.0001)
debut = int(sys.argv[1])
fin = input("Nombre de fin : ")
while len(sys.argv)<1:
  time.sleep(0.0001)
fin = int(sys.argv[1)
print("Recherche des nombres premiers de ",debut," à ",fin)
def afficher_progression(pourcentage, largeur=50):
  barre = int((pourcentage/100)*largeur)
  barre_str = '#'*barre+'-'*(largeur-barre)
  sys.stdout.write(f"\r[{barre_str}]{pourcentage}%")
  sys.stdout.flush()
print("Progression de la recherche : ")
time.sleep(0.25)
for i in range(101):
  afficher_progression(i)
  time.sleep(0.05)
print()
for candi in range(debut, fin):
  for x in range(2, candi):
    if candi%x==0:
      break
    if(x==candi-1):
      print("***Nombre premier :", candi)  
