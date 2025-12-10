# Simple C++ Password Cracker

This directory contains a minimal brute-force example written in C++ for educational use.

It increases the candidate length from 1 up to the limit you set, tries every character in the chosen charset at each position, and stops as soon as a generated attempt equals the target password. Attempt count and elapsed time are printed at the end.

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

See `password_cracker.md` for more details.
