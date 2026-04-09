from marshmallow import Schema, fields, validate

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(max=50))
    color = fields.Str(required=False, allow_none=True, validate=validate.Length(max=7))

class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(max=100))
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))
    completed = fields.Bool(load_default=False)
    due_date = fields.DateTime(required=False, allow_none=True)
    category_id = fields.Int(required=False, allow_none=True)
    category = fields.Nested(CategorySchema, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
