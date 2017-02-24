# Simulation of lifting operation and passengers in a building
using Python and SimPy framework


Objectives: 
1. Create a model, which reflects:
-	moving lifts between levels
-	passenger`s  behavior (appearance, queueing, a way out of a lift)
-	procedure of making a choice between lifts to use
-	lift`s reaction on pushing a button
-	lift`s action when not in use
2. Get information about lifting operation
	-  Average waiting time for a lift
- Average transporting time
3. Compare two algorithms of lifting operation (with/ without “basic level”) 


Lift`s model:
---------------------------
Modeling system - SimPy

Amount of lifts – 6

Amount of levels - {0, 1, 2, 3, 4, 5, 6, 7}

Capacity – 11 people

Time to get to next level– 3 sec

Time to open/close lifts doors and to stop at a level – 2 sec

Programm works – 3600 s


