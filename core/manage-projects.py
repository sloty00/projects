import json
import os
import sys
from datetime import datetime

def update_projects():
    # 1. Obtener las variables del entorno inyectadas por el Action
    action = os.getenv('GITOPS_ACTION', '').strip()
    data_raw = os.getenv('GITOPS_DATA', '').strip()
    
    print(f"--- DEBUG: ENTORNO GITOPS RECIBIDO ---")
    print(f"Acción: {action}")
    print(f"Datos RAW: {data_raw}")
    print(f"--------------------------------------")
    
    try:
        data = json.loads(data_raw) if data_raw else {}
    except json.JSONDecodeError as e:
        print(f"❌ Error al decodificar los datos JSON recibidos: {e}")
        return

    if not action:
        print("⚠️ No se detectó ninguna acción válida a ejecutar.")
        return

    # 2. Configuración de rutas
    file_path = "_data/project-schedule.json"
    print(f"🛠️ Procesando Acción: {action}")

    # 3. Lectura robusta del archivo JSON (RED DE SEGURIDAD)
    try:
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            print(f"⚠️ Archivo inexistente o vacío, iniciando estructura base.")
            content = {"metadata": {"last_updated": ""}, "projects": []}
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                # Asegurar que la estructura mínima exista
                if 'projects' not in content:
                    content['projects'] = []
                if 'metadata' not in content:
                    content['metadata'] = {}
    except json.JSONDecodeError:
        print(f"⚠️ Archivo JSON corrupto detectado. Reiniciando estructura limpia.")
        content = {"metadata": {"last_updated": ""}, "projects": []}
    except Exception as e:
        print(f"❌ Error crítico al leer el archivo JSON: {e}")
        return

    # 4. Lógica de Negocio
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

    # 5. Operaciones CRUD
    if action == 'add_project':
        new_p = {
            "name": data.get('name', 'Proyecto Nuevo'),
            "status": "Activo",
            "dates": {"contract_start": data.get('start'), "contract_end": data.get('end')},
            "metrics": {"uf_valor_referencia": 38000.0, "tasa_por_hora": 0.25, "status_label": "Activo"},
            "phases": []
        }
        content['projects'].append(new_p)
        print(f"✅ Proyecto '{new_p['name']}' inyectado.")

    elif action == 'add_task':
        for p in content['projects']:
            if p['name'] == data.get('project_name'):
                for phase in p.get('phases', []):
                    if phase['phase_name'] == data.get('phase_name'):
                        new_task = {
                            "task_name": data.get('task_name', 'Nueva Tarea'),
                            "hh_spent": float(data.get('hh', 0)),
                            "status": data.get('status', 'en proceso').lower()
                        }
                        phase.setdefault('tasks', []).append(new_task)
                        print(f"✅ Tarea añadida.")
                        break

    # 6. Guardar cambios
    for i in range(len(content['projects'])):
        content['projects'][i] = recalculate(content['projects'][i])
    
    content['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        print("💾 Cambios persistidos con éxito.")
    except Exception as e:
        print(f"❌ Error al escribir: {e}")

if __name__ == "__main__":
    update_projects()
