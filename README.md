A generator of fake data for Divergence Point Analysis
======================================================

The goal of this tool is to model the behavior of participants when performing
a Visual World Paradigm (VWP) task. It was created with the purpose of examining
how [Divergence Point Analysis](https://doi.org/10.1017/S1366728920000607)
is impacted by different analysis parameters. It can also be abused to do
anything else that requires fake data generation.

In a typical VWP task, participants come to the lab and sit in front of a
computer while wearing headphones and having their eye tracked by an
eye-tracker. At each trial, they hear a sentence and, at the
same time, are shown two or more objects (images) on the screen. The objects
normally relate to words of the sentence, and the participants are free to
look around towards any object they want. With the eye-tracker, we record
which object the participant was looking at at each point in time (say,
every millisecond). This leads to data that looks more or less like this:

|participant|condition|trial|time|    object    |is_looking|
|:---------:|:-------:|:---:|:--:|:------------:|:--------:|
|    P35    |    0    | T0  | 0  |  Target      |   1      |
|    P35    |    0    | T0  | 0  |  Distractor  |   0      |
|    P35    |    0    | T0  | 1  |  Target      |   1      |
|    P35    |    0    | T0  | 1  |  Distractor  |   0      |
|    P35    |    0    | T0  | 2  |  Target      |   1      |
|    P35    |    0    | T0  | 2  |  Distractor  |   0      |
|    P35    |    0    | T0  | 3  |  Target      |   1      |
|    P35    |    0    | T0  | 3  |  Distractor  |   0      |
|    P35    |    0    | T0  | 4  |  Target      |   1      |
|    P35    |    0    | T0  | 4  |  Distractor  |   0      |
|    P35    |    0    | T0  | 5  |  Target      |   1      |
|    P35    |    0    | T0  | 5  |  Distractor  |   0      |
|    P35    |    0    | T0  | 6  |  Target      |   1      |
|    P35    |    0    | T0  | 6  |  Distractor  |   0      |
|    P35    |    0    | T0  | 7  |  Target      |   1      |
|    P35    |    0    | T0  | 7  |  Distractor  |   0      |
|    P35    |    0    | T0  | 8  |  Target      |   1      |
|    P35    |    0    | T0  | 8  |  Distractor  |   0      |
|    P35    |    0    | T0  | 9  |  Target      |   1      |

That is, each row indicates whether a given participant is looking at a
given object.

In the following, you will learn more about what you need to use this tool,
what exactly each script produces, how to use them, and finally (if you are
interested) some technical details about how the data is generated.



What do I need in order to use it?
==================================

The package was created having in mind that many of its users could be
new to Python or to programming. Therefore, an attempt was made to keep
the number of dependencies to a minimum.
The following is a list of everything you'd need in order to use all features
of the programs. In the subsections below we describe how to get them
installed in your computer.

 * Python 3
 * pandas
 * scipy
 * plotnine


The scripts don't use any unorthodox feature of Python, so you should probably
be able to run this with any modern (say, less than 4 years old) version of
Python. The libraries the scripts depend on are also quite established and
haven't changed much in the last several years (and will probably not change
much either in the future). So you probably don't need to care much about the
versions. Still, if you want to know the version I have been using here, they
are:

 * Python 3.8.10
 * pandas 2.0.1
 * scipy 1.10.1
 * plotnine 0.12.1

In case you know what you are doing, you will also find a
`requirements.txt` file with a dump of my `pip freeze`.


Python 3
--------

### Windows and Mac users

If you are a Windows or Mac user, you can probably just go to
[the official Python webpage](https://www.python.org/), click on Download,
and choose the latest Python version. Or you can look through the list of
all versions to get the 3.8.10 (which comes with an installer in Windows).

When installing Python, make sure to select the option
"Add Python to PATH"
on the first screen of the installer.

**TODO**: MAKE IMAGE HERE FOR WINDOWS USERS

### Linux users

If you are in Linux, you may already have Python installed on your
computer. In that case, make sure that the version you have is correct
by running
```
$ python --version
```
In particular, make sure you **DO NOT** have Python 2. If you do, then
Python 3 may actually be called `python3` in your computer. You may
try running
```
$ python3 --version
```
to see what happens.

If you haven't Python 3 installed in your computer, then you probably want
to look for a package named something like "python3" in your package manager.
Debian-based users can probably just do
```
$ sudo apt install python3
```
to install a reasonably-new version Python 3 in their computer.

Installing pandas, scipy and plotnine
-------------------------------------

Python comes along with a program called `pip`, that works as a package
manager for Python libraries (it may be called `pip3` if your Python 3 is
called `python3`). In order to use it, you need to open a terminal
(in Mac, it is in `Applications->Utilities->Terminal`; in Windows, you
can press the Windows key, type `cmd` and press Enter) and type:
```
pip install pandas
pip install scipy
pip install plotnine
```
(in general, just the last line, `pip install plotnine`, is probably already
enough to install everything, but it is probably a good idea to still try
and run all three)

If you *absolutely* want the exact versions I was using, you can do
```
pip install pandas==2.0.1
pip install scipy==1.10.1
pip install plotnine==0.12.1
```


What does the tool do?
======================

The program is composed of two scripts (more about them in the next sections):

 * `dpa_fake_data_gen.py`: outputs a single dataset file
 * `run_generator.py`: repeatedly call `dpa_fake_data_gen.py`, generating many
    datasets

Each dataset file produced by `dpa_fake_data_gen.py` is formatted as a .csv
(comma-separated values) file, containing 7 columns (we will discuss what
these columns represent in more details below):

 1. (A column without a name): this is produced automatically, and can be
    safely ignored
 2. *participant*: the ID of the current participant
 3. *condition*: the ID of the current condition
 4. *trial*: the ID of the current trial
 5. *time*: the point in time (in milliseconds) this row refers to
 6. *object*: the object this row refers to
 7. *is_looking*: whether the participant *participant* was looking (1)
    or not (0) to *object* in time *time*.

      |participant|condition|trial|time|    object    |is_looking|
|:---:|:---------:|:-------:|:---:|:--:|:------------:|:--------:|
| 538 |    P35    |    0    | T0  | 0  |  Target      |   1      |
| 539 |    P35    |    0    | T0  | 0  |  Distractor  |   0      |
| 540 |    P35    |    0    | T0  | 1  |  Target      |   1      |
| 541 |    P35    |    0    | T0  | 1  |  Distractor  |   0      |
| 542 |    P35    |    0    | T0  | 2  |  Target      |   1      |
| 543 |    P35    |    0    | T0  | 2  |  Distractor  |   0      |
| 544 |    P35    |    0    | T0  | 3  |  Target      |   1      |
| 545 |    P35    |    0    | T0  | 3  |  Distractor  |   0      |
| 546 |    P35    |    0    | T0  | 4  |  Target      |   1      |
| 547 |    P35    |    0    | T0  | 4  |  Distractor  |   0      |
| 548 |    P35    |    0    | T0  | 5  |  Target      |   1      |
| 549 |    P35    |    0    | T0  | 5  |  Distractor  |   0      |
| 550 |    P35    |    0    | T0  | 6  |  Target      |   1      |
| 551 |    P35    |    0    | T0  | 6  |  Distractor  |   0      |
| 552 |    P35    |    0    | T0  | 7  |  Target      |   1      |
| 553 |    P35    |    0    | T0  | 7  |  Distractor  |   0      |
| 554 |    P35    |    0    | T0  | 8  |  Target      |   1      |
| 555 |    P35    |    0    | T0  | 8  |  Distractor  |   0      |
| 556 |    P35    |    0    | T0  | 9  |  Target      |   1      |


How do I use the tool?
======================



TODO
====

 * Add references to the following terms
    * Visual World Paradigm



