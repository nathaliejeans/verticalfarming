# VERTICAL AEROPONIC FARMING SIMULATION

Vertical Farming Simulation
How-To

My ultimate goal with this project is to provide an interactive way of educating people about vertical farming and its possibilities. Vertical farming is when plants are grown in layers, which enables farming to occur in smaller spaces rather than larger stretches of land. The particular system I’m focusing on is an aquaponic system, where the nutrients of aquatic animals like fish nourish the plants above it. I’m going to create multiple parts of the game that interact with one another as follows:

A. The ability to grow plants and cabbages from the inventory. Can also add fish into fish tanks.

B. A marketplace where users can sell their plants and buy more expensive ones that would generate more profit. Users can also purchase equipment like fish tanks (aka planters).

C. Graphs that include analysis on the current state of your farm and steps you should take to improve your revenue growth & economics.

________________________________________________________________________________________________________________________________________________________

THE FILE TO RUN : verticalfarming-2.py
Used PIL/pillow module from notes so that should be installed for this to run.

(1) Homepage: Navigate to your garden by clicking "BEGIN"

(2) Your garden: 
Everything on the menu on the right is a button, except for the 'Menu' rectangle and the balance.

____________________________________________________________________________

TABLE FOR ACTIONS (press key to do the following) -->

plant type (add key, remove key)

planter (p, x)

plant   (a, r)

cabbage (c, t)

flower  (f, w)

rose    (o, s)

tropic  (i, k)

Note that this will only work if you have the capacity to sell/buy/plant based on your garden, so be sure to check your inventory.

To zoom up on a fish tank, press the number of the fish tank. It should go from 0 to however many tanks you have.
The order goes in columns, so the first column down is 0, 1, 2 then the next column is 3, 4, 5, etc. They are labelled.

Like so:

[0 3 6

 1 4 7
 
 2 5 8]

(3) Your fish tank:
Add fish by pressing 'a'
Press 2 to return to garden menu.

(4) Marketplace:
Press on 'buy' or 'sell' for any of the buttons on the screen
Also you can navigate the menu.

(5) Graph Analysis:
Click on the 'prediction' button to get your prediction. You can click it again to remove the prediction, and click it a third time to get a new prediction.

____________________________________________________________________________

Your graph will automatically update every time your money value changes.

You can click each pink point to get more precise values on your axis.

Press 'a' to scale up axis

Press 's' to scale down axis

Note that using a prediction is worth $30.

Navigate the menu at the top of the screen.
