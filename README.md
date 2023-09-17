# chat-summary

Use this library to get a summary of results of internet games (like Wordle) in a group chat.

![Tests](https://github.com/samirg1/ALTER-SMX-Tool/actions/workflows/tests.yml/badge.svg)
![python](https://img.shields.io/pypi/pyversions/chat-summary?logo=python)
![pypi](https://img.shields.io/pypi/v/chat-summary?logo=pypi)
![downloads](https://static.pepy.tech/badge/chat-summary)
![code style](https://img.shields.io/badge/code%20style-black-000000.svg)

### Requirements
- Only works on MacOS with iMessages
- Must have messages [stored in iCloud](https://support.apple.com/en-au/guide/messages/icht5b5d1e63/mac#:~:text=In%20the%20Messages%20app%20on,all%20of%20them%20to%20appear.) (or simply on Mac)
- Only works for group chats
- Having [contacts synced](https://support.apple.com/en-au/101336) to your Mac as well is not essential but allows for better viewage of results

### Installation
```python
pip install chat-summary
```

### Usage
```python
chat-summary user chat_name [options]
```

#### Options
- user (required): The name of the user with the messages
- chat_name (required): The name given to the messages group chat
- --silence-contacts: Silecne the "unable to find contacts" error
- '-C', '--Connections': Include the 'Connections' game in the results
- '-N', '--Nerdle': Include the 'Nerdle' game in the results
- '-W', '--Wordle': Include the 'Wordle' game in the results

### Output
For each game you opt-in to you will be shown an output like this:
```
🟨🟨🟨 {game} 🟨🟨🟨

COMPLETIONS ({n} days)
1. *********..{c}/{a}
2. *******....{c}/{a}
3. ******.....{c}/{a}
...

AVERAGE GUESSES
1. *********..{av}
2. *******....{av}
3. ******.....{av}
...
```
Where:
- {game} is the name of the game
- {n} is the total amount of {game}s between the first message with {game} and the last
- '******' are replaced by either the contact name or phone numbers of each group chat member (depending on whether contacts are available)
- {c} is the amount of {game}s this person has completed (won)
- {a} is the amount of {game}s this person has attempted
- {av} is the average amount of guesses this person used in a 'win' of {game}
- Completions are sorted from most completed ({c}) to least completed
- Average guesses are sorted from lowest to highest

If there are no messages for a particular game that you have opted-in to you will see something like this instead:
```
🟥 no '{game}' messages found 🟥
```
Where {game} is replaced by the game that there were no messages for.

### Errors

- ```"user not found, user should be one of: ..."```
    - user parameter was invalid, check that you've spelt it correctly and that you are a valid user in the ```\Users``` directory
-  ```"could not connect to messages database, ensure you have the right permissions to access file"```
    - Ensure you have the right permissions to view the `chat.db` by going System Preferences > Securiy & Privacy > Full Disk Access and ensure that Terminal (or whatever you are using to run the script) is ticked
- ```"could not find stored messages, ensure you have signed in and uploaded iMessages to iCloud"```
    - Ensure there is a `chat.db` file in `\Users\{your user}\Library\Messages`, if not your messages are not stored locally on your Mac, try logging in to iMessage on your Mac and [uploading the messages to iCloud](https://support.apple.com/en-au/guide/messages/icht5b5d1e63/mac#:~:text=In%20the%20Messages%20app%20on,all%20of%20them%20to%20appear.)
- ```"chat name not found, should be one of: ..."```
    - you have entered an invalid chat_name argument that doesn't match up with any group chats you are currently in on iMessage
- ```"unable to find contacts"```
    - not a destructive error, means that the program could not find contacts that were stored on your computer, so instead of displaying people's names it will instead display their phone numbers in the summary, silence this warning with the `--silence-contacts` option
    - the program will look for a `'AddressBook-v22.abcddb'` file somewhere in `'/Users/{your user}/Library/Application Support/AddressBook/Sources'`

### Add your own!

If you have your own internet games that are similar to Wordle and are not currently supported [raise an issue](https://github.com/samirg1/chat-summary/issues/new?assignees=samirg1&labels=new-game&projects=&template=new-game.md&title=%5BNew+Game%5D)  and it will be implemented as soon as possible.
