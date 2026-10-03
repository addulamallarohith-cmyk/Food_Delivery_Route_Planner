from flask import Flask, render_template, request, jsonify
import math
import heapq

app = Flask(__name__)

DEFAULT_LOCATIONS = {
    "Restaurant": (0, 0),
    "Customer A": (2, 4),
    "Customer B": (5, 2),
    "Customer C": (7, 6),
    "Customer D": (3, 8),
    "Customer E": (9, 3),
}

def distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def build_graph(locations):
    names = list(locations)
    graph = {n: [] for n in names}
    for i, u in enumerate(names):
        for j, v in enumerate(names):
            if i != j:
                graph[u].append((distance(locations[u], locations[v]), v))
    return graph

def nearest_neighbor(locations, start):
    unvisited = set(locations)
    unvisited.remove(start)
    route = [start]
    total = 0.0
    current = start

    while unvisited:
        nxt = min(unvisited, key=lambda x: distance(locations[current], locations[x]))
        total += distance(locations[current], locations[nxt])
        route.append(nxt)
        current = nxt
        unvisited.remove(nxt)

    total += distance(locations[current], locations[start])
    route.append(start)
    return route, total

def two_opt(route, locations):
    best = route[:]
    best_cost = route_cost(best, locations)
    improved = True

    while improved:
        improved = False
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best) - 1):
                candidate = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                cost = route_cost(candidate, locations)
                if cost + 1e-9 < best_cost:
                    best, best_cost = candidate, cost
                    improved = True
    return best, best_cost

def route_cost(route, locations):
    return sum(distance(locations[route[i]], locations[route[i + 1]])
               for i in range(len(route) - 1))

def dijkstra(locations, start, end):
    graph = build_graph(locations)
    pq = [(0.0, start)]
    costs = {n: float("inf") for n in locations}
    previous = {}
    costs[start] = 0.0

    while pq:
        cost, node = heapq.heappop(pq)
        if cost > costs[node]:
            continue
        if node == end:
            break
        for edge_cost, neighbor in graph[node]:
            new_cost = cost + edge_cost
            if new_cost < costs[neighbor]:
                costs[neighbor] = new_cost
                previous[neighbor] = node
                heapq.heappush(pq, (new_cost, neighbor))

    if costs[end] == float("inf"):
        return [], None

    path = []
    cur = end
    while cur != start:
        path.append(cur)
        cur = previous[cur]
    path.append(start)
    path.reverse()
    return path, costs[end]

@app.route("/")
def index():
    return render_template("index.html", locations=DEFAULT_LOCATIONS)

@app.route("/api/plan", methods=["POST"])
def plan():
    data = request.get_json(silent=True) or {}
    locations = data.get("locations", DEFAULT_LOCATIONS)
    start = data.get("start", "Restaurant")

    # Convert JSON lists to tuples.
    locations = {k: tuple(v) for k, v in locations.items()}

    if start not in locations or len(locations) < 2:
        return jsonify({"error": "Please provide at least two valid locations."}), 400

    nn_route, nn_cost = nearest_neighbor(locations, start)
    improved_route, improved_cost = two_opt(nn_route, locations)
    d_path, d_cost = dijkstra(locations, start, improved_route[1])

    return jsonify({
        "nearest_neighbor": {"route": nn_route, "distance": round(nn_cost, 2)},
        "improved": {"route": improved_route, "distance": round(improved_cost, 2)},
        "dijkstra": {
            "route": d_path,
            "distance": round(d_cost, 2) if d_cost is not None else None
        }
    })

if __name__ == "__main__":
    app.run(debug=True)
