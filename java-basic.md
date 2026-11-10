---
title: Java
summary: Java — language core, records, streams, modern switch, virtual threads
tags: [language, java]
tooling: [openjdk, javac]
verified_on: 2026-11-10
verified_env: OpenJDK 27.0.1, Linux
status: verified
---

# Java

Compiled and run against OpenJDK 27. The 2021 version of this sheet stopped at
primitives and operators; everything from `var` onward is new here. LTS releases are
21 and 25 — if you are starting a project today, that is where to aim, and the
features below are all present in 21.

## Structure of a program

```java
public class Main {
    public static void main(String[] args) {
        System.out.println("hello");
    }
}
```

```bash
javac Main.java        # produces Main.class
java Main              # runs it
```

Since Java 11 a single file runs without a build step:

```bash
java Main.java
```

## Types and variables

```java
int count = 1;
long big = 1_000_000L;         // underscores are legal in numeric literals
double ratio = 0.5;
boolean ready = true;
char code = 'A';
String name = "host1";

var port = 22;                 // inferred: int. Readable shorthand, not dynamic typing
final int MAX = 100;           // final = cannot be reassigned
```

Primitives have no null; wrappers do:

```java
Integer boxed = null;          // legal
int unboxed = boxed;           // NullPointerException at runtime
```

## Strings

```java
String host = "host1";
String label = "%s:%d".formatted(host, 22);      // preferred over String.format
String joined = String.join("-", "a", "b", "c");

boolean matches = "abc123".matches("[a-z]+\\d+");
String replaced = "a-b-c".replace("-", "_");
String[] parts = "a,b,c".split(",");

var block = """
        line one
        line two
        """;                                    // text block, keeps newlines
```

Strings are immutable. A loop that concatenates thousands of pieces should use
`StringBuilder`.

## Collections

```java
import java.util.*;

List<String> names = new ArrayList<>(List.of("a", "b"));
names.add("c");

Map<String, Integer> ports = new HashMap<>();
ports.put("ssh", 22);
ports.getOrDefault("http", 80);

var fixed = List.of("x", "y");       // immutable
var copy = new ArrayList<>(fixed);   // mutable copy

for (Map.Entry<String, Integer> e : ports.entrySet()) {
    System.out.println(e.getKey() + "=" + e.getValue());
}
```

`List.of` and `Map.of` are immutable and reject nulls — a good default.

## Records

A record is an immutable data carrier with `equals`, `hashCode`, `toString` and
accessors generated:

```java
public record Interface(String name, int mtu) {
    public Interface {
        if (mtu < 68) throw new IllegalArgumentException("mtu too small");
    }
    public String label() { return name + "/" + mtu; }
}
```

## Streams

```java
import java.util.*;
import java.util.stream.*;

List<String> longNames = List.of("ab", "abcd", "abcdef").stream()
        .filter(s -> s.length() > 3)
        .map(String::toUpperCase)
        .sorted()
        .toList();

int total = IntStream.rangeClosed(1, 10).sum();

Map<Integer, List<String>> byLength = List.of("a", "bb", "cc").stream()
        .collect(Collectors.groupingBy(String::length));
```

Streams express transformation; loops express mutation. Use `forEach` for side effects
sparingly.

## Switch expressions and pattern matching

```java
static String describe(Object o) {
    return switch (o) {
        case Integer i when i > 100 -> "big int " + i;
        case Integer i -> "int " + i;
        case String s -> "string of length " + s.length();
        case null -> "null";
        default -> "other";
    };
}
```

Arrow labels do not fall through, and `switch` is an expression that returns a value.

Sealed types make the hierarchy closed, so the compiler can check exhaustiveness:

```java
public sealed interface Shape permits Circle, Square {}
record Circle(double r) implements Shape {}
record Square(double s) implements Shape {}

static double area(Shape shape) {
    return switch (shape) {
        case Circle c -> Math.PI * c.r() * c.r();
        case Square s -> s.s() * s.s();
    };
}
```

## Optional

```java
Optional<String> maybe = Optional.ofNullable(System.getenv("HOME"));
String home = maybe.orElse("/tmp");
maybe.ifPresent(h -> System.out.println(h));
```

Do not use `Optional` for fields or parameters; it is a return type for "may be absent".

## Exceptions and resources

```java
try (var reader = java.nio.file.Files.newBufferedReader(
        java.nio.file.Path.of("/etc/hostname"))) {
    System.out.println(reader.readLine());
} catch (java.io.IOException e) {
    System.err.println("read failed: " + e.getMessage());
}
```

`try`-with-resources closes anything `AutoCloseable`, including when the body throws.

## Virtual threads

Java 21 made threads cheap enough to use one per task:

```java
try (var pool = java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
    var future = pool.submit(() -> {
        Thread.sleep(100);
        return "done";
    });
    System.out.println(future.get());
}
```

For I/O-bound work this replaces most hand-rolled thread pools.

## Files and paths

```java
import java.nio.file.*;

Path p = Path.of("/etc/hostname");
String text = Files.readString(p);
Files.writeString(Path.of("/tmp/out.txt"), "done\n");
try (var lines = Files.lines(p)) {
    lines.forEach(System.out::println);
}
```

`java.nio.file` replaced `java.io.File` for new code.

## Build tools

```bash
# Gradle
gradle init --type java-application
gradle build test
gradle run --args="one two"

# Maven
mvn archetype:generate -DgroupId=com.example -DartifactId=demo
mvn -q compile exec:java
```

```groovy
// build.gradle
plugins { id 'java'; id 'application' }
java { toolchain { languageVersion = JavaLanguageVersion.of(21) } }
application { mainClass = 'com.example.Main' }
```

A toolchain block pins the compiler version independently of the JDK running Gradle.

## Traps worth remembering

- `==` on objects compares references; use `.equals` for value equality.
- Integer caching makes `==` appear to work for small ints and fail above 127.
- `List.of(...)` is immutable; `Arrays.asList(...)` is fixed-size but settable.
- Checked exceptions must be declared or caught; unchecked ones need not be, which is
  not permission to ignore them.
- `HashMap` iteration order is unspecified; use `LinkedHashMap` or `TreeMap` when
  order matters.
