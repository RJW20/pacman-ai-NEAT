# PacMan AI: NEAT
An application of my implementation of [NEAT](https://github.com/RJW20/NEAT) to the game PacMan.

## Configuration

### What PacMan can see:
PacMan receives 8 visual inputs, 4 from the cardinal directions and another 4 from the oridinal directions. These are rotated to always be from PacMans perspective (so north is always considered to be the direction PacMan is travelling/facing).

#### Cardinal Vision
In each cardinal direction, PacMan is given a value in [-1,1] indicating how favourable or unfavourable turning in that direction would be. This value is found by looking 5 tiles in each direction and running the following checks:
- if the first tile is wall returns 1.
- if there is nothing (possibly before a wall) returns 0.
- if there is a PacDot before any walls returns -0.5.
- if there is the Fruit before any walls return -0.7 (looks like better PacDot).
- if there is an active Ghost before any walls returns 1 (looks like a wall to PacMan).
- if there is a frightened Ghost before any walls returns -1 (looks like even better PacDot).

Note that other than the first check the order does not matter here, values with higher magnitude will always be reported if their conditions are met (and also active ghosts are considered more important than frightened).

The visual below shows a representation of the result of these checks, with [-1,1] being mapped to [Green, Yellow, Red].

![cardinal_vision](https://github.com/RJW20/pacman-ai-NEAT/assets/99192767/15628aa8-1b4a-4f3b-a362-448828eb1c24)

The lines actually originate from the centre of the tile PacMan is on, hence the apparent 'snapping'.

#### Ordinal Vision
In the ordinal directions PacMan receives one-hot values. These are turned on (have value 1) if there is an active Ghost in the 3x3 square of tiles in the respective ordinal direction. This is shown below, with the square being green or red representing if the node is turned off or on.

![ordinal_vision](https://github.com/RJW20/pacman-ai-NEAT/assets/99192767/da3421b6-16f8-4bc5-8b97-1e6a5d4b57cd)

### What PacMan can do:
PacMan can choose to move in any direction forward, right, back or left i.e. relative to itself. The rules apply as they would to a normal game of PacMan so if it tries to turn right into a wall the move will be ignored and it will keep moving forwards.

### Neural Network Structure:
The algorithm starts off with networks that have 8 input nodes, 1 bias node, 4 output nodes with sigmoid activation, and one random connection. A move is chosen by mapping the output nodes to the 4 possible moves and choosing the move which corresponds to the node with highest activation.

## Training
Training is split up into 5 separate phases, to enable PacMan to learn different skills in isolation before having to deal with more complicated scenarios.

### Phase 1 - Only Dots

#### Setup
In this phase the only thing in the maze with PacMan is basic PacDots. This should allow PacMan to learn how to navigate the maze and also that eating PacDots is good. Deaths here occur from either not moving for 20 frames or going more than 2000 frames without eating another PacDot.

#### End criteria
Eating the majority of the PacDots (>220).

#### Fitness function
The fitness function is a ratio between the number of dots eaten raised to the power of 4 and the time taken to eat them (with a baseline added to prevent early deaths looking good). This encourages PacMan to not only eat lots of PacDots, but also that doing so quicker is better, thus resulting in him actually seeking them out rather than just stumbling over them given infinite time.

### Phase 2 - Dots and Blinky

#### Setup
In this phase we also add Blinky into the Maze. This should teach PacMan to avoid the Ghosts, while still retaining the ability to hunt down the PacDots.

#### End criteria
Eating all of the PacDots (240). This is actually easier to achieve now because reacting to Blinky stops PacMan from getting stuck in endless loops. 

#### Fitness function
The fitness function is now just PacMan's score, since we care less about the speed of the score and more about PacMan not dying (colliding with Blinky) no matter how long it takes.

### Phase 3 - Dots and Two Ghosts

#### Setup
In this phase we now also add Pinky into the Maze. The aim here is to further improve PacMan's ability to avoid ghosts, without making it too difficult.

#### End criteria
Eating all of the PacDots (240).

#### Fitness function
The fitness function is still just PacMan's score.

### Phase 4 - Dots and Ghosts

#### Setup
In this phase we now have all Ghosts in the maze with PacMan, but still no PowerDots. This makes it very difficult for PacMan to do well. The aim here is still to improve PacMan's ability to avoid ghosts.

#### End criteria
Eating approximately 2/3 of the PacDots (>160).

#### Fitness function
The fitness function is still just PacMan's score.

### Phase 5 - Full Game

#### Setup
In this phase we now have all the game elements present. This means adding PowerDots and the Fruit into Phase 4. The result of this is that now the Ghosts can be in frightened mode and because of the way we set up PacMan's vision they should just look like better PacDots so it shouldn't require additional training for PacMan to try and eat them.

#### End criteria
Eating all the dots.

#### Fitness function
The fitness function is essentially the same as before, but it is not PacMan's score anymore since that can be increased by eating frightened Ghosts and the Fruit which with how score is calculated can skew the score massively if PacMan gets lucky. To achieve the same as before the fitness is now just the number of PacDots and PowerDots eaten multiplied by 10.

## Results:
The network produced from the training is capable of completing the full game. However, the random motion of the Ghosts in frightened mode mean that it is unable to be consistent at doing so, resulting in a rate of about 1 in 500 games to actually eat all the dots. Below is one such game, achieved after 19 generations in phase 5 and 92 generations in total (30 + 5 + 8 + 30 + 19).

![win](https://github.com/RJW20/pacman-ai-NEAT/assets/99192767/b0686305-9a97-43c0-8882-30bd55960563)

Note that this is not actually the highest score PacMan achieved, but the goal here wasn't to maximise his score but instead the numbr of dots eaten.

Taking a look at the network itself (using [this](https://github.com/RJW20/NEAT-genome-utility)):

![winning_genome](https://github.com/RJW20/pacman-ai-NEAT/assets/99192767/9e552f9c-3f16-41b4-a4ae-a5bb560ab801)

we can see that PacMan is only actually using the front left ordinal vision, implying the algorithm has determined that in its current state the ordinal vision is not useful. Perhaps increasing the size of the 3x3 squares thus might provide better results, but equally since we are only using one-hot values for these squares it might be more that actually they are not helpful inputs (one can imagine a scenario where the node is turned on, but actually the active Ghost is on the other side of a wall with no easy route to PacMan, so not actually threatening him and so reacting to the input doesn't make any sense).
