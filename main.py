import math
import sys
import random
import pygame
import os
import time
from queue import PriorityQueue
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
bsize = 100
width = int(1300/bsize)*bsize
height = int(650/bsize)*bsize
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
player = None
path = []
food = None
rects = []
clicked = []
corners = {}
adj = {}
cornerRect = {}
p = None
angle = 0
speed = 10
playerpos = None
pathPos = 1

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

def astar():
    s = time.time()
    q = PriorityQueue()
    dist = {player: (0, player)}
    q.put((0, player))
    while not q.empty():
        curr = q.get()[1]
        if curr is food:
            q = PriorityQueue()
            break
        for corn in adj[curr]:
            if corn[0] is not player and (corn[0] not in dist or dist[corn[0]][0] > dist[curr][0] + corn[1]):
                dist[corn[0]] = (dist[curr][0] + corn[1], curr)
                q.put((dist[corn[0]][0] + int(((corn[0][0] - food[0])**2 + (corn[0][1] - food[1])**2)**0.5), corn[0]))
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
    d = astar()
    if d is not None:
        d = d[::-1]
    return d

def changeObs(x, y, mode):
    global p
    global player
    global playerpos
    global pathPos
    if mode and (x-bsize/2, y-bsize/2) not in corners:
        rect = (pygame.Rect(x-bsize/2, y-bsize/2, bsize, bsize))
        if rect.collidepoint(player) or rect.collidepoint(food) or rect.collidepoint(playerpos):
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
            try:
                rects.remove(j)
                corners.pop(j.topleft)
                corners.pop(j.topright)
                corners.pop(j.bottomleft)
                corners.pop(j.bottomright)
                clicked.remove(j)
            except:
                pass
    corners.pop(player)
    corners.pop(food)
    player = playerpos
    corners[player] = True
    corners[food] = True
    pathPos = 1
    for corn in list(corners):
        yess = False
        for rect in rects:
            if corn == rect.bottomright or corn == rect.bottomleft or corn == rect.topleft or corn == rect.topright:
                yess = True
                break
        if not yess and not (corn is player or corn is food):
            corners.pop(corn)
    p = updateMatrix()


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
    while food is None or player is None or food == player or p is None or pathPos == len(p):
        if player in corners and food in corners:
            try:
                corners.pop(player)
                corners.pop(food)
            except:
                pass
        player = (random.randint(0, width), random.randint(0, height))
        food = (random.randint(0, width), random.randint(0, height))
        yes = False
        for i in rects:
            if i.collidepoint(player) or i.collidepoint(food):
                food = None
                yes = True
                break
        if yes:
            continue
        playerpos = player
        pathPos = 1
        corners[player] = True
        corners[food] = True
        p = updateMatrix()
    for i in range(len(rects)):
        pygame.draw.rect(screen, (100, 100, 100), rects[i])
    for i in corners:
        if corners[i]:
            pygame.draw.circle(screen, (255, 0, 0), (i), 5)
    for i in adj:
        for j in adj[i]:
            pygame.draw.line(screen, (255, 255, 0), i, j[0], 5)
    if p is not None:
        for i in range(len(p) - 1):
            pygame.draw.line(screen, (0, 0, 255), p[i], p[i + 1], 5)
    if playerpos[0] != p[pathPos][0]:
        angle = math.degrees(math.atan(-(playerpos[1] - p[pathPos][1]) / (p[pathPos][0] - playerpos[0])))
    elif playerpos[1] < p[pathPos][1]:
        angle = 90
    else:
        angle = -90
    if p[pathPos][0] < playerpos[0]:
        angle -= 180

    playerpos = (playerpos[0] + math.cos(math.radians(angle)) * speed, playerpos[1] + math.sin(math.radians(angle)) * speed)
    if (playerpos[0] - p[pathPos][0])**2 + (playerpos[1] - p[pathPos][1])**2 <= speed ** 2:
        playerpos = p[pathPos]
    if (int(playerpos[0]), int(playerpos[1])) == p[pathPos]:
        pathPos += 1
    pygame.draw.circle(screen, (255, 0, 0), (playerpos[0], playerpos[1]), 10)
    pygame.draw.circle(screen, (0, 255, 0), (food[0], food[1]), 10)
    pygame.display.update()
    clock.tick(30)






