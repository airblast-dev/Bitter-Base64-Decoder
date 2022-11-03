# Bitter-Base64-Decoder
## What does Bitter! do ?
Bitter! is a discord bot that will read and detect base64 strings. For every base64 string it detects, it will add a numbered reaction.
A user can click on the reaction and Bitter! will DM the decoded version to them.

### Here is an example response:

![example](https://user-images.githubusercontent.com/67981946/188310549-87c513fc-bc13-46d6-bebc-a0e51f042c24.png)

## Can i add the bot to my server ?
Sure thing, just click [here](https://discord.com/oauth2/authorize?client_id=1004271933178773534&permissions=2147511360&scope=bot%20applications.commands).

## What are the supported use cases ?
### User sent message's
It will work with base64 string's sent to a discord server's channel.

![bitter](https://user-images.githubusercontent.com/67981946/188309919-c32ffaf3-6b74-4950-b1e6-e8f5e6b750db.png)

It will also work with multiple base64 string's in a single paragraph.

![bitter-mult](https://user-images.githubusercontent.com/67981946/188310529-ea9c2952-654d-424e-9df4-f3ad3e780eec.png)

### Bot sent embed messages:
All bot sent messages should get read including embed and such formats.

### Edited messages:
Edited messages will also get updates automatically and remove or add reactions if needed. Edited messages will only scan for enabled settings and update based off of current settings. If you want to update a message with content not enabled you should use FindB64 or temporarily toggle on whatever type you want to be found.

![edit_example](https://user-images.githubusercontent.com/111659262/199730265-641d6339-d27d-4ad4-b145-4dbed5f2bd53.gif)

![reation_update_example](https://user-images.githubusercontent.com/111659262/199742423-ae455236-5a74-4ab7-93c3-db1523de4944.gif)


### Other supported formats:
If a detection is enabled and text is found alongside the enabled detection, clicking the reaction will send you a decoded version of the whole base64 text. See example as below:

![text_including_url_example](https://user-images.githubusercontent.com/111659262/199734416-2d1fed9f-54db-4a12-8bf8-b75bc83093d6.gif)

## Commands and Applications:

### Commands:
  
#### /toggle
The /toggle command will enable specific detections based on the user input. For example /toggle UrlB64 enable's detecting base64 encoded Url's. Using the command will enable it if was disabled and disable it if was enabled. Using the command will also send a current settings list. Currently the bot supports automatic TextB64 UrlB64 and MagnetB64 detection. By default Url detection is enabled and should work out of the box.

![image](https://user-images.githubusercontent.com/111659262/199736743-0ceb1bf7-8196-4d18-88cc-fb6cdc375f0d.png)
![image](https://user-images.githubusercontent.com/111659262/199736792-f3da2ae4-b795-444c-a4da-73eb2b1e88ca.png)



#### /encodeb
The /encodeb command encode's any input and sends the result to the channel that the command was used in. The output will always be reacted by Bitter.

![image](https://user-images.githubusercontent.com/111659262/199736691-fd86c6b2-13ff-4563-aefa-46db8a721c28.png)


#### /usageb
This command sends how many times Bitter has been used since November  1st.

![image](https://user-images.githubusercontent.com/111659262/199736607-4bb9d4e9-0b67-49bf-bb36-a130f10f12f3.png)


### Applications:

#### FindB64:
Using FindB64 on a message will force find any base64 content. 

![image](https://user-images.githubusercontent.com/111659262/199736561-7ca16149-8c5a-409b-a4e3-2c89537f1043.png)


### Requirments
Install python 3.10 and latest version of pip.

Install the requirments (pip install -r requirements.txt).

Enter the bot's file and enter your bot token in the last line of the file.

You are ready to run Bitter!

