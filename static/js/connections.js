// static/js/connections.js
document.addEventListener('DOMContentLoaded', function() {
    // Static example: Connect trunk to a task and task-to-task
    // Replace with dynamic logic based on your task relationships
    const trunk = document.getElementById('trunk');
    const tasks =document.querySelectorAll('.task-card');
    if (trunk && tasks.length > 0) {
        new LeaderLine(
            trunk,
            tasks[0],
            {color: 'black', size: 2}
        );
        for (let i = 0; i < tasks.length - 1; i++) {
            new LeaderLine(
                tasks[i],
                tasks[i + 1],
                {color: 'black', size: 2}
            );
        }
    }
});