// static/js/color_picker.js
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.color-swatch').forEach(function(swatch) {
        swatch.addEventListener('click', function() {
            document.querySelectorAll('.color-swatch').forEach(function(s) {
                s.classList.remove('selected');
            });
            this.classList.add('selected');
            document.getElementById('selected-color').value = this.getAttribute('data-color');
        });
    });
});