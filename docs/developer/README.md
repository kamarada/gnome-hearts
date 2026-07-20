# Hearts Developer Guidelines

Source: <https://www.jejik.com/gnome-hearts/developers/>

This guide gives a brief overview of the Hearts package and related resources on this website.

## 0: Table of contents

- 1: Getting help
- 2: Obtaining the source
  - 2.1: From the web
  - 2.2: Through subversion
- 3: Compiling and installing
  - 3.1: Prerequisites
  - 3.2: Preparing the source
  - 3.3: Compiling and installing
- 4: Source overview
  - 4.1: The core game
  - 4.2: The player scripts
    - 4.2.1: Creating and editing players
    - 4.2.2: Datastructures and global variables
    - 4.2.3: Implementing the AI
    - 4.2.4: The Trick object
    - 4.2.5: Functions provided to you
- 5: Contributing
  - 5.1: Bugs and feature requests
  - 5.2: Translating Hearts
  - 5.1: Submitting patches

## 1: Getting help

This documentation (when complete) should give a good overview of the steps required to build, install and
modify the Hearts game. Right now it's still in the process of being written though. If you need any help
(or if you simply want to talk about the game) feel free to sign up to the
[Hearts mailing list](http://lists.jejik.com/cgi-bin/mailman/listinfo/hearts).

## 2: Obtaining the source

### 2.1: From the web

You can download a nightly snapshot of the Hearts trunk at: <http://www.jejik.com/files/gnome-hearts/gnome-hearts.snapshot.tar.gz>
You can also browse our Subversion repositories online at <http://svn.jejik.com>. You can also download a
release tarball from the [download](https://www.jejik.com/gnome-hearts/download) page, but because the game is constantly under development, the
release sources may be outdated.

### 2.2: Through Subversion

If you have [Subversion](http://subversion.tigris.org/) installed on your system, you can grab the latest
sources directly from the repository. Our repository is readable by guests (commits require an account though). Use
the following command:

```
svn checkout https://svn.jejik.com/gnome-hearts/trunk
```

## 3: Compiling and installing

### 3.1: Prerequisites

Before you can compile and install Hearts, you need several other packages and libraries:

- gnome 2 and GTK 2
- libgnomeui (plus headers)
- gnome-common (for the AM_GLIB_GNU_GETTEXT() m4 macro's)
- libglade2 (plus headers)
- gmodule (to make sure the --export-dynamic compiler flag is used. This is part of glib)
- python2.3 or better (plus headers)
- intltool and gettext (plus headers). You need intltool 0.41 for Subversion builds. Release packages can be built with an older intltool.

Aside from the packages and libraries listed in the above list, you also need a decent C build enviroment
(the build-essential package on Debian and deratives), the GNU autotools, the GNU gettext package and GNOME's intltool
package.

### 3.2: Preparing the source

Untar the sources somewhere convenient and run the `./bootstrap` script. If you downloaded a release tarball
then you can skip this step. Release packages are already bootstrapped. This script checks some things
in your build enviroment, processes some macro's and runs various autotools in the right order. If all goes well then
the only thing it will output is that you can run the `./configure` script (it will not run it for you, so you can play
with the standard `./configure` options yourself).

Note that you need a working internet connection for this step to fully execute. If you do not, then `./bootstrap`
will complain that it cannot get some config files from the internet. Download them yourself (or get them via other means), add
them in the package root directory and rerun the ./bootstrap. You need the following two files:

- <http://cvs.savannah.gnu.org/viewcvs/*checkout*/config/config/config.sub>
- <http://cvs.savannah.gnu.org/viewcvs/*checkout*/config/config/config.guess>

### 3.3: Compiling and installing

Compiling and installing is done the usual way (for GNU packages that is) through the invocation of the magical commands:

```
$ ./configure
$ make
$ sudo make install
$ make clean
```

If the `./bootstrap` ran without errors and you have all required libraries then there should be no errors. If you
find that other libraries than the one's listed above are required, please post to the mailing list so we can update this
document. The compilation will throw a few warnings at the end. These are caused by Python and can be ignored.

If you configure Hearts with the same prefix as you have installed gnome-games and gnome-games-extra-data then Hearts will
be able to use the card styles provided by those packages. Make sure you uninstall and version of hearts you already have
before doing so. Also, you should probabely delete the .gnome-hearts.cfg file from your home directory because hearts won't be
able to find the old paths. For most Linux systems you should configuring the package with:

```
./configure --prefix=/usr
```

## 4: Source overview

The Hearts source code consists of two main parts: the core game written in C and the computer opponents in various
Python scripts. If you want to work on the computer opponents then you don't need to know C. Simply edit the Python scripts
(or create a new player script) and put it in the /scripts/players directory.

### 4.1: The core game

The core game is written in C and can be found in the /src directory. The overview below lists what can be found where.

- `/src/background.c` - Manages the background image of the playingarea.
- `/src/cards.c` - Manages decks of cards, hands of cards and the trick. The game's scoring rules are implemented in here.
- `/src/cards-image.c` - Interface for the card faces.
- `/src/cfg.c` - Manages the configuration files.
- `/src/events.c` - Handles all GTK events. Also contains most of the game flow.
- `/src/hearts.c` - This contains the main() function and core game functions such as (re)starting games and rounds.
- `/src/player-api.c` - Contains the functions that are exposed to the Python AI players.
- `/src/player.c` - Here is the player's C implementation (play a card, pass cards, etcetera).
- `/src/preimage.c` - A helper object for cards-images.c that handles the source image data.
- `/src/ui.c` - This contains all the user interface functions that are not events.
- `/scripts/definitions.py` - More functions that player scripts can use.
- `/scripts/hearts.py` - Loads and registers all the players in the UI in C.
- `/scripts/player.py` - The base player class that AI p[layers derive from.

A note about cards: The only object that actually holds any cards is the `CardsDeck`. All other objects such
as hands of cards and the trick only pass around pointers to individual cards in the `CardsDeck`.

### 4.2: The player scripts

#### 4.2.1: Creating and editing players

The computer opponents are implemented as separate Python scripts in the `/scripts/players` directory. Each Python script
is a distinct player. If you want to create your own players, simply write a script and put it in the players
directory. If you want an example player script, take a look at the standard AI in `/scripts/stock_ai.py`. Just copy
that to `/scripts/players/your_player.py` and start editing it. The player should become selectable from the
preferences dialog.

Each player runs as a separate Python module inside the core hearts game. That means that you are free to use global
variables to keep track of things during the game over different tricks and rounds.

#### 4.2.2: Datastructures and global variables

The core game sets several class attributes in your player. These attributes are reïnitialized
before each function call, so feel free to munge them. Most of these attributes contain cards or lists of cards.
A card is a tuple with two values. The first value is the suit of the card and the second is the rank.
In Python you would define a card with:

```python
card = (1, 12)
```

You can use numbers, but for your convenience a range of global variables have been defined by the core game:

```python
clubs, diamonds, hearts, spades = 0, 1, 2, 3
ace, two, three, ... ten, jack, queen, king, ace_high = 1, 2, 3, ... 10, 11, 12, 13, 14
north, east, south, west = 1, 2, 3, 4
suit, rank = 1, 2
```

A list of cards in Python would look like:

```python
list = [(diamonds, 10), (spades, queen), (hearts, ace_high)]
```

The core game sets the following class attributes for you before calling one of your functions:

- **hand** — A list of cards that you have in your hand
- **trick** — An object that represents the trick that is being played by the players. See [4.2.4: The Trick object](#424-the-trick-object).
- **direction** — An integer value telling you which player you are.

#### 4.2.3: Implementing the AI

Your player must derive from the `Player` class, and your classname must be prefixed with `PlayerAI`.
At a bare minimum, your player must implement the `select_cards()` and `play_cards()` method. Hearts will
quit with a failed assertion if you do not provide these. The `select_cards()` method should return a list of
three cards that you want to pass on to the next player. The `play_card()` function should return a single *valid*
card that you want to play on this trick. You must also set the `self.name` attribute to string containing the name
of your AI as it should be used in the Hearts game.

Optionally, you can also provide a `trick_end()` or `round_end()` method. The `trick_end()` method
will be called at the end of a trick, when all four players have played their cards and the trick is full.
The `round_end()` function is called at the end of each round, after all cards have been played (and after the
`trick_end()` function).

#### 4.2.4: The Trick object

The Trick object represents the trick that is currently being played by the players. It has the
following attributes and methods.

- **card** — A list of four cards, representing the card played by north, east, south and west respectively. If a player has not played a card yet, it will be `None` instead of a tuple.
- **trump** — The suit of the first card played on the trick.
- **num_played** — The amount of cards played on the trick.
- **first_played** — The player (north, east, south or west) that started this trick.
- **get_winner()** — This method returns the winner of the trick or `None` if the trick has not finished yet.
- **get_highest_card()** — Returns the highest trump card on the trick.

#### 4.2.5: Functions provided to you

The core game also defines several usefull functions, filters and sorting methods you can use in your player scripts.
Filters can be used to filter lists of cards. An example:

```python
result_list = filter(f_filter_name, list)
```

Sorting methods can be used as such:

```python
list.sort(s_sort_name [, reverse=True])
```

- **have_suit(list, suit)** — Returns `True` if there are cards of the suit in the list, `False` otherwise.
- **f_clubs(card)** — A filter to get all clubs from a list.
- **f_diamonds(card)** — A filter to get all diamonds from a list.
- **f_spades(card)** — A filter to get all spades from a list.
- **f_hearts(card)** — A filter to get all hearts from a list.
- **f_pointless_cards(card)** — A filter to get all cards that are not worth any points.
- **f_point_cards(card)** — A filter to get all cards worth one or more points from a list.
- **s_rank(a, b)** — Sort cards by their rank value, then by suit. E.g: `[(spades, 1), (hearts, 1), (spades, 2)]`
- **s_suit(a, b)** — Sort cards by suit, then by rank. E.g: `[(spades, 1), (spades, 2), (hearts, 1)]`
- **s_points(a, b)** — Sort the cards ascending by their point value.
- **s_random(card)** — Randomize a list of cards.

## 5: Contributing

### 5.1: Bugs and feature requests

All bugs, feature requests and the like should go in [Bugzilla](http://bugzilla.jejik.com), but before you file a new one, please do a quick
search of bugzilla and the [mailing list archive](http://lists.jejik.com/pipermail/hearts/) to see if your issue has already been reported. We don't
expect you to search for hours, but do read the first page or so of results to see if your bug is listed.

### 5.2: Translating Hearts

Hearts is translated through Launchpad.net's [Rosetta](https://launchpad.net/) system. Translations should
be added and updated through there, not as diffs for the subversion repository. This makes our life easier because
we won't have to resolve conflicts between translations in Subversion and translations in Rosetta. You can find Hearts
in Rosetta as <https://launchpad.net/products/hearts/trunk/+pots/hearts>.

### 5.3: Submitting patches

If you have a patch that you want to contribute then you can send an e-mail to the Hearts mailing list at
hearts@lists.jejik.com. You must be subscribed to the mailing list to
do so (to prevent spammers abusing our lists). If you have a Subversion account on our server, you can commit it
directly. You might want to post it to the list before committing anyway so other people can proofread your code.
This goes especially for non-trivial patches.
