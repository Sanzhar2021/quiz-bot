// static/script.js

document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('textInput');
    const generateBtn = document.getElementById('generateBtn');
    const loader = document.getElementById('loader');
    const testContainer = document.getElementById('testContainer');
    const quizForm = document.getElementById('quizForm');
    const submitBtn = document.getElementById('submitBtn');
    const scoreDisplay = document.getElementById('scoreDisplay');
    const resultDisplay = document.getElementById('resultDisplay');
    const restartSection = document.getElementById('restartSection');
    const restartBtn = document.getElementById('restartBtn');
    const studentNameInput = document.getElementById('studentName');
    const studentGroupInput = document.getElementById('studentGroup');

    let correctAnswers = {};
    const pointsPerQuestion = 5;

    generateBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        console.log("Кнопка 'Сгенерировать тест' нажата.");
        console.log("Текст из поля ввода:", text);

        if (!text) {
            alert('Пожалуйста, введите текст для генерации теста.');
            return;
        }

        generateBtn.disabled = true;
        textInput.disabled = true;
        loader.classList.remove('hidden');
        testContainer.classList.add('hidden');
        restartSection.classList.add('hidden');
        quizForm.innerHTML = '';
        scoreDisplay.textContent = 'Счёт: 0 / 100';
        resultDisplay.textContent = '';

        try {
            console.log("Отправляем POST-запрос на /generate_test...");
            const response = await fetch('/generate_test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });

            console.log("Ответ от сервера получен. Статус:", response.status);
            const data = await response.json();
            console.log("JSON-данные из ответа:", data);

            if (data.success) {
                renderQuiz(data.questions);
                correctAnswers = data.questions.reduce((acc, q) => {
                    acc[q.question] = q.correct_option;
                    return acc;
                }, {});
                testContainer.classList.remove('hidden');
                submitBtn.style.display = 'block';
            } else {
                alert(`Ошибка: ${data.error}`);
            }
        } catch (error) {
            console.error('Произошла ошибка в JavaScript:', error);
            alert(`Произошла ошибка: ${error.message}`);
        } finally {
            generateBtn.disabled = false;
            textInput.disabled = false;
            loader.classList.add('hidden');
        }
    });

    submitBtn.addEventListener('click', async () => {
        const studentName = studentNameInput.value.trim();
        if (!studentName) {
            alert('Пожалуйста, введите ваше имя.');
            return;
        }

        let score = 0;
        let totalQuestions = 0;
        
        const questions = quizForm.querySelectorAll('.question-block');
        questions.forEach((qBlock, index) => {
            const questionText = qBlock.querySelector('h3').textContent.trim();
            const selectedOption = qBlock.querySelector(`input[name="q${index}"]:checked`);
            
            if (selectedOption) {
                totalQuestions++;
                const selectedValue = selectedOption.value;
                const correctAnswer = correctAnswers[questionText];
                
                const optionLabels = qBlock.querySelectorAll('.option-label');
                optionLabels.forEach(label => {
                    if (label.textContent.trim() === correctAnswer.trim()) {
                        label.classList.add('correct-answer');
                    }
                });

                if (selectedValue.trim() === correctAnswer.trim()) {
                    score += pointsPerQuestion;
                } else {
                    const wrongLabel = selectedOption.closest('.option-label');
                    wrongLabel.classList.add('wrong-answer');
                }
            }
        });

        scoreDisplay.textContent = `Счёт: ${score} / ${pointsPerQuestion * 20}`;
        resultDisplay.textContent = `Вы ответили на ${score / pointsPerQuestion} из 20 вопросов правильно.`;

        console.log("Отправляем результат на сервер.");
        try {
            const response = await fetch('/save_result', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    name: studentName, 
                    group: studentGroupInput.value.trim() || 'Без группы',
                    score: score 
                })
            });
            const resultData = await response.json();
            console.log("Результат сохранения:", resultData);
            if(resultData.success) {
                alert('Ваш результат сохранён.');
            } else {
                alert(`Ошибка при сохранении: ${resultData.error}`);
            }
        } catch (error) {
            console.error('Ошибка при сохранении результата:', error);
            alert('Произошла ошибка при сохранении вашего результата.');
        }

        submitBtn.style.display = 'none';
        restartSection.classList.remove('hidden');
    });

    restartBtn.addEventListener('click', () => {
        location.reload(); // Простой способ перезагрузить страницу
    });

    function renderQuiz(questions) {
        quizForm.innerHTML = '';
        questions.forEach((q, index) => {
            const qBlock = document.createElement('div');
            qBlock.classList.add('question-block');
            
            const qTitle = document.createElement('h3');
            qTitle.textContent = q.question;
            qBlock.appendChild(qTitle);
            
            const optionsList = document.createElement('ul');
            optionsList.classList.add('options-list');
            
            q.options.forEach(option => {
                const li = document.createElement('li');
                li.classList.add('option-item');
                
                const label = document.createElement('label');
                label.classList.add('option-label');
                
                const input = document.createElement('input');
                input.type = 'radio';
                input.name = `q${index}`;
                input.value = option;
                
                label.appendChild(input);
                label.appendChild(document.createTextNode(option));
                li.appendChild(label);
                optionsList.appendChild(li);
            });
            
            qBlock.appendChild(optionsList);
            quizForm.appendChild(qBlock);
        });
    }
});


