# Simple C++ Password Cracker

`password_cracker.cpp` is a minimal brute-force example for educational use. It tries every combination up to a chosen length using a configurable character set.

## How it works
- Builds an attempt string starting at length 1 and grows it up to the `max_length` you allow.
- Recursively walks through every character in the charset for each position, incrementing an attempt counter for each full guess.
- Compares each completed attempt to the target password and stops immediately when it matches.
- Reports whether the password was found, how many attempts were made, and how long the search took (measured with `std::chrono::steady_clock`).

Because it is pure brute force, search time grows exponentially with password length and charset size.

## Build
```bash
g++ -std=c++17 -O2 password_cracker.cpp -o password_cracker
```
Run the command from the `scripts` directory or adjust the path accordingly.

## Usage
```bash
./password_cracker <target_password> [max_length] [charset]
```
- `target_password`: the password you want to discover.
- `max_length`: optional maximum length to search (defaults to the target password length).
- `charset`: optional character set to try (defaults to lowercase letters and digits).

The program prints whether the password was found, how many attempts were made, and how long the search took.
