const aNewTask = (taskText, index, type) => {
    const newTask = document.createElement('li');
    newTask.className = 'list-group-item p-2 d-flex justify-content-between align-items-center';
    const buttonText = type === 'todo' ? 'done <i class="bi bi-check-lg"></i>' : 'read <i class="bi bi-check-lg"></i>';
    console.log("tried");
    const pipe = taskText.indexOf('|');
    if (pipe === -1) {
        newTask.innerHTML = `
            ${taskText}
            <button class="btn btn-success btn-sm ms-2 delete-task" data-index="${index}" data-type="${type}">${buttonText}</button>
        `;
    } else {
        newTask.innerHTML = `
            ${taskText.slice(0, pipe)}
            (Due: ${taskText.slice(pipe+1)})
            <button class="btn btn-success btn-sm ms-2 delete-task" data-index="${index}" data-type="${type}">${buttonText}</button>
        `;
    }
    return newTask;
}

const updateTaskIndices = (type) => {
    const taskList = document.getElementById(`${type}-list`);
    Array.from(taskList.children).forEach((task, index) => {
        task.querySelector('.delete-task').setAttribute('data-index', index);
    });
}

const newTaskDeleteStuff = (newTask, type) => {
    newTask.querySelector('.delete-task').addEventListener('click', function() {  // new listener for delete
        const taskIndex = this.getAttribute('data-index');
        fetch(`/tasks/${taskIndex}?type=${type}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                const taskList = document.getElementById(`${type}-list`);
                taskList.removeChild(newTask);
                updateTaskIndices(type);
            }
        });
    });
}

const intoToDo = (tasks, type) => {    
    const taskList = document.getElementById(`${type}-list`);
    tasks.forEach((taskText, index) => {
        const newTask = aNewTask(taskText, index, type);
        taskList.appendChild(newTask);  // add to the task list
        newTaskDeleteStuff(newTask, type);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    fetch('/tasks')  // sends a GET request
        .then(response => response.json())  // converts the response into json format
        .then(tasks => {
            intoToDo(tasks.todo, 'todo'); // processes the list of todo tasks
            intoToDo(tasks.summary, 'summary'); // processes the list of summary tasks
        });
});

// document.getElementById('add-todo').addEventListener('click', function() {  // event listener, listens for 'add-todo'
//     const taskInput = document.getElementById('new-todo');  // get input field from 'new-todo'
//     const taskText = taskInput.value.trim();  // get the text
//     if (taskText !== '') {
//         fetch('/tasks?type=todo', {  // POST request
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'  // content type is JSON
//             },
//             body: JSON.stringify({ task: taskText })  // converts task text to JSON string, included in request body
//         })
//         .then(response => response.json())
//         .then(data => {
//             const taskList = document.getElementById('todo-list');  // gets the unordered list element
//             const index = taskList.children.length;
//             const newTask = aNewTask(taskText, index, 'todo');
//             taskList.appendChild(newTask);  // add to the task list
//             taskInput.value = '';
//             newTaskDeleteStuff(newTask, 'todo');
//             updateTaskIndices('todo');
//         });
//     }
// });

// // REFRESHING
// document.getElementById('refresh').addEventListener('click', function() {  // event listener, listens for 'add-todo'
//     console.log("help");
//     fetch('/');
// });