import instaloader
import os

# Initialize Instaloader
L = instaloader.Instaloader()

# Define your Instagram credentials
USERNAME = 
PASSWORD = 

# Define the path where you want to save the session file
save_path = "

# Log in and save session to a .session file in the specified directory
try:
    # Login and save session
    L.login(USERNAME, PASSWORD)  # Logs in and saves session for future use

    # Save the session to the specified directory
    session_file_path = os.path.join(save_path, f"{USERNAME}.session")
    L.save_session_to_file(session_file_path)
    
    print(f"Session saved to {session_file_path}")

except instaloader.exceptions.BadCredentialsException:
    print("Invalid credentials. Please check your username and password.")
except Exception as e:
    print(f"An error occurred: {e}")
