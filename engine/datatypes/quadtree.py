import pygame

from engine.ecs import Entity


# Quadrants
#    x y
# 1: + + (top right)
# 2: - + (top left)
# 3: - - (bottom left)
# 4: + - (bottom right)

class QuadNode:
    maxChildrenCount = 10
    minBoundSize = 40
    def __init__(self, parentNode, quadrantBounds : pygame.Rect):
        self.parent = parentNode
        self._isLeafNode = True
        self._quadrantChildren = [None,None,None,None] #quadrant 1,2,3,4 as seen on top of file.
        self._quadrantEntities = []
        self.bounds : pygame.Rect = quadrantBounds

        self.minBound = (self.bounds.w // 2) <= QuadNode.minBoundSize
    def AddEntity(self, entity : Entity):
        if(self._isLeafNode):
            if(entity in self._quadrantEntities):
                return

            if(len(self._quadrantEntities)+1 >= QuadNode.maxChildrenCount and not self.minBound):
                self.SubdivideNode()
                self.FindNextQuadrantForEntity(entity)
            else:
                entity.boundingSpatialNodes.append(self)
                self._quadrantEntities.append(entity)
        else:
            self.FindNextQuadrantForEntity(entity)
    def UpdateEntity(self, entity):
        if(not self._isLeafNode):
            return

        if (QuadNode.EntityOverlappingBounds(entity, self.bounds)):
            return

        self.RemoveEntity(entity)

        curQuadNode : QuadNode = self.parent
        while(not QuadNode.EntityOverlappingBounds(entity,curQuadNode.bounds)):
            curQuadNode = curQuadNode.parent
        curQuadNode.AddEntity(entity)

        if(self.parent == None or self.parent._isLeafNode):
            return

        if(self.GetEntityParentCount() < self.maxChildrenCount):
            print("Shrinking")
            self.parent.UnSubdivideNode()

    def RemoveEntity(self,entity):
        if(entity in self._quadrantEntities):
            self._quadrantEntities.remove(entity)
            entity.boundingSpatialNodes.remove(self)

    def SubdivideNode(self):
        self._isLeafNode = False

        #Create new children

        #Q1 + + (top right)
        self._quadrantChildren[0] = QuadNode(self,pygame.Rect(self.bounds.x+self.bounds.w / 2,self.bounds.y, self.bounds.w / 2, self.bounds.h / 2))
        #Q2 - + (top left)
        self._quadrantChildren[1] = QuadNode(self,pygame.Rect(self.bounds.x,self.bounds.y, self.bounds.w / 2, self.bounds.h / 2))
        #Q3 - - (bottom left)
        self._quadrantChildren[2] = QuadNode(self,pygame.Rect(self.bounds.x,self.bounds.y + self.bounds.h / 2, self.bounds.w / 2, self.bounds.h / 2))
        #Q4 + - (bottom right)
        self._quadrantChildren[3] = QuadNode(self,pygame.Rect(self.bounds.x+self.bounds.w / 2,self.bounds.y + self.bounds.h / 2, self.bounds.w / 2, self.bounds.h / 2))

        for entity in self._quadrantEntities:
            entity.boundingSpatialNodes.remove(self)
            self.FindNextQuadrantForEntity(entity)
        self._quadrantEntities = []

    def UnSubdivideNode(self):
        for child in self._quadrantChildren:
            #child.parent = None
            for entity in child._quadrantEntities:
                self._quadrantEntities.append(entity)
                entity.boundingSpatialNodes.append(self)
                entity.boundingSpatialNodes.remove(child)
            child._quadrantEntities = []
        self._quadrantChildren = [None,None,None,None]
        self._isLeafNode = True

    def GetEntityParentCount(self):
        count = 0
        for child in self.parent._quadrantChildren:
            count += len(child._quadrantEntities)
        return count


    def FindNextQuadrantForEntity(self, entity : Entity):
        for child in self._quadrantChildren:
            if(QuadNode.EntityOverlappingBounds(entity,child.bounds)):
                child.AddEntity(entity)
    @staticmethod
    def EntityOverlappingBounds(entity : Entity, bounds : pygame.Rect):
        if(entity.spatialBounds == None):
            return bounds.collidepoint(entity.position)
        #if((entity.spatialBounds.x >= bounds.x and entity.spatialBounds.x <= bounds.x+bounds.w) or
        #   (entity.spatialBounds.x+entity.spatialBounds.w >= bounds.x and entity.spatialBounds.x+entity.spatialBounds.w <= bounds.x+bounds.w)):
        #    if ((entity.spatialBounds.y >= bounds.y and entity.spatialBounds.y <= bounds.y + bounds.h) or
        #            (entity.spatialBounds.y + entity.spatialBounds.h >= bounds.y and entity.spatialBounds.y + entity.spatialBounds.h <= bounds.y + bounds.h)):
        #        return True
        #return False

        return bounds.colliderect(entity.spatialBounds)