from sklearn.cluster import DBSCAN
import numpy as np

def cluster_waypoints(G, eps_meters=200):
    """
    가까운 경유지들을 하나의 클러스터로 묶고,
    각 클러스터의 대표 지점을 반환한다.
    """
    
    coords = []
    for node,data in G.nodes(data=True):
        lat = float(data['y'])
        lon = float(data['x'])
        coords.append((lat,lon))

    coords = np.array(coords)
    kms_per_radian = 6371.0088
    epsilon = eps_meters / 1000.0 / kms_per_radian

    db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine')
    labels = db.fit_predict(np.radians(coords))

    clustered_centers = []
    for label in set(labels):
        cluster_points = coords[labels == label]
        # 평균 좌표를 클러스터 대표로 설정
        centroid = tuple(np.mean(cluster_points, axis=0))
        clustered_centers.append(centroid)

    return clustered_centers

from sklearn.cluster import KMeans
import numpy as np

def cluster_waypoints_kmeans(G, n_clusters=10):
    """
    그래프 G의 노드 좌표를 kmeans로 클러스터링하고,
    각 클러스터의 대표 지점(중심점)을 반환한다.
    """
    
    coords = []
    for node, data in G.nodes(data=True):
        lat = float(data['y'])
        lon = float(data['x'])
        coords.append((lat, lon))

    coords = np.array(coords)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(coords)

    clustered_centers = []
    for i in range(n_clusters):
        cluster_points = coords[labels == i]
        # kmeans.cluster_centers_가 바로 중심점임
        centroid = tuple(kmeans.cluster_centers_[i])
        clustered_centers.append(centroid)

    return clustered_centers

import matplotlib.pyplot as plt

def plot_clusters(G, cluster_func, n_clusters=10, title="Clusters"):
    """
    G: 그래프
    cluster_func: 클러스터링 함수 (G를 인자로 받고 좌표 리스트 반환)
    """
    coords = []
    for node, data in G.nodes(data=True):
        lat = float(data['y'])
        lon = float(data['x'])
        coords.append((lat, lon))
    coords = np.array(coords)
    
    
    clustered_centers = cluster_func(G,n_clusters)

    plt.figure(figsize=(10, 8))
    plt.title(title)

    # 원본 노드 좌표 산점도 (작은 점)
    plt.scatter(coords[:,1], coords[:,0], c='lightgray', label='Nodes', s=10)

    # 클러스터 대표점 (큰 점, 붉은색)
    centers = np.array(clustered_centers)
    plt.scatter(centers[:,1], centers[:,0], c='red', label='Cluster Centers', s=100, marker='X')

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.show()