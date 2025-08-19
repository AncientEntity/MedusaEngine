import math

def Magnitude(vec):
    sum = 0
    for scalar in vec:
        sum += scalar*scalar
    return math.sqrt(sum)

def Distance(vec1,vec2):
    a = vec1[0] - vec2[0]
    b = vec1[1] - vec2[1]
    return math.sqrt(a*a+b*b)

# The given delta MoveTowards applies.
def MoveTowardsDelta(current, target, delta):
    x = target[0]-current[0]
    y = target[1]-current[1]
    length = Distance(current,target)
    if(length == 0):
        return (0,0)
    elif(length <= delta):
        return (x,y)

    normalizedVecAndDelta = (x/length*delta,y/length*delta)
    return normalizedVecAndDelta

# Gives the final position after moving towards
def MoveTowards(current, target, delta):
    normalizedVecAndDelta = MoveTowardsDelta(current,target,delta)
    return [current[0]+normalizedVecAndDelta[0],current[1]+normalizedVecAndDelta[1]]

def LerpRotation(currentRotation, targetRotation, delta):
    maxDistance = (currentRotation % 360)-(targetRotation % 360)
    delta = Clamp(delta,-abs(maxDistance),abs(maxDistance))
    return (currentRotation + delta) % 360


def NormalizeVec(vec):
    length = math.sqrt(vec[0]*vec[0]+vec[1]*vec[1])
    if(length == 0):
        return [0,0]
    return [vec[0]/length,vec[1]/length]

def LookAt(position, target):
    normalized = [target[0]-position[0],target[1]-position[1]]
    return math.degrees(math.atan2(-normalized[1],normalized[0])) # we apply -y as pygame displays negative as going up.

def Clamp(value, min, max):
    if(value < min):
        return min
    elif(value > max):
        return max
    return value