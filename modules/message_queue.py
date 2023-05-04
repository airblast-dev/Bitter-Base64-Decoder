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

    high_load: Is True if there is more than 20 messages in the queue or _soft_load is bigger than 100.
    """

    high_load = False
    _soft_load: int = 0

    def __init__(self, loop=None):
        self.loop = loop
        super().__init__()
        self._message_thread: Thread = Thread(target=self._message_queue, daemon=True)
        self._message_thread.start()

    def _send_message(self, user: User, embed: Embed, t: datetime) -> bool:
        """
        Sends only messages that were supposed to be sent within the last 30 seconds.
        If sending the message was delayed for more than 30 seconds its just ignored. Rather than sending a message a minute late,
        its better to just send the newer ones as at least it can keep working for some people rather than to keep everyone waiting
        for a possibly long amount of time.

        I dont like this solution but i dont see another way.

        (Realistically anyone that waited more than a minute will likely decode the content through other means)
        """
        t_delta = datetime.now() - t
        was_sent = False
        if t_delta.total_seconds() < 30 or self._soft_load < 100:
            was_sent = True
            asyncio.run_coroutine_threadsafe(user.send(embed=embed), self.loop)
        self.popleft()
        return was_sent

    def _message_queue(self):
        """Discord doesnt exactly tell anyone what is considered flaggable or spam so this is my solution with the numbers i pulled from my backside."""
        while True:
            message_count = 0
            if self._soft_load < 0:
                self._soft_load = 0
            while (i := (len(self))) > 0:
                current = self[0]
                was_sent = self._send_message(current[0], current[1], current[2])
                if was_sent is True:
                    message_count += 1
                    self._soft_load += 5
                    sleep(1.5)
                else:
                    self._soft_load -= 1
                self.high_load = (True if i > 20 else False) or (
                    True if self._soft_load > 100 else False
                )
            self._soft_load -= message_count / 10 if message_count / 10 > 0.1 else 0.1
            sleep(0.05)
