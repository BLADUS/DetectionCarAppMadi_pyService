import matplotlib.pyplot as plt
from pymongo import MongoClient
from collections import defaultdict

# Подключение к MongoDB
client = MongoClient('localhost', 27017)
db = client['MadiTracker']
collection = db['data']

# Извлечение данных из коллекции
data = collection.find()

# Подсчет уникальных объектов по track_id
unique_objects = defaultdict(set)
for item in data:
    unique_objects[item['name']].add(item['track_id'])

# Подсчет количества уникальных объектов каждого типа
type_counts = {name: len(track_ids) for name, track_ids in unique_objects.items()}

# **Исправление ошибки:**
# * Установка пакета seaborn (рекомендуется)
#   ```bash
#   pip install seaborn
#   ```
# * Или замена стиля оформления на другой, доступный в matplotlib
#   ```python
#   plt.style.use('ggplot')  # Пример другого стиля
#   ```

# Стилизация графика
try:
    plt.style.use('seaborn-darkgrid')  # Применение стиля seaborn-darkgrid
except OSError:
    print("seaborn-darkgrid style not found. Using a default style instead.")
    plt.style.use('ggplot')  # Пример стиля по умолчанию

fig, ax = plt.subplots()
bars = ax.bar(type_counts.keys(), type_counts.values(), color=['#3498db', '#2ecc71', '#e74c3c', '#f1c40f'], edgecolor='black')

# Добавление тени
for bar in bars:
    bar.set_zorder(2)
    bar.set_edgecolor('black')
    bar.set_linewidth(0.8)
    bar.set_alpha(0.8)

# Настройка шрифтов
plt.xlabel('Тип объекта', fontsize=12, fontweight='bold')
plt.ylabel('Количество уникальных объектов', fontsize=12, fontweight='bold')
plt.title('Количество уникальных типов объектов на видео', fontsize=14, fontweight='bold')

# Настройка осей
ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.7)
ax.xaxis.grid(False)

# Увеличение размера меток на осях
plt.xticks(fontsize=10, rotation=45, ha='right')
plt.yticks(fontsize=10)

# Добавление значений над столбцами
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # Смещение текста
                textcoords="offset points",
                ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()  # Автоматическая подгонка элементов графика
plt.show()
