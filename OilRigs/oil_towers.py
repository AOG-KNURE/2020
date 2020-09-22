from functools import cmp_to_key
import numpy as np

class Point:
    def __init__(self, x, y):
        self.np_arr = np.array((x, y))

    def __eq__(self, other):
        return all(self.np_arr == other.np_arr)

    def __sub__(self, other):
        new_x, new_y = self.np_arr - other.np_arr
        return Point(new_x, new_y)

    def __add__(self, other):
        new_x, new_y = self.np_arr + other.np_arr
        return Point(new_x, new_y)

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    @property
    def x(self):
        return self.np_arr[0]

    @property
    def y(self):
        return self.np_arr[1]

def compare_counterclockwise(point1, point2):
    det = np.linalg.det(np.vstack([point2.np_arr, point1.np_arr]))

    if det == 0:
        return (point1.x + point1.y) - (point2.x + point2.y)
    else:
        return det

def pop_pivot(seq):
    min_x = min([point.x for point in seq])
    min_y = min([point.y for point in seq if point.x == min_x])
    res = Point(min_x, min_y)

    seq.remove(res)
    for i in range(len(seq)):
        seq[i] -= res
    
    return res

def is_right_turn(point1, point2, point3):
    v1 = (point2 - point1).np_arr
    v2 = (point3 - point1).np_arr

    return np.linalg.det(np.vstack([v1, v2])) < 0

def get_barycentric(point1, point2, target):
    matrix = np.vstack([point1.np_arr, point2.np_arr]).T
    det = np.linalg.det(matrix)

    if det == 0:
        length1 = np.linalg.norm(point1.np_arr)
        length2 = np.linalg.norm(point2.np_arr)

        length, point = max([(length, point1),
                             (length2, point2)],
                            lambda x: x[0])

        if np.linalg.det(np.vstack(point1.np_arr, target.np_arr)) != 0:
            return None
        
        coord = np.linalg.norm(target.np_arr) / length
        return [(coord, point), (1 - coord, Point(0, 0))]
    else:
        vec = np.linalg.inv(matrix) @ target.np_arr
        last_coord = 1 - vec[0] - vec[1]
        return [(last_coord, Point(0, 0)), (vec[0], point1), (vec[1], point2)]

def mix_oils(oils, target):
    oils = oils.copy()
    pivot = pop_pivot(oils)
    target -= pivot
    oils.sort(key = cmp_to_key(compare_counterclockwise))

    stack = [oils[0], oils[1]]
    
    for i in range(2, len(oils)):
        coords = get_barycentric(stack[-2], stack[-1], target)
        if coords is not None and all(0 <= coord[0] <= 1 for coord in coords):
            break
        
        stack.append(oils[i])
        while is_right_turn(stack[-3], stack[-2], stack[-1]):
            del stack[-2]
    else:
        coords = get_barycentric(stack[-2], stack[-1], target)
        if coords is None or not all(0 <= coord[0] <= 1 for coord in coords):
            return None

    return [(coord, point + pivot) for coord, point in coords if coord != 0]
