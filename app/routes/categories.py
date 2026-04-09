from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models import db, Category
from app.schemas import CategorySchema

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)

@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    res = category.to_dict()
    res['tasks'] = [{'id': task.id, 'title': task.title, 'completed': task.completed} for task in category.tasks]
    
    return jsonify(res), 200

@categories_bp.route('', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    res = []
    for category in categories:
        cat_data = category.to_dict()
        cat_data['task_count'] = len(category.tasks)
        res.append(cat_data)
    
    return jsonify({'categories': res}), 200

@categories_bp.route('', methods=['POST'])
def create_category():
    try:
        data = category_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # check if the category already exist
    existing = Category.query.filter_by(name=data.get('name')).first()
    if existing:
        return jsonify({'errors': {'name': ['Category with this name already exists.']}}), 400
    
    category = Category(
        name=data.get('name'),
        color=data.get('color')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify(category.to_dict()), 201

@categories_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get(category_id)
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    # dont delete if category has tasks
    if len(category.tasks) > 0:
        return jsonify({'error': 'Cannot delete category with existing tasks. Move or delete tasks first.'}), 400
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': 'Category deleted'}), 200
