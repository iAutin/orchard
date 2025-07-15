document.addEventListener('DOMContentLoaded', function() {
    // Connect hierarchical unfinished tasks
    document.querySelectorAll('.task-square:not(.completed-task)').forEach(function(el) {
        var parentId = el.getAttribute('data-parent-id');
        if (parentId) {
            var parentEl = document.getElementById('task-' + parentId);
            if (parentEl) {
                new LeaderLine(parentEl, el, {color: 'black', size: 2, path: 'fluid'});
            }
        }
    });

    // Connect completed tasks sequentially (trunk)
    const completed = document.querySelectorAll('.completed-task');
    for (let i = 0; i < completed.length - 1; i++) {
        new LeaderLine(completed[i], completed[i + 1], {color: 'black', size: 2, path: 'straight'});
    }
});