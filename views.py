#Импортируем необходимые библиотеки
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import base64
import io
import matplotlib.pyplot as plt

@csrf_exempt #Отключаем защиту от CSRF для упрощения разработки
def index(request): #Создаем функцию для обработки запросов
    # Инициализация истории в сессии
    history = request.session.get('history', [])
    
    result = None
    chart_url = None

    # Обработка POST-запроса
    if request.method == "POST":
        user_prompt = request.POST.get("prompt", "")

        # Логика фильтрации
        forbidden = ["DROP", "DELETE", "EXEC(",  "script", "alert(", "<script>", "def", "import", "eval("]
        is_safe = not any(word in user_prompt.upper() for word in forbidden)
        status = "Безопасно" if is_safe else "Заблокировано"

        # Шифрование
        encrypted = base64.b64encode(f"{user_prompt}:ModelGuard".encode()).decode() if is_safe else "Не зашифровано"

        # Сохранение результата текущего ввода
        result = {
            "status": status,
            "encrypted": encrypted,
            "prompt": user_prompt
        }

        # Добавление нового статуса в историю сессии
        history = request.session.get('history', []) 
        history.append(status)                      
        request.session['history'] = history        
        request.session.modified = True
        

    history = request.session.get('history', []) # Получаем историю из сессии
    if history:
        plt.figure(figsize=(5, 4))

        # Считаем количество каждого статуса
        safe_count = history.count("Безопасно")
        blocked_count = history.count("Заблокировано")

        labels = ['Безопасно', 'Заблокировано']
        counts = [safe_count, blocked_count]

        # Отрисовка
        plt.bar(labels, counts, color=['green', 'red'])
        plt.title(f"Всего обработано запросов: {len(history)}")
        plt.ylabel("Количество")

        # Конвертация в картинку для HTML
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        chart_url = base64.b64encode(buf.getvalue()).decode()
        plt.close()

    # Передача данных в шаблон
    context = {
        "result": result,
        "chart": chart_url,
        "total_count": len(history)
    }
    return render(request, "security_filter/index.html", context)