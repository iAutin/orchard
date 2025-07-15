from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import random
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'orchard.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)

# Expanded list of pastel colors
pastel_colors = [
    '#FFD1DC', '#FFA07A', '#FFB6C1', '#FFC0CB', '#FFE4E1',
    '#FFFACD', '#E6E6FA', '#D8BFD8', '#DDA0DD', '#EE82EE',
    '#98FB98', '#AFEEEE', '#ADD8E6', '#B0E0E6', '#87CEFA',
    '#B0C4DE', '#F0E68C', '#FFEFD5', '#FFF5EE', '#F5F5DC',
    '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#F4EBD3',
    '#DED3C4', '#98A1BC', '#687FE5', '#EBD6FB', '#FEEBF6',
    '#FCD8CD', '#E0BBE4', '#957DAD', '#D291BC', '#FEC8D8',
    '#A9B5D9', '#F2A477', '#F29472', '#F2C4C4', '#FFDADA',
    '#FFE5C5', '#FFFDC7', '#DFFFC6', '#CCE8DB', '#C1D4E3',
    '#BEB4D6', '#FADAE2', '#FF99CC', '#FFCCFF', '#CC99FF',
    '#CCCCFF', '#77DD77', '#89CFFF', '#99C5C4', '#9ADEDB',
    '#FFADAD', '#FFD6A5', '#FDFFB6', '#CAFFBF', '#9BF6FF',
    '#A0C4FF', '#BDB2FF', '#FFC6FF', '#66C5CC', '#F6CF71',
    '#F89C74', '#DCB0F2', '#87C55F', '#9EB9F3', '#FE88B1',
    '#C9DB74', '#8BE0A4', '#B497E7'
]

# Models
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    color = db.Column(db.String(7), default=lambda: random.choice(pastel_colors))
    tasks = db.relationship('Task', backref='project', lazy=True, cascade="all, delete-orphan")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    color = db.Column(db.String(7), default='#FFFFFF')
    due_date = db.Column(db.DateTime, nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

# Helper function for sorting projects by earliest due date
def get_earliest_due(project):
    due_dates = [t.due_date for t in project.tasks if not t.completed and t.due_date]
    return min(due_dates) if due_dates else None

# Routes
@app.route('/')
def index():
    projects = Project.query.all()
    # Sort projects: those with earliest due first, no due last
    projects = sorted(projects, key=lambda p: (get_earliest_due(p) is None, get_earliest_due(p) or datetime(9999, 12, 31)))
    return render_template('index.html', projects=projects)

@app.route('/project/<int:project_id>')
def project_tree(project_id):
    project = Project.query.get_or_404(project_id)
    unfinished_tasks = Task.query.filter_by(project_id=project_id, completed=False).order_by(Task.priority).all()
    completed_tasks = Task.query.filter_by(project_id=project_id, completed=True).order_by(Task.id.desc()).all()
    priorities = sorted(set(task.priority for task in unfinished_tasks))
    return render_template('project_tree.html', project=project, unfinished_tasks=unfinished_tasks, 
                           completed_tasks=completed_tasks, priorities=priorities)

@app.route('/orchard')
def orchard():
    projects = Project.query.all()
    # Sort projects by earliest due date
    projects = sorted(projects, key=lambda p: (get_earliest_due(p) is None, get_earliest_due(p) or datetime(9999, 12, 31)))
    for project in projects:
        project.priority_1_tasks = Task.query.filter_by(project_id=project.id, priority=1, completed=False).all()
    return render_template('orchard.html', projects=projects)

@app.route('/project/add', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            new_project = Project(name=name)
            db.session.add(new_project)
            db.session.commit()
            flash('Project added successfully!', 'success')
            return redirect(url_for('index'))
    return render_template('add_project.html')

@app.route('/task/add/<int:project_id>', methods=['GET', 'POST'])
def add_task(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        description = request.form.get('description')
        priority = request.form.get('priority', type=int)
        color = request.form.get('color')  # Get the selected color (could be None or empty)
        due_date_str = request.form.get('due_date')
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None
        
        # If no color is selected or it's invalid, pick a random pastel color
        if not color or color not in pastel_colors:
            color = random.choice(pastel_colors)
        
        if description and priority:
            new_task = Task(description=description, priority=priority, project_id=project.id, 
                            color=color, due_date=due_date)
            db.session.add(new_task)
            db.session.commit()
            flash('Task added successfully!', 'success')
            return redirect(url_for('project_tree', project_id=project.id))
    return render_template('add_task.html', project=project, pastel_colors=pastel_colors)

@app.route('/task/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    return redirect(url_for('project_tree', project_id=task.project_id))

@app.route('/task/<int:task_id>/uncomplete', methods=['POST'])
def uncomplete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = False
    db.session.commit()
    return redirect(url_for('project_tree', project_id=task.project_id))

@app.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('project_tree', project_id=project_id))

@app.route('/project/<int:project_id>/delete', methods=['POST'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project
    if request.method == 'POST':
        description = request.form.get('description')
        priority = request.form.get('priority', type=int)
        color = request.form.get('color')  # Get the selected color (could be None or empty)
        due_date_str = request.form.get('due_date')
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None
        
        # If no color is selected or it's invalid, pick a random pastel color
        if not color or color not in pastel_colors:
            color = random.choice(pastel_colors)
        
        if description and priority:
            task.description = description
            task.priority = priority
            task.color = color
            task.due_date = due_date
            db.session.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('project_tree', project_id=task.project_id))
    return render_template('edit_task.html', task=task, project=project, pastel_colors=pastel_colors)

@app.route('/task_list')
def task_list():
    projects = Project.query.all()
    # Sort projects by earliest due date
    projects = sorted(projects, key=lambda p: (get_earliest_due(p) is None, get_earliest_due(p) or datetime(9999, 12, 31)))
    for project in projects:
        project.tasks_sorted = Task.query.filter_by(project_id=project.id, completed=False).order_by(Task.priority.asc()).all()
    return render_template('task_list.html', projects=projects)

@app.route('/stats')
def stats():
    projects = Project.query.all()
    stats = []
    total_completed = 0
    total_outstanding = 0
    for p in projects:
        completed = Task.query.filter_by(project_id=p.id, completed=True).count()
        outstanding = Task.query.filter_by(project_id=p.id, completed=False).count()
        stats.append({'project': p, 'completed': completed, 'outstanding': outstanding, 'total': completed + outstanding})
        total_completed += completed
        total_outstanding += outstanding
    return render_template('stats.html', stats=stats, total_completed=total_completed, total_outstanding=total_outstanding)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001, host='0.0.0.0')