import bcrypt

# Generer les mots de passe hasches avec bcrypt directement
passwords = {
    "admin": "admin123",
    "souha": "souha2026"
}

print("Mots de passe hasches — copiez ces valeurs dans app.py :\n")
for user, pwd in passwords.items():
    hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f"Utilisateur : {user}")
    print(f"Hash        : {hashed}")
    print()
