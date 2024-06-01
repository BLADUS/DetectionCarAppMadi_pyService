import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient
from sklearn.cluster import DBSCAN
from collections import defaultdict

# Подключение к MongoDB
client = MongoClient('localhost', 27017)
db = client['MadiTracker']
collection = db['data']

# Извлечение данных из коллекции
data = collection.find()

# Группировка данных по track_id
tracks = defaultdict(list)
for item in data:
    x_center = (item['box']['x1'] + item['box']['x2']) / 2
    y_center = (item['box']['y1'] + item['box']['y2']) / 2
    tracks[item['track_id']].append((x_center, y_center))

# Преобразование траекторий в формат, подходящий для DBSCAN
trajectories = []
for track_id, points in tracks.items():
    if len(points) > 1:  # Игнорируем траектории с одной точкой
        trajectories.append(points)

# Функция для развертывания траекторий в массив точек
def flatten_trajectories(trajectories):
    points = []
    labels = []
    for idx, trajectory in enumerate(trajectories):
        for point in trajectory:
            points.append(point)
            labels.append(idx)
    return np.array(points), labels

# Применение DBSCAN для кластеризации точек траекторий
points, labels = flatten_trajectories(trajectories)
db = DBSCAN(eps=50, min_samples=2).fit(points)
cluster_labels = db.labels_

# Визуализация результатов кластеризации
plt.figure(figsize=(10, 8))
unique_labels = set(cluster_labels)

for k in unique_labels:
    if k == -1:
        # Черные точки для шумовых элементов
        color = 'k'
        marker = 'x'
    else:
        # Цветные точки для кластеров
        color = plt.cm.Spectral(float(k) / len(unique_labels))
        marker = 'o'
    
    class_member_mask = (cluster_labels == k)
    xy = points[class_member_mask]
    plt.plot(xy[:, 0], xy[:, 1], marker, markerfacecolor=color, markeredgecolor='k', markersize=6)

plt.title('DBSCAN Кластеризация траекторий движения транспорта')
plt.xlabel('X координата')
plt.ylabel('Y координата')
plt.show()
