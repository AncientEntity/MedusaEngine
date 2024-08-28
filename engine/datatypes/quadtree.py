import pygame

from engine.components.physicscomponent import PhysicsComponent

# Quadrants
#    x y
# 1: + + (top right)
# 2: - + (top left)
# 3: - - (bottom left)
# 4: + - (bottom right)

class QuadNode:
    maxChildrenCount = 8
    minBoundSize = 2 # Should be power of 2.
    def __init__(self, parentNode, quadrantBounds : pygame.Rect):
        self.parent = parentNode
        self._isLeafNode = True
        self._quadrantChildren = [] #quadrant 1,2,3,4 as seen on top of file.
        self._quadrantBodies = []
        self.bounds : pygame.Rect = quadrantBounds

        self.minBound = self.bounds.w <= QuadNode.minBoundSize
    def AddBody(self, body : PhysicsComponent):
        if(not QuadNode.BodyOverlappingBounds(body,self.bounds)):
            return

        if(self._isLeafNode):
            if(body in self._quadrantBodies):
                return

            self._quadrantBodies.append(body)
            body._overlappingSpatialPartitions.append(self)

            if(not self.minBound and len(self._quadrantBodies) > QuadNode.maxChildrenCount):
                self.SubdivideNode()
        else:
            self.FindNextQuadrantForBody(body)


    def UpdateBody(self, body : PhysicsComponent):
        if(QuadNode.BodyOverlappingBounds(body,self.bounds)):
           return

        self.RemoveBody(body)

        curNode = self.parent
        while(not QuadNode.BodyOverlappingBounds(body,curNode.bounds)):
            curNode = curNode.parent

        curNode.AddBody(body)


    def RemoveBody(self, body : PhysicsComponent):
        if(self._quadrantBodies and body in self._quadrantBodies):
            self._quadrantBodies.remove(body)
            body._overlappingSpatialPartitions.remove(self)

        if(self.parent and self.parent.GetBodyCountFromNode(ignoreNoneLeaf=False,maxValue=15) <= QuadNode.maxChildrenCount):
            self.parent.UnSubdivideNode()

    def SubdivideNode(self):
        self._isLeafNode = False

        #Create new children

        #Q1 + + (top right)
        self._quadrantChildren.append(QuadNode(self,pygame.Rect(self.bounds.x+self.bounds.w / 2,self.bounds.y, self.bounds.w / 2, self.bounds.h / 2)))
        #Q2 - + (top left)
        self._quadrantChildren.append(QuadNode(self,pygame.Rect(self.bounds.x,self.bounds.y, self.bounds.w / 2, self.bounds.h / 2)))
        #Q3 - - (bottom left)
        self._quadrantChildren.append(QuadNode(self,pygame.Rect(self.bounds.x,self.bounds.y + self.bounds.h / 2, self.bounds.w / 2, self.bounds.h / 2)))
        #Q4 + - (bottom right)
        self._quadrantChildren.append(QuadNode(self,pygame.Rect(self.bounds.x+self.bounds.w / 2,self.bounds.y + self.bounds.h / 2, self.bounds.w / 2, self.bounds.h / 2)))

        for body in self._quadrantBodies:
            body._overlappingSpatialPartitions.remove(self)
            self.FindNextQuadrantForBody(body)
        self._quadrantBodies = None

    def UnSubdivideNode(self):
        self._quadrantBodies = []
        for child in self._quadrantChildren:
            if(not child._isLeafNode):
                child.UnSubdivideNode()
            for body in child._quadrantBodies:
                self._quadrantBodies.append(body)
                body._overlappingSpatialPartitions.append(self)
                body._overlappingSpatialPartitions.remove(child)
            child._quadrantBodies = []
        self._quadrantChildren = []
        self._isLeafNode = True

        # Parent may need to unsubdivide as well now.
        if (self.parent and self.parent.GetBodyCountFromNode(ignoreNoneLeaf=False,
                                                                                  maxValue=15) <= QuadNode.maxChildrenCount):
            self.parent.UnSubdivideNode()

    def GetBodyCountFromNode(self, ignoreNoneLeaf=True, includeSelf=False,maxValue=-1):
        count = 0 if not includeSelf else len(self._quadrantBodies)
        for child in self._quadrantChildren:
            if(maxValue > 0 and count >= maxValue):
                return count

            if(not child._isLeafNode and ignoreNoneLeaf):
                continue
            elif(child._isLeafNode):
                count += len(child._quadrantBodies)
            else:
                count += child.GetBodyCountFromNode(ignoreNoneLeaf)
        return count



    def FindNextQuadrantForBody(self, body : PhysicsComponent):
        found = False
        for child in self._quadrantChildren:
            if(QuadNode.BodyOverlappingBounds(body, child.bounds)):
                child.AddBody(body)
                found = True
        if not found: #todo remove this exception when certain it works as it should.
            raise Exception("Quadrant couldn't be found for body. Outside world bounds?" +
                            "Make sure your min quad node size is a power of 2, and you're" +
                            " root node bounds are a power of 2. BodyBounds: "+str(body.bounds)+", Last Child Bounds: "+str(child.bounds))

    def GetBodiesRecursive(self):
        if self._isLeafNode:
            return self._quadrantBodies

        bodies = []
        for child in self._quadrantChildren:
            if(not child._isLeafNode):
                bodies.extend(child.GetBodiesRecursive())
            else:
                bodies.extend(child._quadrantBodies)
        return bodies

    @staticmethod
    def RemoveFromTree(body : PhysicsComponent):
        for quad in body._overlappingSpatialPartitions:
            quad.RemoveBody(body)

    @staticmethod
    def BodyOverlappingBounds(body : PhysicsComponent, bounds : pygame.Rect):
        bodyBounds = pygame.FRect(body.parentEntity.position[0]-body.bounds[0] / 2 + body.offset[0],
                                 body.parentEntity.position[1]-body.bounds[1] / 2 + body.offset[1],
                                 body.bounds[0],
                                 body.bounds[1])
        return bounds.colliderect(bodyBounds)

    @staticmethod
    def GetBodiesInSharedSpace(body : PhysicsComponent):
        others = []
        for quad in body._overlappingSpatialPartitions:
            others.extend(quad.GetBodiesRecursive())
        return others