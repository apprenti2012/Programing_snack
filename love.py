import random 
def two_version():
 name1 = input("entrer le prénom de la personne que vous aimez : ")
 name2 = input("entrer votre prénom : ")
 nombre = random.randint(1,3)
 if nombre == 1 :
	 print(f"{name1} et vous ({name2}) n'êtes pas fait pour être ensemble")
 else:
	 print(f"{name1} et vous ({name2}) allez vivre heureux pour toujours 😊")
def random_version():
	woman_list = ["Anna","Gulia","Margaux","Tess","Naya", "Elena", "Mélodie","Personne", "Juliette","Lise", "Yuna",          "Mélina", "Lyna"]
	man_list = ["Ethan", "Mathis", "Louis", "Tom", "Lorenzo","Personne", "Amaury", "Yannis", "Lucas", "Gabriel", "Florent", "Antonin", "Jules"]
	sexe = input("Indique ton sexe, H ou F : ")
	if sexe=="H":
		 print(f"Tu irais bien avec {random.choice(woman_list)} ")
	elif sexe=="F" :
		 print(f"Tu irais bien avec {random.choice(man_list)} ")
while True:
	n = input(" quel version voulez vous choisir : 1 ou 2")
	if n=="1" :
	    two_version()
	elif n=="2" :
		random_version()
	else:
	    print("Tu n'as pas tapé 1 ou 2")
