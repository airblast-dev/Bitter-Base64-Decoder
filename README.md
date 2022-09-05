# Bitter-Base64-Decoder
## What does Bitter! do ?
Bitter! is a discord bot that will read and detect base64 strings. For every base64 string it detects, it will add a numbered reaction.
A user can click on the reaction and Bitter! will DM the decoded version to them.

### Here is an example response:

![example](https://user-images.githubusercontent.com/67981946/188310549-87c513fc-bc13-46d6-bebc-a0e51f042c24.png)

## Can i add the bot to my server ?
Sure thing, just click [here](https://discord.com/oauth2/authorize?client_id=1004271933178773534&permissions=0&scope=bot%20applications.commands).

## What are the supported use cases ?
### User sent message's
It will work with base64 string's sent to a discord server's channel.

![bitter](https://user-images.githubusercontent.com/67981946/188309919-c32ffaf3-6b74-4950-b1e6-e8f5e6b750db.png)

It will also work with multiple base64 string's in a single paragraph.

![bitter-mult](https://user-images.githubusercontent.com/67981946/188310529-ea9c2952-654d-424e-9df4-f3ad3e780eec.png)

### [Rezi Bot by Wamy](https://github.com/Wamy-Dev/Rezi)
The bot also supports reading and reacting to strings from Rezi Bot. It will add a reaction for each result.

![rezi_bot](https://user-images.githubusercontent.com/67981946/188311530-69d1efa2-3ec9-42d5-b35a-f2570da4aabb.png)

## How do i use it ?
### Requirments
Install python 3.10 and latest version of pip.

Install the requirments (pip install -r requirements.txt).

Enter the bot's file and enter your bot token in the last line of the file.

You are ready to run Bitter!

### Parameters
Once you start the bot you will be asked a few questions.

1# First question will be Rezi Bot Support: if you intend to use it with Rezi Bot just respond with 'yes', if not leave it blank.

2# 'Soft cache limit' needs a little explaining: The bot will try to stay under this limit. Allthough it's very hard, the limit can technicaly be passed. Once the soft cache limit is reached it will calculate the average reaction usage of all message's. Message's under the average usage will get removed from the cache. If you set 0 it will disable soft caching with the exception of the last message that was reacted to.

3# 'Hard cache limit' is pretty straight forward: Once this limit is met. Half of the current cache will get removed. I recommend setting this a higher value than the 'Soft cache limit'. If you set 0 it will disable hard caching with the exception of the last message that was reacted to.

4# 'Logging': If you want to enable logging type in 'yes'. Enabling logging will create a file called auto_log.txt. In this file the message itself will be stored along with time and date.

### Final Notes
When the bot is running you can see if the reaction/messsage you used is in the cache or not. The program will tell you if the last usage was in the cache.

Setting 'soft cache limit' or 'hard cache limit' too low (setting either of them under 10 isn't recommended) can cause issues.
