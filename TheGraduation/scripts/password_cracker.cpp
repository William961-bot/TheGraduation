#include <chrono>
#include <iostream>
#include <string>

namespace {
void bruteForceRecursive(const std::string &charset,
                         const std::string &target,
                         std::string &attempt,
                         std::size_t index,
                         bool &found,
                         std::uint64_t &attempts) {
  if (found) {
    return;
  }

  for (char ch : charset) {
    attempt[index] = ch;
    if (index + 1 == attempt.size()) {
      ++attempts;
      if (attempt == target) {
        found = true;
        return;
      }
    } else {
      bruteForceRecursive(charset, target, attempt, index + 1, found, attempts);
      if (found) {
        return;
      }
    }
  }
}

void bruteForce(const std::string &charset, std::size_t maxLength,
                const std::string &target) {
  auto start = std::chrono::steady_clock::now();
  bool found = false;
  std::uint64_t attempts = 0;

  for (std::size_t length = 1; length <= maxLength && !found; ++length) {
    std::string attempt(length, charset.front());
    bruteForceRecursive(charset, target, attempt, 0, found, attempts);
  }

  auto end = std::chrono::steady_clock::now();
  auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

  if (found) {
    std::cout << "Password found: " << target << "\n";
  } else {
    std::cout << "Password not found within the provided limits.\n";
  }

  std::cout << "Attempts: " << attempts << "\n";
  std::cout << "Elapsed: " << duration.count() << " ms\n";
}

void printUsage(const std::string &program) {
  std::cout << "Usage: " << program
            << " <target_password> [max_length] [charset]\n\n";
  std::cout << "Parameters:\n";
  std::cout << "  <target_password>  The password to brute force.\n";
  std::cout << "  [max_length]       Optional maximum length to search (defaults to"
            << " target length).\n";
  std::cout << "  [charset]          Optional character set to try (defaults to"
            << " lowercase letters and digits).\n";
}
} // namespace

int main(int argc, char *argv[]) {
  if (argc < 2) {
    printUsage(argv[0]);
    return 1;
  }

  const std::string target = argv[1];
  std::size_t maxLength = target.size();
  if (argc >= 3) {
    try {
      maxLength = static_cast<std::size_t>(std::stoul(argv[2]));
    } catch (const std::exception &) {
      std::cerr << "Invalid max_length provided.\n";
      return 1;
    }
  }

  std::string charset = "abcdefghijklmnopqrstuvwxyz0123456789";
  if (argc >= 4) {
    charset = argv[3];
  }

  if (charset.empty()) {
    std::cerr << "Charset cannot be empty.\n";
    return 1;
  }

  if (maxLength == 0) {
    std::cerr << "max_length must be greater than zero.\n";
    return 1;
  }

  std::cout << "Brute forcing password up to length " << maxLength << " using charset: "
            << charset << "\n";
  bruteForce(charset, maxLength, target);

  return 0;
}
