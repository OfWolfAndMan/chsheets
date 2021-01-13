## BASICS

### Define a integer

```Java
int myNumber = 1;
```
### Define a boolean

```Java
bool myBool = true;
```

### Define a single character

```Java
char myChar = "A"
```  

### Define 
### Write a comment

```Java
// Here's a comment
```

### Multiline comment


## OPERATORS

### And operator

```Java
System.out.println(true && true);
//prints true
```

### Or operator

```Java
System.out.println(true || false);
//prints true
```

### Not operator

```Java
System.out.println( !(4 <= 10) );
//prints false
```

### Order of operations

```Java
// 1. ! 2. && 3. ||

boolean riddle = !( 1 < 8 || (5 > 2 && 3 < 5));
System.out.println(riddle);
//Prints false
```

## CONDITIONALS/CONTROL FLOW

### If-then-else statement

```Java
int round;

if (round > 12) {

    System.out.println("The match is over!");
//This could also be written as
//if (round > 12) System.out.println("The match is over!");
//Since there isn't a block, just a single line
} else if (round > 0) {

    System.out.println("The match is underway!");

}	else {

    System.out.println("The boxing match hasn't started yet.");

}
```	

### Ternary Conditional

```Java
//Results in 'Y'
int fuelLevel = 3;

char canDrive = (fuelLevel > 0) ? 'Y' : 'N';
System.out.println(canDrive);
```

### Switch statement

```Java
//Results in default case
char penaltyKick = 'X';

switch (penaltyKick) {

    case 'L': System.out.println("Messi shoots to the left and scores!");
                        break; 
    case 'R': System.out.println("Messi shoots to the right and misses the goal!");
                        break;
    case 'C': System.out.println("Messi shoots down the center, but the keeper blocks it!");
                        //Needed to prevent the switch statement from continuing through conditions
                        break;
    default:
        System.out.println("Messi is in position...");

}
```

### Classes

```Java
//Inheritance used with "extends" statement
class Car extends Vehicle{
    //Instance Variable
    int age;
    //Class constructor (Object)
    public Car(int carsAge) {
       age = carsAge;     
    }
    //Defining a method (Actions of a constructor/object    )
    //"void" indicates to the method that no value
    //is returned after calling the method
    public void revUp() {
        System.out.println("Vroom!");
    }
    //Returns an integer (Has to return an integer)
    public int getAge() {
        return age
    }
    //Main method
    //Code in main is executed when script ran
    public static void main(String[] args) {
        //<Class> <Instantiation Name> = new <Class>(<age value>)
        Car myFastCar = new Car(12);
        //Outputs "Vroom!"
        myFastCar.revUp();
        //Returns age of car
        int myFastCarAge = myFastCar.getAge;
        System.out.println(myFastCarAge);
        //Applies inherited method
        myFastCar.checkBatteryStatus();
	}
}

class Vehicle {
    public void checkBatteryStatus() {
        System.out.println("The battery is 
        fully charged and ready to go!");
    }
}
```

## DATA STRUCTURES

### For Loop

```Java
for (int counter = 0; counter < 5; counter++) {

    System.out.println("The counter value is: " + counter);

}
```

### Array Lists

```Java
import java.util.ArrayList;
ArrayList<Integer> quizGrades = new ArrayList<Integer>();

### Manipulating the Array List
quizGrades.add(96);
quizGrades.add(62);
quizGrades.add(75);
//Adds 100 in position 0 (First entry)
quizGrades.add(0, 100);

### Accessing an Array value
//Returns 96
System.out.println( quizGrades.get(0) );

### Iterate over an Array List
//Size method used to return number of elements
//in array
for (int i = 0; i < quizGrades.size(); i++) {
    System.out.println( quizGrades.get(i) );
}
### For each item
//For each grade (int type) in (:) quizGrades
for (Integer grade : quizGrades){
    System.out.println(grade);
}
```

### Passing an Array List into a method


```Java
public int getAverage(ArrayList<Integer>){

}
```

### Hashmaps
```Java
import java.util.HashMap;
//Option for HashMap Types: <String>, <Integer>, <Boolean>
HashMap<String, Integer> myFriends = new HashMap<String, Integer>();

```
### Hashmap manipulation
```Java
myFriends.put("Bob", 25);
myFriends.put("Jane", 32);
myFriends.put("Zeno", 45);

```
### Access Hashmap
```Java
System.out.println( myFriends.get("Zenas") );
```

### Iterating through Hashmap
```Java
System.out.println( myFriends.size() );
//keySet for Hashmaps (Returns keys)
for (String name : myFriends.keySet()) {
    //Return key/value pairs
    System.out.println(name + " is age: " + myFriends.get(name));

}

```