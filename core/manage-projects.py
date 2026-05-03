import json
import os
import sys
from datetime import datetime

class ProjectEngine:
    def __init__(self, data_path='_data/project-schedule.json'):
        self.data_path = data_path
        self.rate_hh_uf = 0.25
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
        """Calcula porcentajes reales, días y costos en UF."""
        # Fechas
        end_date = datetime.strptime(project['dates']['contract_end'], '%Y-%m-%d')
        today = datetime.now()
        diff_days = (end_date - today).days

        total_tasks = 0
        completed_tasks = 0
        total_hh_spent = 0

        # L2 y L3 Processing
        for phase in project.get('phases', []):
            tasks = phase.get('tasks', [])
            p_total = len(tasks)
            p_done = len([t for t in tasks if t['status'].lower() == 'completada'])
            
            # Avance real de fase
            phase['progress'] = round((p_done / p_total * 100), 1) if p_total > 0 else 0
            
            total_tasks += p_total
            completed_tasks += p_done
            total_hh_spent += sum(t.get('hh_spent', 0) for t in tasks)

        # Métricas de Nivel 1 (Proyecto)
        project['metrics'] = {
            "days_diff": diff_days,
            "total_progress": round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0,
            "total_hh": total_hh_spent,
            "total_uf": round(total_hh_spent * self.rate_hh_uf, 2),
            "status_label": "Al día" if diff_days >= 0 else "Retrasado"
        }
        return project

    def sync(self):
        """Recalcula todos los proyectos (ejecutar cada mañana)."""
        for i in range(len(self.data['projects'])):
            self.data['projects'][i] = self.calculate_metrics(self.data['projects'][i])
        self.save()
        print("Sincronización completa: Métricas actualizadas.")

if __name__ == "__main__":
    engine = ProjectEngine()
    if len(sys.argv) == 2 and sys.argv[1] == "--sync":
        engine.sync()
    else:
        print("Uso: python3 manage_projects.py --sync")
