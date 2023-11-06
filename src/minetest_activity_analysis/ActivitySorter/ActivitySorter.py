import numpy as np
import math
import time


def getDistance(coord1, coord2):
    distance = math.sqrt((coord2[0] - coord1[0]) ** 2 + (coord2[1] - coord1[1]) ** 2 + (coord2[2] - coord1[2]) ** 2)
    return distance


def getDistance2d(coord1, coord2):
    distance = math.sqrt((coord2[0] - coord1[0]) ** 2 + (coord2[1] - coord1[1]) ** 2)
    return distance


# Sorry, interfaces and type definitions will be here latter

class ActivitySorter:
    logParser = None

    def __init__(self, logParser):
        if logParser is None:
            raise Exception('Log parser is None!')
        self.logParser = logParser

    def getActions(self, players=[], actionTypes=[], dateFrom=None, dateTo=None):
        logs = []
        for item in self.readActions(players, actionTypes, dateFrom, dateTo):
            if item is None:
                continue
            logs.append(item)
        return logs

    def readActions(self, players=[], actionTypes=[], dateFrom=None, dateTo=None):
        '''Returns generator of actions by player and actions types'''
        for item in self.logParser.read():
            if item['logType'] != 'action':
                continue
            if item['name'] == None:
                continue

            if dateFrom is not None and item['timestamp'] < dateFrom:
                continue
            if dateTo is not None and item['timestamp'] > dateTo:
                continue

            if (item['name'] in players or len(players) == 0) and (
                    item['action'] in actionTypes or len(actionTypes) == 0):
                yield item
        return None

    def getActionsByPos(self, players=[], actionTypes=[], pos=[0, 0, 0], radius=100, dateFrom=None, dateTo=None):

        actions_arr = []
        for item in self.logParser.read():
            if item is None:
                continue
            if item['logType'] != 'action':
                continue

            if dateFrom is not None and item['timestamp'] < dateFrom:
                continue
            if dateTo is not None and item['timestamp'] > dateTo:
                continue

            print(item)
            if (item['name'] in players or len(players) == 0) and (
                    len(actionTypes) == 0 or item['action'] in actionTypes):
                float_coord = [
                    float(item['coords'][0]),
                    float(item['coords'][1]),
                    float(item['coords'][2]),
                ]
                item['coords'] = float_coord
                actions_arr.append(item)

        start_time = time.time()

        players_dict = {}
        for action in actions_arr:
            if getDistance(action['coords'], pos) < radius:
                if action['name'] not in players_dict:
                    players_dict[action['name']] = []
                players_dict[action['name']].append(action)

        print(f"Обработка закончена:{time.time() - start_time}")

        return players_dict

    def getClusters(self, players=[], actionTypes=[], clusterType='2d', dateFrom=None, dateTo=None):

        start_time = time.time()
        coords_arr = []
        for item in self.logParser.read():
            if item is None:
                continue

            if item['logType'] != 'action':
                continue

            if dateFrom is not None and item['timestamp'] < dateFrom:
                continue
            if dateTo is not None and item['timestamp'] > dateTo:
                continue

            if (item['name'] in players or len(players) == 0) and (
                    item['action'] in actionTypes or len(actionTypes) == 0):

                if item['coords'] is None:
                    print(item)
                    continue

                if clusterType == '2d':
                    coords_arr.append([item['coords'][0], item['coords'][2]])
                else:
                    coords_arr.append(item['coords'])

        print("Данные получены!")
        print(time.time() - start_time)
        start_time = time.time()

        tuple_list = [tuple(sublist) for sublist in coords_arr]
        unique_set = set(tuple_list)
        unique_list = [list(subtuple) for subtuple in unique_set]

        print("Уникальные извлечены")
        print(time.time() - start_time)
        start_time = time.time()

        for idx, item in enumerate(unique_list):
            unique_list[idx][0] = float(item[0])
            unique_list[idx][1] = float(item[1])
            if clusterType == '3d':
                unique_list[idx][2] = float(item[2])

        print("Типы преобразованы")
        print(time.time() - start_time)
        start_time = time.time()

        clusters = {}
        itemsCount = len(unique_list)
        print("Количество элементов для кластеризации")
        print(itemsCount)
        unique_list = np.array(unique_list)  # Преобразуем список в массив NumPy

        while itemsCount > 0:
            if len(unique_list) == 0:
                break  # Если не осталось элементов, выходим из цикла

            item = unique_list[0]
            distances = np.linalg.norm(unique_list - item, axis=1)
            close_indices = np.where(distances < 60)[0]

            for idx in close_indices:
                item2 = unique_list[idx]
                if clusterType == '2d':
                    cluster_name = f'{int(item[0])} {int(item[1])}'
                elif clusterType == '3d':
                    cluster_name = f'{int(item[0])} {int(item[1])} {int(item[2])}'

                if cluster_name not in clusters:
                    clusters[cluster_name] = []

                clusters[cluster_name].append(item2)

            unique_list = np.delete(unique_list, close_indices, axis=0)
            itemsCount -= len(close_indices)
        print("Кластеры разбиты:")
        print(time.time() - start_time)

        for clusterKey in clusters:
            for clusterIdx, clusterCoords in enumerate(clusters[clusterKey]):
                clusters[clusterKey][clusterIdx] = clusterCoords.tolist()

        return clusters

    def getAuths(self, players=[], dateFrom=None, dateTo=None):
        auths = []
        for record in self.logParser.read():
            if record is None:
                continue

            if record['logType'] != 'beowulfAuth':
                continue
            if dateFrom is not None and record['timestamp'] < dateFrom:
                continue
            if dateTo is not None and record['timestamp'] > dateTo:
                continue
            if record['name'] not in players and len(players) != 0:
                continue

            auths.append(record)
        return auths

    @classmethod
    def filterByNames(cls, log_events=[], names=[]):
        new_log = []
        players_len = len(names)
        for item in log_events:
            if players_len == 0 or item['name'] in names:
                new_log.append(item)
        return new_log

    @classmethod
    def filterByActions(cls, log_events=[], actions=[]):
        new_log = []
        for item in log_events:
            if item['action'] in actions:
                new_log.append(item)
        return new_log

    # @classmethod
    # def checkSingleByActions(cls, item, actions=[]):
    #     if item['action'] in actions:
    #         return True
    #     else:
    #         return False
    #
    # @classmethod
    # def checkSingleByPlayers(cls, item, players=[]):
    #     if item['name'] in players:
    #         return True
    #     else:
    #         return False
