import math

def Distance(vec1,vec2):
    a = vec1[0] - vec2[0]
    b = vec1[1] - vec2[1]
    return math.sqrt(a*a+b*b)

def MoveTowards(current, target, delta):
    x = target[0]-current[0]
    y = target[1]-current[1]
    length = Distance(current,target)
    if(length <= delta or length == 0):
        return current
    normalizedVecAndDelta = (x/length*delta,y/length*delta)
    return [current[0]+normalizedVecAndDelta[0],current[1]+normalizedVecAndDelta[1]]

def NormalizeVec(vec):
    length = math.sqrt(vec[0]*vec[0]+vec[1]*vec[1])
    if(length == 0):
        return [0,0]
    return [vec[0]/length,vec[1]/length]
