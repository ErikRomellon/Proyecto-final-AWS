import requests

def crear_alumno(id, nombres, apellidos, matricula, promedio):
    # Crear un alumno (POST)
    url = "http://127.0.0.1:8080/alumnos"
    alumno = {
        "id": id,
        "nombres": nombres,
        "apellidos": apellidos,
        "matricula": matricula,
        "promedio": promedio
    }
    response = requests.post(url, json=alumno)
    print("Respuesta al POST (Crear Alumno):", response.json())

def obtener_alumnos():
    # Obtener lista de alumnos (GET)
    url = "http://127.0.0.1:8080/alumnos"
    response = requests.get(url)
    print("Respuesta al GET (Obtener Alumnos):", response.json())

def obtener_alumno(id):
    # Obtener un alumno por id (GET)
    url = f"http://127.0.0.1:8080/alumnos/{id}"
    response = requests.get(url)
    print(f"Respuesta al GET (Obtener Alumno {id}):", response.json())

def actualizar_alumno(id, nombres, apellidos, matricula, promedio):
    # Actualizar un alumno (PUT)
    url = f"http://127.0.0.1:8080/alumnos/{id}"
    alumno = {
        "id": id,
        "nombres": nombres,
        "apellidos": apellidos,
        "matricula": matricula,
        "promedio": promedio
    }
    response = requests.put(url, json=alumno)
    print(f"Respuesta al PUT (Actualizar Alumno {id}):", response.json())

def eliminar_alumno(id):
    # Eliminar un alumno (DELETE)
    url = f"http://127.0.0.1:8080/alumnos/{id}"
    response = requests.delete(url)
    print(f"Respuesta al DELETE (Eliminar Alumno {id}):", response.json())


def crear_profesor(id, numeroEmpleado, nombres, apellidos, horasClase):
    # Crear un profesor (POST)
    url = "http://127.0.0.1:8080/profesores"
    profesor = {
        "id": id,
        "numeroEmpleado": numeroEmpleado,
        "nombres": nombres,
        "apellidos": apellidos,
        "horasClase": horasClase
    }
    response = requests.post(url, json=profesor)
    print("Respuesta al POST (Crear Profesor):", response.json())

def obtener_profesores():
    # Obtener lista de profesores (GET)
    url = "http://127.0.0.1:8080/profesores"
    response = requests.get(url)
    print("Respuesta al GET (Obtener Profesores):", response.json())

def obtener_profesor(id):
    # Obtener un profesor por id (GET)
    url = f"http://127.0.0.1:8080/profesores/{id}"
    response = requests.get(url)
    print(f"Respuesta al GET (Obtener Profesor {id}):", response.json())

def actualizar_profesor(id, numeroEmpleado, nombres, apellidos, horasClase):
    # Actualizar un profesor (PUT)
    url = f"http://127.0.0.1:8080/profesores/{id}"
    profesor = {
        "id": id,
        "numeroEmpleado": numeroEmpleado,
        "nombres": nombres,
        "apellidos": apellidos,
        "horasClase": horasClase
    }
    response = requests.put(url, json=profesor)
    print(f"Respuesta al PUT (Actualizar Profesor {id}):", response.json())

def eliminar_profesor(id):
    # Eliminar un profesor (DELETE)
    url = f"http://127.0.0.1:8080/profesores/{id}"
    response = requests.delete(url)
    print(f"Respuesta al DELETE (Eliminar Profesor {id}):", response.json())


crear_alumno(1,"Erik", "Romellon", "A17016403", 9.0)
obtener_alumnos()
obtener_alumno(1)
actualizar_alumno(1,"Erik", "Romellon", "A17016403", 8.0)
obtener_alumno(1)
eliminar_alumno(1)
obtener_alumnos()