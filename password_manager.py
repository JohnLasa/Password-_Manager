import sqlite3
from cryptography.fernet import Fernet

# Load or generate the encryption key
try:
    with open("key.key", "rb") as key_file:
        key = key_file.read()
except FileNotFoundError:
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

cipher = Fernet(key)

# Connect to SQLite database
conn = sqlite3.connect('passwords.db')
cursor = conn.cursor()

# Create the table (only needs to run once)
cursor.execute('''
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
''')
conn.commit()

# Add a new password to the database
def add_password(service, username, plain_password):
    encrypted_password = cipher.encrypt(plain_password.encode())
    cursor.execute('INSERT INTO passwords (service, username, password) VALUES (?, ?, ?)',
                   (service, username, encrypted_password))
    conn.commit()
    print(f"Password for {service} added successfully.")

# Retrieve a password from the database
def retrieve_password(service):
    cursor.execute('SELECT username, password FROM passwords WHERE service = ?', (service,))
    result = cursor.fetchone()
    if result:
        username, encrypted_password = result
        plain_password = cipher.decrypt(encrypted_password).decode()
        return f"Service: {service}, Username: {username}, Password: {plain_password}"
    else:
        return f"No entry found for {service}."

# Simple user interface
def main():
    print("Password Manager")
    print("----------------")
    while True:
        print("\nOptions:")
        print("1. Add a new password")
        print("2. Retrieve a password")
        print("3. Exit")
        
        choice = input("Enter your choice: ")
        if choice == "1":
            service = input("Enter the service name: ")
            username = input("Enter the username: ")
            password = input("Enter the password: ")
            add_password(service, username, password)
        elif choice == "2":
            service = input("Enter the service name: ")
            print(retrieve_password(service))
        elif choice == "3":
            print("Exiting Password Manager.")
            break
        else:
            print("Invalid choice. Please try again.")

# Run the program
if __name__ == "__main__":
    main()