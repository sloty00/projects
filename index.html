---
layout: default
---

<style>
  /* Reset y Base */
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { 
    background-color: #0a0a0c !important; 
    color: #ffffff !important; 
    font-family: 'Inter', -apple-system, sans-serif;
    display: flex !important;
    justify-content: center !important;
    padding: 40px 20px !important;
    min-height: 100vh;
  }

  .glass-container { 
    background: rgba(255, 255, 255, 0.02) !important; 
    border: 1px solid rgba(255, 255, 255, 0.1) !important; 
    padding: 2.5rem !important; 
    border-radius: 24px !important; 
    width: 100% !important; 
    max-width: 950px !important; 
    backdrop-filter: blur(12px);
  }

  /* Header */
  .dashboard-header {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 1.5rem;
    margin-bottom: 2rem;
  }
  .dashboard-header h1 { color: #00d4ff; font-size: 2.2rem; }
  .dashboard-header p { color: #a0a0a0; font-size: 0.9rem; }

  /* Métricas L1 */
  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2.5rem;
  }
  .metric-card {
    background: rgba(255, 255, 255, 0.04);
    padding: 1.2rem;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.05);
  }
  .metric-label { font-size: 0.7rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
  .metric-value { font-size: 1.3rem; font-weight: 700; margin-top: 5px; }

  /* Niveles L2 y L3 */
  .phase-container {
    margin-top: 2rem;
    padding-left: 1.5rem;
    border-left: 1px solid rgba(255, 255, 255, 0.1);
  }
  .phase-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }
  .task-list { list-style: none; padding-left: 0.5rem; }
  .task-item {
    display: flex;
    justify-content: space-between;
    padding: 0.6rem;
    border-radius: 8px;
    margin-bottom: 0.4rem;
    background: rgba(255, 255, 255, 0.02);
    font-size: 0.9rem;
  }

  /* Progress Bar */
  .progress-bar-bg { width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 10px; margin-top: 10px; overflow: hidden; }
  .progress-fill { height: 100%; background: linear-gradient(90deg, #00d4ff, #00ff88); transition: width 0.5s ease; }
</style>

<div class="glass-container">
    <header class="dashboard-header">
        <h1>Project Dashboard</h1>
        <p>Sistema de control GitOps • Última actualización: {{ site.data.project-schedule.metadata.last_updated }}</p>
    </header>

    {% for project in site.data.project-schedule.projects %}
    <section class="project-block" style="margin-bottom: 4rem;">
        
        <!-- Nivel 1: Métricas de Proyecto -->
        <div class="metrics-grid">
            <div class="metric-card">
                <span class="metric-label">Días de Plazo</span>
                <div class="metric-value" style="color: {% if project.metrics.days_diff >= 0 %}#00ff88{% else %}#ff4d4d{% endif %};">
                    {{ project.metrics.days_diff }} d {% if project.metrics.days_diff >= 0 %}a favor{% else %}atrasado{% endif %}
                </div>
            </div>
            <div class="metric-card">
                <span class="metric-label">Facturación (H/H)</span>
                <div class="metric-value" style="color: #00d4ff;">{{ project.metrics.total_uf }} UF</div>
                <small style="font-size: 0.7rem; opacity: 0.5;">{{ project.metrics.total_hh }} hrs @ 0.25 UF</small>
            </div>
            <div class="metric-card">
                <span class="metric-label">Avance Global</span>
                <div class="metric-value">{{ project.metrics.total_progress | round }}%</div>
                <div class="progress-bar-bg">
                    <div class="progress-fill" style="width: {{ project.metrics.total_progress }}%;"></div>
                </div>
            </div>
        </div>

        <h2 style="margin-bottom: 1.5rem; font-size: 1.5rem;">{{ project.name }}</h2>

        <!-- Nivel 2: Fases -->
        {% for phase in project.phases %}
        <div class="phase-container">
            <div class="phase-header">
                <h4 style="color: #a0a0a0; text-transform: uppercase; font-size: 0.8rem;">Fase: {{ phase.phase_name }}</h4>
                <span style="font-size: 0.8rem; color: #00ff88;">{{ phase.progress | round }}%</span>
            </div>

            <!-- Nivel 3: Tareas -->
            <ul class="task-list">
                {% for task in phase.tasks %}
                <li class="task-item">
                    <span style="{% if task.status == 'completada' %}opacity: 0.4; text-decoration: line-through;{% endif %}">
                        • {{ task.task_name }}
                    </span>
                    <span style="font-size: 0.75rem; color: #888;">
                        {{ task.hh_spent }} hrs | 
                        <strong style="color: {% if task.status == 'completada' %}#00ff88{% else %}#eab308{% endif %};">
                            {{ task.status }}
                        </strong>
                    </span>
                </li>
                {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </section>
    {% else %}
    <div style="text-align: center; padding: 5rem; opacity: 0.4;">
        <p>No hay proyectos activos.</p>
        <code>python3 manage_projects.py "Nuevo Proyecto" "2026-05-01" "2026-06-01"</code>
    </div>
    {% endfor %}
</div>
