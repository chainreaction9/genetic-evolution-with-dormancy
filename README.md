Chain Reaction Webapp
==================

This is an open source [web application](https://chainserver.pythonanywhere.com) designed for playing the android game [Chain Reaction](https://brilliant.org/wiki/chain-reaction-game/) on web browsers. The project includes both the frontend and the backend implementation of the webapp. For the frontend development, typescript language and [WebGL](https://www.khronos.org/webgl/) API are used to create a client-side javascript module containing the helper functions of the game. For the backend, a Flask webserver is designed in python which enables players to play the game worldwide after [signing in](https://chainserver.pythonanywhere.com/chainreaction-online/login) with a free account! The app makes use of the [Pusher](https://pusher.com/) library for communicating with the online players. The user data is stored in a [MySQL](https://www.mysql.com/) database and mail functionality is available.

![Webapp image](/chain-reaction-online.png)

### About the Chain Reaction game.
_________________________________
This is a strategy based board game between two or more players. Each player gets a turn to occupy board-cells by either capturing an empty cell or by invading cells occupied by other players. The goal of the game is to eliminate all other players by capturing their cells. 

An invasion is caused by filling an already occupied cell beyond its critical mass. As per the common rule of this game, the critical mass of each board-cell is equal to one less than the number of its neighbours. A chain reaction is created if enough neighbouring cells reach their critical mass. More details on the rules can be found [here](https://chainserver.pythonanywhere.com) which is a webapp hosting this game.

Source building
---------------
The project can be built with a typescript compiler (version >= 4.7) and require Python (version >= 3.0) to run the Flask webserver. In order for the typescript compilation to be successful the following dependencies must be available in the dev environment.
### Frontend dependency
1. [glMatrix](https://glmatrix.net/)
2. [jQuery](https://jquery.com/)
3. [pusher-js](https://github.com/pusher/pusher-js/)
4. [webgl-obj-loader](https://www.npmjs.com/package/webgl-obj-loader)

The frontend dependencies are listed in `package.json` and can be installed by running the following command from the project root directory:
```bash
npm install .
```
### Backend dependency
These python modules are needed for the Flask webserver to run:
1. Flask>=2.2
2. Flask-Session>=0.4
3. Flask-Login>=0.5
4. Flask-Mail>=0.8
5. Flask-MySQL>=1.0
6. Flask-Bcrypt>=1.0
7. pusher>=2.1
8. validate-email

The backend dependencies can be installed by running either the command `pip install -r requirements.txt`, or `npm run-script pydep` from the project root directory. To install both frontend and backend dependencies, run the following command from project root directory:
```bash
npm run-script dev
```
After successful compilation of the typescript source files with the command
```bash
npm run-script build
```
the webserver can be run with the command `npm run-script start`.

## Future ideas
- Add chat feature among online players with the Pusher API.
- Add options to play with AI bot.

Please fork this project and make a pull request if you wish to contribute.
