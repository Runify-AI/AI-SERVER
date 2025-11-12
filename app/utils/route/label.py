import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, box

def coord_getLabel(coords):
    if not coords or len(coords) < 2:
        return None

    # 1️⃣ LineString 생성
    line = LineString([(lng, lat) for lat, lng in coords])
    buffer_dist_deg = 100 / 111000  # 약 100m
    minx, miny, maxx, maxy = line.bounds
    bbox = (maxy + buffer_dist_deg, miny - buffer_dist_deg, maxx + buffer_dist_deg, minx - buffer_dist_deg)  # (north, south, east, west)

    # 2️⃣ 필요한 태그만 선택
    tags = {
        "leisure": ["park"],
        "waterway": ["river"],
        "highway": ["crossing"],
        "shop": True,
    }

    # 3️⃣ OSM 데이터 수집 (EPSG:4326)
    try:
        features = ox.features_from_bbox(*bbox, tags=tags)
    except Exception as e:
        print(f"OSM fetch error: {e}")
        return None

    if features.empty:
        return {
            "park": {"count": 0, "area": 0, "ratio": 0},
            "river": {"count": 0, "area": 0, "ratio": 0},
            "amenity": {"count": 0},
            "cross": {"count": 0},
        }

    # 4️⃣ 좌표계 변환 (UTM Zone 자동 감지)
    utm_crs = ox.utils_geo.bearing.get_utm_crs(line.centroid.y, line.centroid.x)
    features = features.to_crs(utm_crs)
    line_utm = gpd.GeoSeries([line], crs="EPSG:4326").to_crs(utm_crs).iloc[0]
    buffer_polygon = line_utm.buffer(100)  # 100m 버퍼
    buffer_gdf = gpd.GeoSeries([buffer_polygon], crs=utm_crs)
    buffer_area = buffer_gdf.area.values[0]

    # 5️⃣ 공원 (park)
    parks = features[features.get("leisure") == "park"]
    park_area, park_count = 0, 0
    if not parks.empty:
        parks = parks[parks.geometry.intersects(buffer_polygon)]
        park_area = parks.intersection(buffer_polygon).area.sum()
        park_count = len(parks)
    park_ratio = park_area / buffer_area if buffer_area > 0 else 0

    # 6️⃣ 하천 (river)
    rivers = features[features.get("waterway") == "river"]
    river_area, river_count = 0, 0
    if not rivers.empty:
        rivers = rivers[rivers.geometry.intersects(buffer_polygon)]
        river_area = rivers.intersection(buffer_polygon).length.sum()
        river_count = len(rivers)
    river_ratio = river_area / buffer_area if buffer_area > 0 else 0

    # 7️⃣ 편의시설 (shop)
    amenity_count = features["shop"].notna().sum() if "shop" in features.columns else 0

    # 8️⃣ 횡단보도 (crossing)
    cross_count = features["highway"].eq("crossing").sum() if "highway" in features.columns else 0

    return {
        "park": {"count": int(park_count), "area": float(park_area), "ratio": float(park_ratio)},
        "river": {"count": int(river_count), "area": float(river_area), "ratio": float(river_ratio)},
        "amenity": {"count": int(amenity_count)},
        "cross": {"count": int(cross_count)},
    }
