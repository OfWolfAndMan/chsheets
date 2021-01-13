# Overview

- Purpose of a programming language
    - Prevent ambiguity
    - Provide verbose instruction
- Algorithm analysis
    - Procedure
        - Well-defined sequence of steps that can be executed mechanically
        - Guaranteed to always finish and produce correct result
- Requirements
    - Functional requirements
        - Operations
    - Non-functional requirements
        - Security
        - Help
        - Performance
        - Legal
        - Support
        - Usability
        - Reliability
    - Design requirements
    - Implementation requirements
    - Interface requirements
    - Physical requirements
- UML (Unified Modeling Language)
    - Not a programming language
    - Graphical notation of a system
    - Class diagram
        - Name
        - Attributes
        - Behaviors/Methods
    - Easy to sketch out an idea, regardless of programming language
    - Two commonly used formats
        - Use case
            - Title (Goal)
                - Short phrase, active verb
            - Person/Actor (Who desires it)
                - User, customer, member, administrator
- Steps needed to accomplish the goal
- User story
- Recursive Definitions
    - A recursive definition is a function calling itself, but with a slight modification, and something known as a base case to tell it when to stop so it does not loop indefiintely
    - Base case
        - A starting point not defines in terms of itself
        - Smallest input - already know the answer
    - Recursive case
        - Defined in terms of "smaller" version of itself
***

# String Methods

- .find()
    - Finds first string's specified position. -1 is specified if it is not found
    - Using .find(`<string>`,<number\>) will search beginning at the position specified by the number
- .upper()
    - Prints all string characters in upper case
- .lower()
    - Prints all string characters in lower case
- .title()
    - Returns the first character of the string as upper case, as if capitalizing for the beginning of a sentence
- .isupper() OR .islower()
    - Returns true if there is at least one upper or lower case character
- .isalpha
    - Returns true if the string consists of only letters and is not blank
- .isalnum
    - Returns true if the string consists of only letters and numbers and is not blank
- .isdecimal
    - Returns true only if string consists of numeric characters and is not blank
- .isspace
    - Returns true only if the string consists of spaces, tabs, and new lines and is not blank
- .istitle
    - Returns true only if the string consists of words that begin with an uppercase letter followed by lowercase
- .startswitch()
    - Returns true if string starts with characters defined in string method's parentheses
- .endswith()
    - Returns true if string starts with characters defined in string method's parentheses
- .join()
    - Used to join values in parentheses based on delimiter defined to the left of the .join()
- .split()
    - Used to split values to the left of .split() based on the delimiter defined in the parentheses
- .rjust(), .ljust(), .center()
    - Used to justify text. To define a certain integer length of the string, insert a number in parentheses
    - Default character to fill the remaining of the string is space. To change that, define it in the parentheses after a comma next to the integer in parentheses
    - i.e. 'Hello'.center(20, '=')
    - '=======Hello======='
- .strip(), .lstrip(), .rstrip()
    - Used to strip off excess space, tabs and newlines from one side or both sides of text
    - You can also strip based on a delimiter in the parentheses, but only by single characters
    - i.e. 'SpamSpamBaconSpamEggsSpamSpam'.strip('apS') will strip the string to 'BaconSpamEggs'
- .sub('substitution string', 'Original string')
    - Used to substitute specified criteria
- .read('file')
    - After using 'import sys' and opening the file (open('file')), outputs the file's text to the screen, in a very poorly formatted way
- Import pyperclip and then use .copy() and.paste()
    - Used to copy and paste text where applicable
- Regex symbols
    - \d (Any numeric digit from 0-9)
    - \D (Any character that is not a numeric digit from 0-9)
    - \w (Any letter, the numeric digit, or underscore character)
    - \W (Any character that is not a letter, numeric digit, or the underscore character)
    - \s (Any space, tab, or newline character)
    - \S (Any character that is not a space, tab or newline character)
    - ^(Used at the start of a regular expression to indicate the match must occur at the beginning of the searched text)
    - $ (Used at the end of a regular expression to indicate the match must occur at the end of the searched text)
    - . (Wildcard character. Matches only one character)
    - [abc] (Matches any characters in the brackets)
    - [^abc] (Matches any characters not in the brackets)
    - ? (Matches zero or one of the preceding group)
    - * (Matches zero or more of the preceding group)
    - + (Matches one or more of the preceding group)
***

# Functions

- Procedures and control
    - Procedure: Takes an input, changes it, and outputs it
- Def `<name>` (`<input1>`,`<input2>`):
    - `<block1>`
    - `<block2>`
- Parameters
    - Variable. Can be one or more names or inputs
- Block
    - The code that runs to execute the procedure
- Return `<expression>`, `<expression2>`
    - Output to input
- Using a function
    - Input/Paramaters: AKA operands/arguments
- Built-in functions
    - Len() - Returns the length (As an integer) of the string
- Importing built-in functions (Modules)
    - Import `<module>`
    - `<module>`.`<subcomponent>`()
        - Invokes a specific function within the module
    - From `<module>` import `<submodule>` | *>
        - (Imports a function nested within a built-in module
        - Using the '*' option imports every component in that module

***
# File Handling

- `<variable>` = open('file.ext', 'mode')
    - Opens a file with the mode either r (Read), w (Write), or a (Append)
    - R+ is used for both read and write permissions
- `<variable>`.read(`<size in bytes>`)
    - Outputs the file onscreen
    - Additional option size in bytes only outputs that specific bytes in the file
- `<variable>`.close()
    - Closes the file
- `<variable>`.readline()
    - Reads a particular line of the text
- With open('`<file name>`') as `<variable>`:
    - Contents = `<variable>`.[read | write]()
    - Print contents
    - In addition, you do not need to call .close() to close the file. It

***

# Booleans

- a = True
- b = False
- True and false must be capitalized
- type(a)
    - <type 'bool'>
- Operators
    - ==
    - !=
    - <
    - \>
    - \>=
    - <=
    - == vs =
        - = means an assignment
        - == is a comparison
    - %
        - Modulus. If the left number is divisible the right number, as to return an integer rather than a float, it will return 0 (i.e. 24 % 3 == 0)

***

## Setting up tox
##Primarily used to test projects in different versions of Python primarily
```Python
pip install tox
```
Should be run in the same directory as setup.py file

### Specifying a platform
```Python
[testenv]
platform - linux2|darwin
```
### Specify dependencies file
```Python
deps =
    -requirements.txt
```
### Integrating pytest in the tox file
```Python
commands =
    py.test {posargs}
```

## Using pytest
Create a "tests" folder. Run the "pytest" function when done, and it will recursively run tests on all test*.py or *test.py files


## Multithreading issues in python
- Not problematic on a small scale, large
  amounts of memory issues at scale can be 
  observed
- Leads to race conditions, resource starvation
  at scale
- Alternative: Asyncio