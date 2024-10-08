import json
from datetime import datetime, timedelta

# Función para leer el archivo JSON original y transformarlo
def transform_json(input_file, output_file):
    # Leer el archivo JSON original
    with open(input_file, 'r') as f:
        data = json.load(f)

    transformed_data = []

    for i in range(len(data["round_number"])):
        event = {
            "name": data["event_name"][str(i)],
            "countryName": data["country"][str(i)],
            "countryKey": None,
            "roundNumber": data["round_number"][str(i)],
            "start": None, # El valor de 'end' se calculará a partir de las sesiones
            "end": None,  # El valor de 'end' se calculará a partir de las sesiones
            "gmt_offset": data["gmt_offset"][str(i)],
            "sessions": [],
            "over": False  # Cambia esto según la lógica que desees
        }

        # Calcular las fechas de las sesiones
        for j in range(1, 6):
            session_name = data[f'session{j}'][str(i)]
            session_date = data[f'session{j}_date'][str(i)]

            if session_name:  # Solo incluir sesiones que no sean None
                session_start = session_date
                session_start_dt = datetime.fromisoformat(session_start)
                session_end_dt = session_start_dt + timedelta(hours=1)
                
                event["sessions"].append({
                    "sessionNumber": str(j),
                    "kind": session_name,
                    "start": session_start + 'Z',
                    "end": session_end_dt.isoformat() + 'Z'
                })

        # Asignar la fecha de finalización del evento
        event["start"] = min(session["start"] for session in event["sessions"])
        event["end"] = max(session["end"] for session in event["sessions"])

        transformed_data.append(event)

    # Guardar el nuevo archivo JSON
    with open(output_file, 'w') as f:
        json.dump(transformed_data, f, indent=4)

# Llamar a la función con los nombres de archivo deseados
input_file = '2024_input.json'  # Reemplaza con la ruta a tu archivo de entrada
output_file = '2024.json'  # Ruta para guardar el archivo de salida
transform_json(input_file, output_file)
