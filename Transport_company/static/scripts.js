// static/scripts.js

document.addEventListener("DOMContentLoaded", function() {
    // Обработчик события DOMContentLoaded гарантирует, что скрипт выполнится после загрузки всего DOM

    // Получаем все строки таблицы и добавляем им обработчики событий
    var tableRows = document.querySelectorAll("table tbody tr");

    tableRows.forEach(function(row) {
        row.addEventListener("mouseover", function() {
            // Подсвечиваем строку при наведении курсора мыши
            this.style.backgroundColor = "#f0f0f0";
        });

        row.addEventListener("mouseout", function() {
            // Восстанавливаем цвет после ухода курсора мыши
            this.style.backgroundColor = "";
        });
    });
});