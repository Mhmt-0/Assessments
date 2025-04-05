# Flappy Bird Game Documentation

Flappy Bird Game

GitHub Repository
The source code for this project is available on GitHub: “https://github.com/Mhmt-0/Assessments.git”

Identification
Name: MEHMET ORMAN
P- number: P452292
Course code: IY499

Declaration of Own Work
I assure that this work is my own.
Wherever I have employed scholarly sources, I have performed in-text citations and have put the sources in the final reference list.

Introduction
This is a Python version of the hit video game Flappy Bird, coded withthe Pygame library.
It is a hands-on game development and object-oriented programmingexercise.
The game is about a bird that can be driven by the player. The objective is to steer the bird past a line of pipes without crashing into them or the ground. Points are awarded every time the bird successfully passes through a set of pipes.

Special Features
1-) Realistic gravity and jump physics
2-) Dynamic pipe generation with random vertical placement
3-) Smooth animation for bird and ground movement
4-) Sound effects for jumping and collisions
5-) Automatic game reset after game over
6-) Score display in real-time

This project demonstrates:
1-) Event handling
2-) Collision detection
3-) Surface blitting and layering
4-) Real-time animation with Pygame
5-) Code modularity and maintainability

Installation
To run the game, make sure you have Python installed on your system.
Then, install the required dependencies using:
pip install pygame
Alternatively, if a requirements.txt is provided:
pip install -r requirements.txt

How to Play
1-) Press the spacebar to make the bird flap upward.
2-) Avoid colliding with pipes and the ground.
3-) Try to pass through as many pipes as possible to increase your score.
4-) After a collision, the game will reset automatically and you can start again.

Running the Game
In the terminal or command prompt, navigate to the project directory and run:
python "Flappy Bird.py"
Running Unit Tests
If Flappy Bird Game.py is implemented in your project, you can run: Flappy Bird Game.py
This will execute all test cases and validate key components of the game.

Game Elements
a-) Bird: The player-controlled character affected by gravity and jumps.
b-) Pipes: Randomly generated vertical obstacles with gaps.
c-) Ground: Moving platform that simulates a scrolling background.
d-) Score System: Displays the number of pipes successfully passed.

Libraries Used
- pygame: A Python library for creating video games.

Project Structure
1-) Flappy Bird Game.py: Main game file

2-) Folder containing: Images and sound effects(img_45.png, img_46.png, img_47.png, img_48.png, img_49.png, img_50.png, greenpie.png, score.mp3, collision.mp3, jump.mp3)

3-) Requirements.txt: ((pip install -r requirements.txt) 

4-) Flappy Bird Test Error Handling.py: Test the error handling file for validating functionality.

5-) README.word: Project description and instructions

Unit Tests:
If included, unit tests are located in the Flappy Bird Game.py file. 
They may cover:
a-) Collision logic
b-) Pipe generation
c-) Score updating
d-) Reset mechanism

To run all tests:
Flappy Bird Game.py

License
This project is only for personal and academic purposes.
All the rights to the original game of Flappy Bird belong to its creators.

Enjoy the game!
Feel free to explore and improve upon the code.
