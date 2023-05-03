from discord import User, Embed
from threading import Thread
from collections import deque
from datetime import datetime
from time import sleep
import asyncio


class MessageQueue(deque):
    """
    Only use for DM responses to avoid the bot getting quarantined by discord.

    While discord.py does abide rate limits. Extended duration of constant direct messages (even if within rate limits)
    can cause the bot to be quarantined. This isnt the be and end all to avoid it but its better than nothing.

    Items that are appended should be a tuple of a user, embed and the datetime of when it was added.
    """

    def __init__(self, test=None):
        super().__init__(test)
        self._message_thread: Thread = Thread(target=self._message_queue, daemon=True)
        self._message_thread.start()

    def _send_message(self, user: User, embed: Embed, t: datetime) -> None:
        """
        Sends only messages that were supposed to be sent within the last 30 seconds. Older messages will be ignored.
        If sending the message was delayed for more than 30 seconds its just ignored. Rather than sending a message a minute late,
        its better to just send the newer ones as at least it can keep working for some people rather than to keep everyone waiting
        for a possibly long amount time.

        I dont like this solution but i dont see another way.

        (Realistically anyone that waited more than a minute will likely decode the content through other means)
        """
        t_delta = datetime.now() - t
        was_sent = False
        if t_delta.total_seconds() < 30:
            was_sent = True
            asyncio.run(user.send(embed=embed))
        self.popleft()
        return was_sent

    def _message_queue(self):
        while True:
            while (i := (len(self))) > 0:
                current = self[0]
                was_sent = self._send_message(current[0], current[1], current[2])
                if was_sent is True:
                    sleep(1.5)
                self.high_load = i > 30
            sleep(0.01)


if __name__ == "__main__":

    class FakeUser:
        async def send(*args, **kwargs):
            print("Message Sent - Test Passed")

    test_messages = list()
    for i in range(0, 3):
        time = datetime.now()
        embed = Embed(description=str(i))
        test_messages.append((FakeUser, embed, time))
        sleep(1)

    MessageQueue(test_messages)
    sleep(5)
