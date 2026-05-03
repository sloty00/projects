import json
import os
import sys
from datetime import datetime

class ProjectEngine:
    def __init__(self):
        # 1. Detectar la raíz del proyecto de forma absoluta
        # Asume estructura: repo/core/manage-projects.py
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = os.path.join(self.base_dir, '_data', 'project-schedule.json')
        
        self.rate_hh_uf = 0.25
        self.data = self._load()

    def _load(self):
        """Carga el JSON asegurando que la ruta existe."""
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"AVISO: No se encontró el archivo en {self.data_path}. Creando nuevo.")
            return {"projects": [], "metadata": {}}

    def save(self):
        """Guarda el JSON en la ruta absoluta calculada."""
        if 'metadata' not in self.data:
            self.data['metadata'] = {}
            
        self.data['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Asegurar que la carpeta _data existe
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"Archivo guardado exitosamente en: {self.data_path}")

    def add_project(self, name, uf_value, mora_rate):
        """Crea un nuevo proyecto con estructura base y lo guarda."""
        try:
            # Limpieza de strings a números (maneja "0,5" -> 0.5)
            uf_clean = float(str(uf_value).replace(',', '.'))
            mora_clean = float(str(mora_rate).replace(',', '.'))

            new_item = {
                "name": name,
                "status": "Activo",
                "dates": {
                    "contract_start": datetime.now().strftime("%Y-%m-%d"),
                    "contract_end": datetime.now().strftime("%Y-%m-%d") 
                },
                "metrics": {
                    "uf_base": uf_clean,
                    "mora": mora_clean,
                    "total_progress": 0,
                    "total_hh": 0,
                    "total_uf": 0,
                    "days_diff": 0,
                    "status_label": "Iniciado"
                },
                "phases": [] 
            }
            
            self.data['projects'].append(new_item)
            self.save()
            print(f">>> Proyecto '{name}' añadido exitosamente al JSON.")
        except Exception as e:
            print(f"Error al añadir proyecto: {e}")

    def calculate_metrics(self, project):
        """Calcula porcentajes reales, días y costos en UF."""
        try:
            # Fechas
            end_date_str = project.get('dates', {}).get('contract_end', '').strip()
            if not end_date_str:
                return project
                
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            today = datetime.now()
            diff_days = (end_date - today).days

            total_tasks = 0
            completed_tasks = 0
            total_hh_spent = 0

            # Procesamiento de Fases (L2) y Tareas (L3)
            for phase in project.get('phases', []):
                tasks = phase.get('tasks', [])
                p_total = len(tasks)
                p_done = len([t for t in tasks if str(t.get('status', '')).lower() == 'completada'])
                
                phase['progress'] = round((p_done / p_total * 100), 1) if p_total > 0 else 0
                
                total_tasks += p_total
                completed_tasks += p_done
                total_hh_spent += sum(float(t.get('hh_spent', 0)) for t in tasks)

            # Inyección de métricas calculadas
            project['metrics'].update({
                "days_diff": diff_days,
                "total_progress": round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0,
                "total_hh": total_hh_spent,
                "total_uf": round(total_hh_spent * self.rate_hh_uf, 2),
                "status_label": "Al día" if diff_days >= 0 else "Retrasado"
            })
            return project
        except Exception as e:
            print(f"Error procesando proyecto {project.get('name')}: {e}")
            return project

    def sync(self):
        """Recalcula métricas de todos los proyectos existentes."""
        if not self.data.get('projects'):
            print("No se encontraron proyectos para sincronizar.")
            return

        for i in range(len(self.data['projects'])):
            self.data['projects'][i] = self.calculate_metrics(self.data['projects'][i])
        
        self.save()
        print(">>> Sincronización completa: Métricas actualizadas.")

if __name__ == "__main__":
    engine = ProjectEngine()
    
    # Lógica de ejecución basada en argumentos de la GitHub Action
    if len(sys.argv) == 4:
        # Modo: Añadir Proyecto
        engine.add_project(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 2 and sys.argv[1] == "--sync":
        # Modo: Sincronizar métricas
        engine.sync()
    else:
        print("Uso añadir: python3 manage-projects.py 'Nombre' 'UF' 'Mora'")
        print("Uso sync: python3 manage-projects.py --sync")
