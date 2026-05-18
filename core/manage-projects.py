import json
import os
import sys
from datetime import datetime

def update_projects():
    # 1. Obtener las variables del entorno independientes inyectadas por el Action
    action = os.getenv('GITOPS_ACTION', '').strip()
    data_raw = os.getenv('GITOPS_DATA', '').strip()
    
    # Imprimimos para ver qué llega exactamente en los logs de GitHub Actions
    print(f"--- DEBUG: ENTORNO GITOPS RECIBIDO ---")
    print(f"Acción: {action}")
    print(f"Datos RAW: {data_raw}")
    print(f"--------------------------------------")
    
    # Reconstruimos el diccionario de datos de forma segura sin romper el parseo
    try:
        data = json.loads(data_raw) if data_raw else {}
    except json.JSONDecodeError as e:
        print(f"❌ Error al decodificar los datos JSON recibidos: {e}")
        return

    # Compatibilidad de respaldo si se llega a ejecutar pasando argumentos directos por consola
    if not action and len(sys.argv) > 1:
        try:
            fallback_payload = json.loads(sys.argv[1])
            action = fallback_payload.get('action')
            data = fallback_payload.get('data', {})
        except Exception as e:
            print(f"⚠️ No se pudo procesar el argumento de respaldo: {e}")
            return

    if not action:
        print("⚠️ No se detectó ninguna acción válida a ejecutar. Cancelando proceso.")
        return

    # 2. Configuración de rutas y validación del archivo destino
    file_path = "_data/project-schedule.json"
    print(f"🛠️ Procesando Acción: {action}")

    if not os.path.exists(file_path):
        print(f"❌ Error Crítico: No se encontró el archivo de datos en la ruta {file_path}")
        return

    # 3. Lectura del archivo JSON existente con manejo de errores
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
    except Exception as e:
        print(f"❌ Error al leer el archivo JSON: {e}")
        return

    # 4. Lógica de Negocio (Cálculos automáticos de métricas, H/H y UF)
    def recalculate(project):
        phases = project.get('phases', [])
        total_hh = 0
        sum_progress = 0
        
        for phase in phases:
            tasks = phase.get('tasks', [])
            done = len([t for t in tasks if t.get('status', '').lower() == 'completada'])
            p_progress = (done / len(tasks) * 100) if tasks else 0
            phase['progress'] = round(p_progress, 1)
            sum_progress += p_progress
            total_hh += sum(float(t.get('hh_spent', 0)) for t in tasks)

        if 'metrics' not in project: 
            project['metrics'] = {}
            
        project['metrics']['total_progress'] = round(sum_progress / len(phases), 1) if phases else 0
        project['metrics']['total_hh'] = total_hh
        project['metrics']['total_uf'] = round(total_hh * 0.25, 2)
        return project

    # 5. Procesar Operaciones CRUD basadas en la acción recibida
    if action == 'add_project':
        new_p = {
            "name": data.get('name', 'Proyecto Nuevo'),
            "status": "Activo",
            "dates": {
                "contract_start": data.get('start'), 
                "contract_end": data.get('end')
            },
            "metrics": {
                "uf_valor_referencia": 38000.0,
                "tasa_por_hora": 0.25,
                "status_label": "Activo"
            },
            "phases": []
        }
        content['projects'].append(new_p)
        print(f"✅ Proyecto '{new_p['name']}' inyectado correctamente en la lista.")

    elif action == 'add_phase':
        project_found = False
        for p in content['projects']:
            if p['name'] == data.get('project_name'):
                p['phases'].append({
                    "phase_name": data.get('phase_name'), 
                    "tasks": [], 
                    "progress": 0.0
                })
                project_found = True
                print(f"✅ Fase '{data.get('phase_name')}' añadida con éxito a {p['name']}.")
                break
        if not project_found:
            print(f"⚠️ Advertencia: No se encontró ningún proyecto con el nombre '{data.get('project_name')}'")

    # 6. Recalcular e indexar todo el árbol antes de guardar cambios
    for i in range(len(content['projects'])):
        content['projects'][i] = recalculate(content['projects'][i])
    
    # Actualizar la marca de tiempo global en los metadatos del JSON
    content['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Guardar los cambios definitivos de vuelta al archivo JSON
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        print("💾 Cambios persistidos y guardados con éxito en el archivo local.")
    except Exception as e:
        print(f"❌ Error al intentar escribir los datos en el archivo: {e}")

if __name__ == "__main__":
    update_projects()
