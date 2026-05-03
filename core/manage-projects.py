import json
import os
import sys
from datetime import datetime

def update_projects():
    # 1. Obtener y depurar el PAYLOAD
    payload_raw = os.getenv('PAYLOAD', '').strip()
    
    # Imprimimos para ver qué llega en los logs de GitHub
    print(f"--- DEBUG: PAYLOAD RECIBIDO ---\n{payload_raw}\n------------------------------")
    
    if not payload_raw or payload_raw in ['null', '{}', 'None', '']:
        print("⚠️ PAYLOAD vacío o inválido. Verificando argumentos de sistema...")
        # Si falló la variable de entorno, intentamos leer argumentos directos
        if len(sys.argv) > 1:
             payload_raw = sys.argv[1]
        else:
             return

    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError as e:
        print(f"❌ Error al decodificar JSON: {e}")
        return

    # 2. Configuración de rutas y Acción
    file_path = "_data/project-schedule.json"
    
    # Prioridad: payload['action'] -> payload['event_type'] -> 'sync'
    action = payload.get('action') or payload.get('event_type') or 'sync'
    data = payload.get('data', {})
    
    print(f"🛠️ Procesando Acción: {action}")

    if not os.path.exists(file_path):
        print(f"❌ Error Crítico: No se encontró {file_path}")
        return

    # 3. Lectura con manejo de errores
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
    except Exception as e:
        print(f"❌ Error al leer el JSON: {e}")
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

        if 'metrics' not in project: project['metrics'] = {}
        project['metrics']['total_progress'] = round(sum_progress / len(phases), 1) if phases else 0
        project['metrics']['total_hh'] = total_hh
        project['metrics']['total_uf'] = round(total_hh * 0.25, 2)
        return project

    # 5. Procesar Acción (Normalización de nombres para tu JSON)
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
        print(f"✅ Proyecto '{new_p['name']}' inyectado.")

    elif action == 'add_phase':
        for p in content['projects']:
            if p['name'] == data.get('project_name'):
                p['phases'].append({"phase_name": data.get('phase_name'), "tasks": [], "progress": 0.0})
                print(f"✅ Fase añadida a {p['name']}")

    # 6. Sincronización y Guardado
    for i in range(len(content['projects'])):
        content['projects'][i] = recalculate(content['projects'][i])
    
    content['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    
    print("💾 Cambios guardados en el archivo local.")

if __name__ == "__main__":
    update_projects()
