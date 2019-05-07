# MotionFinder

If you have a folder full of videos and you want to know which video contains motion, then this is the answer.

## Usage

python motionfinder.py -ARGS

### Args
-d -- Required; this is the directory path to scan.

-t -- This is the movement threshold.  Default is 20, lower is more sensitive.

-q -- The size of the queue to use.  32 is the default.  If you get memory erros, lower it.

-v -- If you want frame by frame details to spew down the screen, set this to any value.

## Examples:
Scan files in curent directory:

python motionfinder.py -d .

Scan files in current directory with a larger queue:

python motionfinder.py -d . -q 128

Scan files in current directory and watch my screen fill with frame data:

python motionfinder.py -d . -v True
