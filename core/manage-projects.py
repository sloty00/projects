import json
import os
from datetime import datetime

def update_projects():
    # 1. Obtener el PAYLOAD de la GitHub Action
    payload_raw = os.getenv('PAYLOAD', '').strip()
    
    if not payload_raw or payload_raw in ['null', '{}', 'None', '']:
        print("⚠️ Sin datos en PAYLOAD. Saliendo.")
        return

    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError as e:
        print(f"❌ Error JSON: {e}")
        return

    # 2. Configuración de rutas
    file_path = "_data/project-schedule.json"
    # Ajuste para detectar la acción correctamente desde el evento de GitHub
    action = payload.get('action') or payload.get('event_type')
    data = payload.get('data', {})
    
    if not os.path.exists(file_path):
        print(f"❌ No existe {file_path}")
        return

    # 3. Lectura
    with open(file_path, 'r', encoding='utf-8') as f:
        content = json.load(f)

    # 4. LÓGICA DE NEGOCIO (0.25 UF por Hora)
    def recalculate(project):
        """Recalcula métricas basadas en las tareas reales."""
        total_hh = 0
        sum_progress = 0
        phases = project.get('phases', [])
        
        for phase in phases:
            tasks = phase.get('tasks', [])
            total_tasks = len(tasks)
            done_tasks = len([t for t in tasks if t.get('status', '').lower() == 'completada'])
            
            phase_progress = (done_tasks / total_tasks * 100) if total_tasks > 0 else 0
            phase['progress'] = round(phase_progress, 1)
            
            sum_progress += phase_progress
            total_hh += sum(float(t.get('hh_spent', 0)) for t in tasks)

        num_phases = len(phases)
        # Aseguramos que la estructura de métricas exista
        if 'metrics' not in project:
            project['metrics'] = {}
            
        project['metrics']['total_progress'] = round(sum_progress / num_phases, 1) if num_phases > 0 else 0
        project['metrics']['total_hh'] = total_hh
        project['metrics']['total_uf'] = round(total_hh * 0.25, 2)
        return project

    # 5. PROCESAR ACCIÓN
    if action == 'add_project':
        new_p = {
            "name": data.get('name'),
            "status": "Activo",
            "dates": {
                "contract_start": data.get('start'), 
                "contract_end": data.get('end')
            },
            "metrics": {
                "uf_valor_referencia": 38000.0, # Corregido para tu JSON
                "tasa_por_hora": 0.25,
                "status_label": "Activo",
                "total_progress": 0.0,
                "total_hh": 0.0,
                "total_uf": 0.0
            },
            "phases": []
        }
        content['projects'].append(new_p)

    elif action == 'add_phase':
        for p in content['projects']:
            if p['name'] == data.get('project_name'):
                p['phases'].append({"phase_name": data.get('phase_name'), "tasks": [], "progress": 0.0})

    elif action == 'add_task':
        for p in content['projects']:
            if p['name'] == data.get('project_name'):
                for ph in p['phases']:
                    if ph['phase_name'] == data.get('phase_name'):
                        ph['tasks'].append({
                            "task_name": data.get('task_name'),
                            "hh_spent": float(data.get('hh', 0)),
                            "status": data.get('status', 'en proceso')
                        })

    # 6. Sincronización final y actualización de Metadata
    for i in range(len(content['projects'])):
        content['projects'][i] = recalculate(content['projects'][i])
    
    # Actualizar la fecha de última modificación
    content['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 7. ESCRITURA
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    
    print(f"🚀 Proyecto actualizado vía GitOps: {action}")

if __name__ == "__main__":
    update_projects()
