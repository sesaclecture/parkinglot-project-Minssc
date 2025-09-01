from enum import Enum

hourly_bill = 10000

class Action(Enum):
    PARK = "1"
    DEPART = "2"
    QUIT = "exit"

registered_plates = {'1111', '1421', '5151'} # 50%

class ParkingTower:
    def __init__(self, height=3):
        self.depth = height
        self.floors = [[{"slot": None, "time": None} for _ in range(10)] for _ in range(height)]
        self.rfloor = 0
        self.rslot = 0

    def show(self):
        for idx, floors in enumerate(self.floors):
            print(f"Floor {idx} slot status:")
            for slot in floors:
                print(f'[{'X' if slot["slot"] else ' '}]', end=' ')
            print()
    
    def recommend(self):
        for idx, floors in enumerate(self.floors):
            for _idx, slot in enumerate(floors):
                if slot['slot'] is None:
                    print(f"Recommended parking slot is: Floor {idx} slot {_idx}")
                    self.rfloor = idx
                    self.rslot = _idx
                    return
        print("There is no free slot to park!")
        self.rfloor = None
        self.rslot = None
        return 1

    def park(self, plate, time, floor = None, slot = None):
        """return 1 on error"""
        if floor is None or slot is None: # park at recommended slot
            floor = self.rfloor
            slot = self.rslot
        if floor > len(self.floors):
            return 1
        if slot > len(self.floors[0]):
            return 1
        if self.floors[floor][slot]["slot"]:
            print("slot already taken")
            return 1
        self.floors[floor][slot]["slot"] = plate
        self.floors[floor][slot]["time"] = time
        self.show()

    def depart(self, floor, slot):
        slot = self.floors[floor][slot]
        slot['slot'] = None
        slot['time'] = None
        self.show()
    
    def find(self, plate):
        """return (floor, slot)"""
        for idx, floors in enumerate(self.floors):
            for _idx, slot in enumerate(floors):
                if slot["slot"] == plate:
                    return (idx, _idx)
        return (None, None)


class Time:
    def __init__(self, tstr = "0000"):
        if not tstr.isnumeric() or len(tstr) != 4:
            raise Exception(f"Invalid time string {tstr}")
        self.hour = int(tstr[0:2])
        self.minutes = int(tstr[2:4])
        if (r := self.validate()):
            raise Exception(f"Invalid time string {tstr}: {r}")
        
    @property
    def total_mins(self):
        """total minutes"""
        return self.hour * 60 + self.minutes
    
    def validate(self):
        """returns nothing when valid."""
        if not (0 <= self.hour <= 24):
            return 'Invalid Hour'
        if not (0 <= self.minutes <= 60):
            return 'Invalid Minutes'
        
    def diff(self, other): 
        """returns difference in minutes"""
        ret = (other.hour - self.hour) * 60 
        ret += abs(other.minutes - self.minutes)
        return ret
    
tower = ParkingTower()

while True:
    action = input("Select action (park:1, depart:2, quit:exit): ")

    match Action(action):
        case Action.PARK:
            print("Welcome!")
            tower.show()
            if tower.recommend():
                print("Our tower is full.")
                continue
            plate = input("Enter your plate number: ")
            try:
                time = Time(input("Enter time (HHMM ex:0930): "))
            except Exception as e:
                print(f"time: {e}")
                continue
            floor = input("Enter the floor to park in (r to park at recommended slot): ")
            if floor == 'r':
                if not tower.park(plate, time):
                    print("Parked at recommended slot")
                continue
            slot = int(input(f"Enter the slot to park in floor {floor}: "))
            r = tower.park(plate, time, int(floor), slot)
            if not r:
                print(f"Successfully parked at floor {floor} slot {slot}")

        case Action.DEPART:
            plate = input("Enter your plate number: ")
            floor, slot = tower.find(plate)
            if floor is None:
                print(f"Plate {plate} is not parked here.")
                continue
            try:
                time = Time(input("Enter time (HHMM ex:0930): "))
            except Exception as e:
                print(f"time: {e}")
                continue
            data = tower.floors[floor][slot]
            if data['time'].total_mins > time.total_mins:
                print('Depart time must be later than park time.')
                continue
            diff = data['time'].diff(time)
            hours = round(diff / 60 + 0.5)
            bill = hourly_bill * hours
            if plate in registered_plates:
                bill *= 0.5
                print("50% Discount applied!")
            print(f"Your bill is: {bill} won. Goodbye\n")
            tower.depart(floor, slot)

        case Action.QUIT:
            break