'use strict';

let stepCounter = 1;
let addStep = document.getElementById('addStep');
let formsContainer = document.getElementById('formsContainer');

addStep.addEventListener('click', () => {createOneMoreForm()});

let newButton = document.createElement('button');
newButton.setAttribute('id', 'addStepNew');
newButton.setAttribute('type', 'button');

function createOneMoreForm() {
        if (addStep) {addStep.remove()}
        stepCounter++;
         // Обновляем текст в элементе
        const stepElement = document.querySelector('.step_preparing');
        stepElement.textContent = `Добавление ${stepCounter} шага приготовления: `;
        // Находим контейнер для форм
        var formsContainer = document.getElementById('formsContainer');

        // Клонируем первую группу полей
        var originalFormGroup = formsContainer.querySelector('.form-group');
        var newFormGroup = originalFormGroup.cloneNode(true);

        // Очищаем значения в новых полях
        var inputs = newFormGroup.querySelectorAll('input, select, textarea');
        inputs.forEach(function(input) {
            console.log(input.value);
            if (input.type !== 'file') {
                input.value = ''; // Очищаем значение поля (кроме файлов)

            }
        });
        // Добавляем новую группу полей в контейнер
        formsContainer.appendChild(newFormGroup);

        // Добавляем новую кнопку
        newButton.textContent = (`Добавить ${stepCounter + 1} шаг `);
        formsContainer.append(newButton);
        newButton.addEventListener('click', () => {createOneMoreForm()});
    }

