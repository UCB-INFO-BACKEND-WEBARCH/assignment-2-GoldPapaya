from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import and_
from datetime import datetime
from app.models import db, Task, Category
from app.schemas import TaskSchema
from app.jobs import schedule_task_notification

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')
task_schema = TaskSchema()

@tasks_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(task.to_dict()), 200


@tasks_bp.route('', methods=['GET'])
def get_tasks():
    completed = request.args.get('completed', None)
    query = Task.query
    if completed is not None:
        is_completed = completed.lower() == 'true'
        query = query.filter(Task.completed == is_completed)
    
    tasks = query.all()
    return jsonify({'tasks': [task.to_dict() for task in tasks]}), 200


@tasks_bp.route('', methods=['POST'])
def create_task():
    try:
        data = task_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # category_id validation if provided by user
    if data.get('category_id'):
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({'errors': {'category_id': ['Category not found']}}), 400
    
    task = Task(
        title=data.get('title'),
        description=data.get('description'),
        due_date=data.get('due_date'),
        category_id=data.get('category_id'),
        completed=data.get('completed', False)
    )
    db.session.add(task)
    db.session.commit()
    notification_queued = schedule_task_notification(task.id, task.due_date) # call worker
    
    return jsonify({
        #task.todict() would also return the category in the json, but this is not the case in the specification.
        #so here I return everything else explicitly, excluding the category (but keeping category_id).
        'task': {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'category_id': task.category_id,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'updated_at': task.updated_at.isoformat() if task.updated_at else None
        },
        'notification_queued': notification_queued
    }), 201


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    try:
        data = task_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # category_id validation if provided by user
    if 'category_id' in data and data['category_id']:
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({'errors': {'category_id': ['Category not found']}}), 400
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'completed' in data:
        task.completed = data['completed']
    if 'due_date' in data:
        task.due_date = data['due_date']
    if 'category_id' in data:
        task.category_id = data['category_id']
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(task.to_dict()), 200


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': 'Task deleted'}), 200
