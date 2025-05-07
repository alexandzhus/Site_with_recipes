'use strict';

let stepCounter = 1;
let addStep = document.getElementById('addStep');
let formsContainer = document.getElementById('formsContainer');

addStep.addEventListener('click', () => {createOneMoreForm()});

function createOneMoreForm() {
        let currentAddButton = document.querySelector('#addStep, #addStepNew');
        if (currentAddButton) {
            currentAddButton.remove();
        }
        stepCounter++;
         // Обновляем текст в элементе
        const stepElementAddStep = document.querySelector('.step_preparing');
        stepElementAddStep.textContent = `Добавление ${stepCounter} шага приготовления: `;
        // Находим контейнер для форм
        let formsContainer = document.getElementById('formsContainer');

        // Клонируем первую группу полей
        let originalFormGroup = formsContainer.querySelector('.form-group');
        let newFormGroup = originalFormGroup.cloneNode(true);

        // Очищаем значения в новых полях
        let inputs = newFormGroup.querySelectorAll('input, select, textarea');
        inputs.forEach(function(input) {
            console.log(input.value);
                if (input.type === 'file') {
                    // Особый случай для input[type="file"]
                    input.value = ''; // Очищаем значение файлового поля
                    // Если есть превью изображения - удаляем его
                    let preview = input.nextElementSibling;
                    if (preview && preview.classList.contains('image-preview')) {
                            preview.remove();
                        }
                } else {
                    input.value = ''; // Очищаем значение остальных полей
                }
            });
        // Добавляем новую группу полей в контейнер
        formsContainer.appendChild(newFormGroup);

        // Добавляем новую кнопку
        let newButton = document.createElement('button');
        newButton.setAttribute('id', 'addStepNew');
        newButton.setAttribute('type', 'button');
        newButton.classList.add('dynamic-step-button');
        newButton.textContent = (`Добавить ${stepCounter + 1} шаг `);
        formsContainer.append(newButton);
        newButton.addEventListener('click', () => {createOneMoreForm()});
    }

