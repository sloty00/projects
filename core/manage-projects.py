import json
import os
import sys
from datetime import datetime

class ProjectEngine:
    """Motor para la gestión de proyectos: Niveles, Finanzas (UF) y Plazos."""
    
    def __init__(self, data_path='_data/project-schedule.json'):
        self.data_path = data_path
        self.rate_hh_uf = 0.25 # Tarifa: 1/4 de UF por H/H
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"projects": [], "metadata": {}}

    def save(self):
        self.data['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def calculate_metrics(self, project):
        """Calcula días de desfase, progreso y consumo de UF."""
        # 1. Cálculo de Días (Lógica de plazos)
        contract_end = datetime.strptime(project['dates']['contract_end'], '%Y-%m-%d')
        today = datetime.now()
        # Calculamos la diferencia exacta en días
        diff_days = (contract_end - today).days
        
        # 2. Avance y H/H (L2 y L3)
        total_tasks = 0
        completed_tasks = 0
        total_hh_spent = 0
        
        for phase in project.get('phases', []):
            tasks = phase.get('tasks', [])
            phase_total = len(tasks)
            phase_done = len([t for t in tasks if t['status'] == 'completada'])
            
            # Progreso de la fase
            phase['progress'] = (phase_done / phase_total * 100) if phase_total > 0 else 0
            
            # Acumuladores para el proyecto (L1)
            total_tasks += phase_total
            completed_tasks += phase_done
            total_hh_spent += sum(t.get('hh_spent', 0) for t in tasks)

        # 3. Guardar métricas calculadas en el L1
        project['metrics'] = {
            "days_diff": diff_days,
            "total_progress": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "total_hh": total_hh_spent,
            "total_uf": round(total_hh_spent * self.rate_hh_uf, 4),
            "status_label": "Al día" if diff_days >= 0 else "Retrasado"
        }
        return project

    def add_project(self, name, start_date, contract_end):
        """Añade un proyecto con la estructura de 3 niveles solicitada."""
        new_project = {
            "id": len(self.data['projects']) + 1,
            "name": name,
            "dates": {
                "start": start_date,
                "contract_end": contract_end,
                "real_end": None
            },
            "phases": [], # L2: Fases (se añaden después)
            "metrics": {}  # Se llenará con calculate_metrics
        }
        
        # Calculamos métricas iniciales
        new_project = self.calculate_metrics(new_project)
        self.data['projects'].append(new_project)
        self.save()
        print(f"Proyecto '{name}' creado. Plazo: {new_project['metrics']['days_diff']} días.")

    def update_all_metrics(self):
        """Recalcula todo (útil para actualizar los 'días debidos' cada mañana)."""
        for i in range(len(self.data['projects'])):
            self.data['projects'][i] = self.calculate_metrics(self.data['projects'][i])
        self.save()
        print("Métricas de todos los proyectos actualizadas al día de hoy.")

if __name__ == "__main__":
    engine = ProjectEngine()
    
    # Comando para actualizar fechas y días debidos automáticamente
    if len(sys.argv) == 2 and sys.argv[1] == "--sync":
        engine.update_all_metrics()
        
    # Comando para crear proyecto: python3 manage.py "Nombre" "2026-05-01" "2026-06-01"
    elif len(sys.argv) > 3:
        engine.add_project(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Acciones disponibles:")
        print("  Crear: python3 manage_projects.py <nombre> <fecha_inicio_YYYY-MM-DD> <fecha_contrato_YYYY-MM-DD>")
        print("  Sincronizar días: python3 manage_projects.py --sync")
