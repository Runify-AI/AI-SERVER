from typing import Tuple, Dict, Union
import osmnx as ox


class UserInput:
    def __init__(
        self,
        start_address :str,
        end_address : str,
        arrival_time: str,  # "HH:MM" 형식으로 받음
        preferences: Dict[str, Union[str, list]]
    ):
        self.start_address = start_address,
        self.end_address = end_address,
        self.start_location = geocode(self.start_address)
        self.end_location = geocode(self.end_address)
        self.arrival_time = arrival_time
        self.preferences = preferences

    def __repr__(self):
        return (
            f"UserInput(start={self.start_location}, end={self.end_location}"
        )
        
def geocode(address):
    return ox.geocoder.geocode(address)
        
def get_user_input_console() -> UserInput:
    start_address = input("출발지 주소 입력 >> ")
    end_address = input("도착지 주소 입력 >> ")
    
    print("도착 시간 입력 (예: 08:30):")
    arrival_time = input().strip()
    
    print("선호하는 장소 입력 (쉼표로 구분, 예: park,river,cafe):")
    preferred_places = input().strip().split(",")
    
    print("피하고 싶은 조건 입력 (쉼표로 구분, 예: dark,steep):")
    avoid_conditions = input().strip().split(",")
    
    preferences = {
        "preferred_places": preferred_places,
        "avoid_conditions": avoid_conditions
    }
    
    return UserInput(
        start_address = start_address,
        end_address = end_address,
        arrival_time=arrival_time,
        preferences=preferences
    )

if __name__ == "__main__":
    user_input = get_user_input_console()
    