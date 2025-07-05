import yaml 
import csv
import os 
from typing import List, Tuple
from .definitions import ActionType, str_to_action

def parse_csv(file: os.Path) -> List[Tuple[str, int, ActionType]]:
    
    event_sequence = []

    with open(file, newline='') as test_defintion:
        
        reader = csv.reader(test_defintion, delimiter=' ', quotechar='|')

        for row in reader:
            
            try:
                uid = row[0]
                t_ms = row[1]
                action_str = row[2]
            except Exception as err:
                raise err
            
            action = str_to_action(action_str)
            
            if action == ActionType.NOT_IMPLEMENTED:
                raise Exception(f"Invalid Action Type: '{action_str}'")

            row_tuple = (uid, t_ms, action)
            event_sequence.append(row_tuple)

    return event_sequence

