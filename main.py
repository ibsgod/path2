import sys
import random
import pygame
import os
from queue import PriorityQueue
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
bsize = 100
width = int(1300/bsize)*bsize
height = int(650/bsize)*bsize
screen = pygame.display.set_mode((width, height))
click = 0
clock = pygame.time.Clock()
player = None
path = []
food = None
visited = []
rects = []
clicked = []
corners = {}
adj = {}
cornerRect = {}
p = None

def checkPoint(rect, point):
    if point[0] > rect.x and point[0] < rect.x + rect.width and point[1] > rect.y and point[1] < rect.y + rect.height:
        return True
    return False

def checkLine(rect, start, end):
    lines = [(rect.topleft, rect.topright), (rect.topright, rect.bottomright), (rect.bottomright, rect.bottomleft),
             (rect.bottomleft, rect.topleft), (rect.midleft, rect.midright)]
    for line in range(5):
        if line % 2 == 0 or line == 4:
            if start[0] == end[0]:
                if max(lines[line][0][0], lines[line][1][0]) > start[0] > min(lines[line][0][0], lines[line][1][0])\
                    and max(start[1], end[1]) > lines[line][0][1] > min(start[1], end[1]):
                    return True
                continue

            m1 = 0
            b1 = lines[line][0][1]
            m2 = (start[1] - end[1]) / (start[0] - end[0])
            b2 = start[1] - start[0] * m2
            if m1 == m2:
                continue
            x = round(-(b1 - b2) / (m1 - m2), 3)
            if max(min(lines[line][0][0], lines[line][1][0]), min(start[0], end[0])) < x < min(max(lines[line][0][0], lines[line][1][0]), max(start[0], end[0])):
                return True
        else:
            if start[1] == end[1]:
                if max(lines[line][0][1], lines[line][1][1]) > start[1] > min(lines[line][0][1], lines[line][1][1])\
                    and max(start[0], end[0]) > lines[line][0][0] > min(start[1], end[0]):
                    return True
                continue
            m1 = 0
            b1 = lines[line][0][0]
            m2 = (start[0] - end[0]) / (start[1] - end[1])
            b2 = start[0] - start[1] * m2
            if m1 == m2:
                continue
            y = round(-(b1 - b2) / (m1 - m2), 3)
            if max(min(lines[line][0][1], lines[line][1][1]), min(start[1], end[1])) < y < min(
                    max(lines[line][0][1], lines[line][1][1]), max(start[1], end[1])):

                return True
    return False

def Djikstra():
    q = PriorityQueue()
    dist = {player: (0, player)}
    q.put((0, player))
    while not q.empty():
        curr = q.get()[1]
        for corn in adj[curr]:
            if corn[0] is not player and corn[0] not in dist or dist[corn[0]][0] > dist[curr][0] + corn[1]:
                dist[corn[0]] = (dist[curr][0] + corn[1], curr)
                q.put((corn[1], corn[0]))
            if corn[0] == food:
                q = PriorityQueue()
    if food in dist:
        path = []
        curr = food
        while curr is not player:
            path.append(curr)
            curr = dist[curr][1]
        path.append(curr)
        return path
    return None




def updateMatrix():
    global adj
    adj = {}
    for corn in corners:
        if not corners[corn]:
            continue
        adj[corn] = []
        for corny in corners:
            if corn == corny:
                continue
            if not corners[corny]:
                continue
            yes = True
            for rect in rects:
                if checkLine(rect, corn, corny):
                    yes = False
                    break
            if yes:
                dist = int(((corn[0] - corny[0])**2 + (corn[1] - corny[1])**2)**0.5)
                adj[corn].append((corny, dist))
    return Djikstra()

def changeObs(x, y, mode):
    global p
    if mode and (x-bsize/2, y-bsize/2) not in corners:
        rect = (pygame.Rect(x-bsize/2, y-bsize/2, bsize, bsize))
        if rect.collidepoint(player) or rect.collidepoint(food):
            return
        rects.append(rect)
        corners[rect.topleft] = True
        corners[rect.topright] = True
        corners[rect.bottomleft] = True
        corners[rect.bottomright] = True

        for recty in rects:
            if recty.colliderect(rect) and rect is not recty:
                if rect.x <= recty.x:
                    if rect.y <= recty.y:
                        corners[rect.bottomright] = False
                        corners[recty.topleft] = False
                    if rect.y >= recty.y:
                        corners[rect.topright] = False
                        corners[recty.bottomleft] = False
                if rect.x >= recty.x:
                    if rect.y <= recty.y:
                        corners[rect.bottomleft] = False
                        corners[recty.topright] = False
                    if rect.y >= recty.y:
                        corners[rect.topleft] = False
                        corners[recty.bottomright] = False

    else:
        for j in clicked[:]:
            for rect in rects:
                if j.colliderect(rect) and rect is not j:
                    corners[rect.topleft] = True
                    corners[rect.topright] = True
                    corners[rect.bottomleft] = True
                    corners[rect.bottomright] = True
                    for recty in rects:
                        if recty.colliderect(rect) and rect is not recty and recty is not j:
                            if rect.x <= recty.x:
                                if rect.y <= recty.y:
                                    corners[rect.bottomright] = False
                                    corners[recty.topleft] = False
                                if rect.y >= recty.y:
                                    corners[rect.topright] = False
                                    corners[recty.bottomleft] = False
                            if rect.x >= recty.x:
                                if rect.y <= recty.y:
                                    corners[rect.bottomleft] = False
                                    corners[recty.topright] = False
                                if rect.y >= recty.y:
                                    corners[rect.topleft] = False
                                    corners[recty.bottomright] = False
            rects.remove(j)
            corners.pop((j.topleft))
            corners.pop((j.topright))
            corners.pop((j.bottomleft))
            corners.pop((j.bottomright))
            clicked.remove(j)
    p = updateMatrix()
    # for i in corners:
    #     print(i, corners[i])
    # print("-----------------")

while True:
    mousePos = pygame.mouse.get_pos()
    screen.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = []
            click = 0
            for i in rects:
                if i.collidepoint(mousePos):
                    clicked.append(i)
            if len(clicked) == 0:
                click = 2
            else:
                click = 1
            changeObs(mousePos[0], mousePos[1], True if click == 2 else False)
    while food is None or player is None or food[0] == player[0] and food[1] == player[1] and p is None:
        if player in corners:
            corners.pop(player)
            corners.pop(food)
        player = (random.randint(0, width), random.randint(0, height))
        food = (random.randint(0, width), random.randint(0, height))
        corners[player] = True
        corners[food] = True
        p = updateMatrix()
    for i in range(len(rects)):
        pygame.draw.rect(screen, (100, 100, 100), rects[i])
    # for i in range(len(visited)):
    #     for j in range(len(visited[i])):
    #         if visited[i][j] is not None:
    #             pygame.draw.rect(screen, (0, 100, 0), (j * bsize, i * bsize, bsize, bsize))
    # for curr in path:
    #     pygame.draw.rect(screen, (0, 0, 255), (curr[1] * bsize, curr[0] * bsize, bsize, bsize))
    # if not click:
    #     player = (path[len(path)-1][1], path[len(path)-1][0])
    #     path.remove(path[len(path)-1])
    for i in corners:
        if corners[i]:
            pygame.draw.circle(screen, (255, 0, 0), (i), 5)
    # pygame.draw.circle(screen, (255, 0, 0), (player[0], player[1]), 10)
    # pygame.draw.circle(screen, (0, 255, 0), (food[0], food[1]), 10)
    for i in adj:
        for j in adj[i]:
            pygame.draw.line(screen, (255, 255, 0), i, j[0], 5)
    if p is not None:
        for i in range(len(p) - 1):
            pygame.draw.line(screen, (0, 0, 255), p[i], p[i + 1], 5)
    pygame.display.update()
    clock.tick(30)






