# DumbSophomores Catastrophe Client

If siggame is still hosting the game server, go into the root directory of this client and join a match called MATCH_NAME with
```
./run Catastrophe -s game.siggame.io -r MATCH_NAME
```
Else, you will need to run [Cadre, siggame’s game server,](https://github.com/siggame/Cadre/blob/master/howToPlay.md) locally. 
If you get that to work, you can run this client in a match named MATCH_NAME with
```
./run catastrophe -r MATCH_NAME
```
since the server defaults to localhost.  Look in Cadre/Cerveau/output/gamelogs for the game logs.  You will probably need to run [their visualizer server](https://github.com/siggame/Viseur) to view the game described in the logs. 

DumbSophomores used Python3 for Catastrophe.
