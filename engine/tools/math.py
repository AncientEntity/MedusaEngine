import math

def Distance(vec1,vec2):
    a = vec1[0] - vec2[0]
    b = vec1[1] - vec2[1]
    return math.sqrt(a*a+b*b)