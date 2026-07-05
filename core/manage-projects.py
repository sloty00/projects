import json
import os
from datetime import datetime

def update_projects():
    # 1. Obtener las variables del entorno
    action = os.getenv('GITOPS_ACTION', '').strip()
    data_raw = os.getenv('GITOPS_DATA', '').strip()
    
    print(f"--- DEBUG: ENTORNO GITOPS RECIBIDO ---")
    print(f"Acción: {action} | Datos RAW: {data_raw}")
    
    try:
        data = json.loads(data_raw) if data_raw else {}
    except json.JSONDecodeError as e:
        print(f"❌ Error JSON: {e}")
        return

    if not action:
        return

    # 2. Configuración y carga
    file_path = "_data/project-schedule.json"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
    except Exception as e:
        print(f"❌ Error crítico de carga: {e}")
        return

    # 3. Motor de recálculo
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
        project.setdefault('metrics', {})
        project['metrics']['total_progress'] = round(sum_progress / len(phases), 1) if phases else 0
        project['metrics']['total_hh'] = total_hh
        project['metrics']['total_uf'] = round(total_hh * project.get('metrics', {}).get('tasa_por_hora', 0.25), 2)
        return project

    # 4. Operaciones CRUD con normalización estricta
    target_project = data.get('project_name', '').strip().lower()

    if action == 'add_project':
        content['projects'].append({
            "name": data.get('name', 'Proyecto Nuevo'),
            "status": "Activo",
            "dates": {"contract_start": data.get('start'), "contract_end": data.get('end')},
            "metrics": {"uf_valor_referencia": 38000.0, "tasa_por_hora": 0.25},
            "phases": []
        })

    elif action == 'add_phase':
        for p in content['projects']:
            if p['name'].strip().lower() == target_project:
                p['phases'].append({"phase_name": data.get('phase_name'), "tasks": [], "progress": 0.0})

    elif action == 'add_task':
        for p in content['projects']:
            if p['name'].strip().lower() == target_project:
                for ph in p.get('phases', []):
                    if ph['phase_name'].strip() == data.get('phase_name', '').strip():
                        ph.setdefault('tasks', []).append({
                            "task_name": data.get('task_name', 'Nueva Tarea'),
                            "hh_spent": float(data.get('hh', 0)),
                            "status": data.get('status', 'en proceso').lower()
                        })

    elif action == 'edit_task':
        for p in content['projects']:
            if p['name'].strip().lower() == target_project:
                for ph in p.get('phases', []):
                    if ph['phase_name'].strip() == data.get('phase_name', '').strip():
                        for t in ph.get('tasks', []):
                            if t['task_name'].strip() == data.get('original_task_name', '').strip():
                                t['task_name'] = data.get('task_name')
                                t['hh_spent'] = float(data.get('hh', 0))
                                t['status'] = data.get('status', 'en proceso').lower()

    elif action == 'delete_task':
        for p in content['projects']:
            if p['name'].strip().lower() == target_project:
                for ph in p.get('phases', []):
                    if ph['phase_name'].strip() == data.get('phase_name', '').strip():
                        ph['tasks'] = [t for t in ph.get('tasks', []) if t['task_name'].strip() != data.get('task_name', '').strip()]

    elif action == 'delete_phase':
        for p in content['projects']:
            if p['name'].strip().lower() == target_project:
                p['phases'] = [ph for ph in p.get('phases', []) if ph['phase_name'].strip() != data.get('phase_name', '').strip()]

    elif action == 'delete_project':
        content['projects'] = [p for p in content['projects'] if p['name'].strip().lower() != target_project]

    # 5. Persistencia
    for p in content['projects']:
        recalculate(p)
    
    content['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Acción '{action}' ejecutada con éxito.")

if __name__ == "__main__":
    update_projects()
