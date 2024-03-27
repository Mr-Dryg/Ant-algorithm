import asyncio, random

feromon_start = 0.5
a = 8
b = 2
START = int(input('Начало маршрута (1-50): ')) - 1
FINISH = int(input('Конец маршрута (1-50): ')) - 1
c_prox = 10
kol_ant = 75

with open('graph.txt', 'r') as file:
    data = [list(map(int, line.split())) for line in file.readlines()]

for i in range(len(data)):
    for j in range(len(data[i])):
        data[i][j] = [data[i][j], feromon_start if data[i][j] else 0]

distance = lambda i, j: data[i][j][0]
feromons = lambda i, j: data[i][j][1]
wish = lambda i, j: (feromons(i, j) ** a) * ((c_prox / distance(i, j)) ** b)


class Ant:
    def __init__(self, n, start=None) -> None:
        self.n = n
        self.i = random.choice((START, FINISH)) if start is None else start
        self.f1, self.f2 = START, FINISH
        self.route = [self.i]
    
    def dist(self) -> int:
        res = 0
        for id, i in enumerate(self.route[:-1]):
            j = self.route[id+1]
            res += distance(i, j)
        return res

    def next_node(self) -> int:
        i = self.i
        s = sum([wish(i, j) for j in range(len(data[i])) if distance(i, j) and j not in self.route])
        if s == 0:
            s = sum([wish(i, j) for j in range(len(data[i])) if distance(i, j)])
        edges = [round(wish(i, j) / s, 2) if distance(i, j) and j not in self.route else 0 for j in range(len(data[i]))]
        if not any(edges):
            edges = [round(wish(i, j) / s, 2) if distance(i, j) else 0 for j in range(len(data[i]))]
        rand = round(random.random(), 2)
        while rand == 0:
            rand = round(random.random(), 2)
        if rand > 0.95:
            rand -= 0.06
        j = 0
        while not (sum(edges[:j]) <= rand and rand <= sum(edges[:j+1])):
                if j > 50:
                    print('ERROR')
                    exit(f'{edges}\n{rand}')
                j += 1
        return j

    async def move(self):
        while not (self.f1 in self.route and self.f2 in self.route) and len(self.route) < 25:
            self.i = self.next_node()
            self.route.append(self.i)
            await asyncio.sleep(0.0000000001)


def ferom():
    Q = 4
    p = 0.64
    for ant in ants:
        try:
            df = Q / ant.dist()
        except ZeroDivisionError:
            df = 0
        for id, i in enumerate(ant.route[:-1]):
            j = ant.route[id+1]
            data[i][j][1] = data[j][i][1] = round(p * feromons(i, j) + df, 2)


k = 0
while k < 100:
    try:
        tasks = []
        loop = asyncio.get_event_loop()
        ants = [Ant(_) for _ in range(kol_ant)]
        for ant in ants:
            tasks.append(loop.create_task(ant.move()))
        loop.run_until_complete(asyncio.gather(*tasks))
    finally:
        ferom()
    k += 1

loop = asyncio.get_event_loop()
ant = Ant(0, START)
loop.run_until_complete(ant.move())
min_dist, best_route = min([(_.dist(), _.route) for _ in [ant] + ants], key=lambda x: (x[0], len(x[1])))
print(f'Самый короткий маршрут ({min_dist} км):')
print(*[_ + 1 for _ in best_route])