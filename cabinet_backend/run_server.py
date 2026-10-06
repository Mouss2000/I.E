import os
import sys
import webbrowser
import threading
import time

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000")

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cabinet_backend.settings")
    import django
    django.setup()
    
    from waitress import serve
    from cabinet_backend.wsgi import application

    # Automatically execute unapplied migrations just in case it's a fresh DB on another machine
    from django.core.management import call_command
    print("Vérification de la base de données...")
    call_command("migrate", "--noinput")

    print("\n=======================================================")
    print("Démarrage du serveur Cabinet 2.0 sur http://127.0.0.1:8000")
    print("L'application va s'ouvrir dans votre navigateur par défaut.")
    print("Laissez cette fenêtre ouverte.")
    print("=======================================================\n")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    serve(application, host="127.0.0.1", port=8000, threads=6)

if __name__ == "__main__":
    main()
