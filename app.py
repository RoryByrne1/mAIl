from flask import Flask, request, jsonify, send_from_directory
import json
import os
from outlookscraper import run as outlookscrape

app = Flask(__name__, static_folder='.', static_url_path='')
tasks_file_path = 'tasks.json'

# Ensure the tasks file exists
if not os.path.exists(tasks_file_path):
    with open(tasks_file_path, 'w') as f:
        json.dump({"todo": [], "summary": []}, f)

@app.route('/')
def index():
    outlookscrape()
    return send_from_directory('.', 'index.html')

@app.route('/tasks', methods=['GET'])
def get_tasks():
    with open(tasks_file_path, 'r') as f:
        tasks = json.load(f)
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    print(request.json)
    new_task = request.json.get('task')
    task_type = request.args.get('type')
    with open(tasks_file_path, 'r') as f:
        tasks = json.load(f)
    tasks[task_type].append(new_task)
    with open(tasks_file_path, 'w') as f:
        json.dump(tasks, f)
    return jsonify({'task': new_task}), 201

@app.route('/tasks/<int:task_index>', methods=['DELETE'])
def delete_task(task_index):
    task_type = request.args.get('type')
    with open(tasks_file_path, 'r') as f:
        tasks = json.load(f)
    if task_type in tasks and 0 <= task_index < len(tasks[task_type]):
        tasks[task_type].pop(task_index)
        with open(tasks_file_path, 'w') as f:
            json.dump(tasks, f)
        return f'{task_type} task deleted', 200
    return 'task not found', 404

if __name__ == '__main__':
    app.run(debug=True)