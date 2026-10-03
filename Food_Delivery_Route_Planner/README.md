# Food Delivery Route Planner

A college-project website based on Problem 30. It uses Python + Flask and implements:
- Nearest Neighbor (Greedy) route planning
- 2-Opt route improvement
- Dijkstra shortest path
- TSP-style return to the starting restaurant
- Interactive location/coordinate editing

## Run on Windows

1. Install Python 3.10+.
2. Open Command Prompt in this folder.
3. Run:
   `pip install -r requirements.txt`
4. Start:
   `python app.py`
5. Open the address shown in the terminal, usually:
   `http://127.0.0.1:5000`

No MongoDB is required for this demo version. MongoDB can be added later to store riders, orders and saved routes.
