from typing import Dict, Any
import json
from violations_records.data_manager.models import ViolationEvent, PersonInfo

class ViolationDataProcessor:
    @staticmethod
    def process_violation_data(payload: Dict[Any, Any]) -> ViolationEvent:
        # 創建違規事件記錄
        violation_data = {
            'violation_type': payload['violation']['type'],
            'details': payload['violation']['details'],
            'image_url': payload['violation']['imageUrl'],
            'start_time': payload['violation']['time']['start'],
            'end_time': payload['violation']['time']['end'],
            'camera_id': payload['camera_id'],
            'scene_id': payload['scene_id'],
            'image_path': payload['image_path']
        }
        
        violation_event = ViolationEvent.objects.create(**violation_data)
        
        # 創建人員信息記錄
        person_data = {
            'violation_event': violation_event,
            'person_role': payload['person']['person_role'],
            'person_id': payload['person']['person_id'],
            'equipment': json.dumps(payload['person']['person_equipment'])
        }
        
        PersonInfo.objects.create(**person_data)
        
        return violation_event