Make sure all dependencies are installed before starting as specified in the `requirements.txt` file.

To fetch all highlights and create a deck run

`$ python incremdoro.py`

```
$ python incremodoro.py  --help
usage: incremodoro.py [-h] [--notes] [--bookmarks] [--match pattern] [--delete] [--dempty]

Incremodoro

optional arguments:
  -h, --help       show this help message and exit
  --notes          Review all empty notes.
  --bookmarks      Review all bookmarks.
  --match pattern  Find highlights matching pattern
  --delete         Delete highlights after they are put in flashcard deck
  --dempty         Delete empty highlights that match pattern
```

## Format of highlights
To create a highlight in O`Reilly you need to use the following format.
1. Highlight interesting fact
2. Add note with the following format `What is the question? &| This is the answer. #Tag1 Tag2`
3. Run script