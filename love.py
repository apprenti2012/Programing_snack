import random
name1 = input("entrer le prénom de la personne que vous aimez : ")
name2 = input("entrer votre prénom : ")
nombre = random.randint(1,3)
if nombre == 1 :
	print(f"{name1} et vous ({name2}) n'êtes pas fait pour être ensemble")
else:
	print(f"{name1} et vous ({name2})allez vivre heureux pour toujours 😊") 