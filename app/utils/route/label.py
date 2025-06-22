import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString


def coord_getLabel(coords):
    # 1. LineString 생성 (coords는 (위도, 경도) 순서라고 가정)
    line = LineString([(lng, lat) for lat, lng in coords])

    # 2. 약 100m 버퍼 생성 (단위: degree → m로 환산)
    buffer_polygon = line.buffer(100 / 111000)

    # 3. GeoSeries로 변환 + 좌표계 설정 (WGS84)
    buffer_gdf = gpd.GeoSeries([buffer_polygon], crs="EPSG:4326")
        # 4. OSM 데이터 가져오기 (공원, 카페 등 다양한 피처)
    tags = {
        'leisure': True,
        'amenity': True,
        'highway': True,
        'incline': True,
        'lit': True,
        'bicycle': True,
        'waterway':True,
        'shop': True,
        'railway' :True,
    }

    features = ox.features_from_polygon(buffer_gdf[0], tags=tags)
    
        # 5. 태그별 value 집계
    tag_columns = ['highway', 'leisure', 'amenity', 'incline', 
                   'lit', 'bicycle','waterway','shop','railway']
    dfs = []

    for tag in tag_columns:
        if tag in features.columns:
            counts = features[tag].value_counts(dropna=True)
            df = pd.DataFrame({
                'tag': tag,
                'value': counts.index,
                'count': counts.values
            })
            dfs.append(df)

    tag_summary = pd.concat(dfs, ignore_index=True)

    # print(tag_summary)



    # 2. GeoDataFrame으로 버퍼 폴리곤 변환 및 UTM 변환 (면적 계산용)
    buffer_area = buffer_gdf.area.values[0]

    # 3. 공원(park) 집계
    park_area = 0
    park_count = 0
    park_ratio = 0
    if 'leisure' in features.columns:
        parks = features[features['leisure'] == 'park']
        if not parks.empty:
            parks_utm = parks.to_crs(epsg=32652)
            intersection_areas = parks_utm.geometry.intersection(buffer_gdf[0])
            park_area = intersection_areas.area.sum()
            park_count = len(parks)
            park_ratio = park_area / buffer_area if buffer_area > 0 else 0

    # 4. 하천(river) 집계
    river_area = 0
    river_count = 0
    river_ratio = 0

    if 'waterway' in features.columns:
        rivers = features[features['waterway'] == 'river']
        if not rivers.empty:
            rivers_utm = rivers.to_crs(epsg=32652)
            river_area = rivers_utm.geometry.length.sum()
            river_count = len(rivers)
            river_ratio = river_area / buffer_area if buffer_area > 0 else 0

    # 5. 편의시설(amenity) 개수 집계
    amenity_count = 0
    if 'shop' in features.columns:
        amenity_count = features['shop'].notna().sum()


    # 6. 횡단보도(crossing) 개수 집계
    crossing_count = 0
    if 'highway' in features.columns:
        crossing_count = features['highway'].eq('crossing').sum()
        
    # features: ox.features_from_polygon 등으로 얻은 GeoDataFrame

    # 1. 버스정류장 추출
    if 'highway' in features.columns:
        bus_stops = features[features['highway'] == 'bus_stop']
        bus_stop_coords = [(geom.y, geom.x) for geom in bus_stops.geometry if geom.geom_type == 'Point']
    else:
        bus_stop_coords = []

    # 2. 지하철 출입구 추출
    if 'railway' in features.columns:
        subway_entrances = features[features['railway'] == 'subway_entrance']
        subway_coords = [(geom.y, geom.x) for geom in subway_entrances.geometry if geom.geom_type == 'Point']
    else:
        subway_coords = []

    # 3. 합쳐서 반환
    all_stops = bus_stop_coords + subway_coords



    # 7. 결과 출력
    summary = {
        "park": {
            "count": int(park_count),
            "area": float(park_area),
            "ratio": f"{park_ratio:.2%}",
        },
        "river": {
            "count": int(river_count),
            "area": float(river_area),
            "ratio": f"{river_ratio:.2%}",
        },
        "amenity": {
            "count": int(amenity_count),
        },
        "cross": {
            "count": int(crossing_count),
        }
    }

    
    return summary,all_stops
