#include <cmath>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

// Simple 3D vector helper to keep math tidy and commented
struct Vector3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    Vector3() = default;
    Vector3(double px, double py, double pz) : x(px), y(py), z(pz) {}

    Vector3 operator+(const Vector3 &other) const { return {x + other.x, y + other.y, z + other.z}; }
    Vector3 operator-(const Vector3 &other) const { return {x - other.x, y - other.y, z - other.z}; }
    Vector3 operator*(double scalar) const { return {x * scalar, y * scalar, z * scalar}; }

    Vector3 &operator+=(const Vector3 &other) {
        x += other.x;
        y += other.y;
        z += other.z;
        return *this;
    }

    double magnitude() const { return std::sqrt(x * x + y * y + z * z); }
};

// A simple particle affected by the black hole's gravity
struct Particle {
    Vector3 position;
    Vector3 velocity;
};

// Black hole representation that can calculate gravitational pull
class BlackHole {
public:
    BlackHole(double massKg, double eventHorizonRadiusMeters)
        : mass(massKg), horizonRadius(eventHorizonRadiusMeters) {}

    // Calculate gravitational acceleration on a particle using Newtonian gravity
    Vector3 accelerationFor(const Particle &particle) const {
        constexpr double G = 6.67430e-11; // Gravitational constant in m^3 kg^-1 s^-2
        Vector3 direction = {0.0, 0.0, 0.0};

        // Direction from particle toward the black hole (assumed at origin)
        direction = particle.position * -1.0;
        double distance = direction.magnitude();

        // Avoid division by zero and clamp extremely small distances
        if (distance < 1e-3) {
            distance = 1e-3;
        }

        // Normalize direction vector
        direction = direction * (1.0 / distance);

        // Newton's law of universal gravitation: a = G * M / r^2
        double accelerationMagnitude = (G * mass) / (distance * distance);

        return direction * accelerationMagnitude;
    }

    // Determine if a particle has crossed the event horizon
    bool isInsideEventHorizon(const Particle &particle) const {
        return particle.position.magnitude() <= horizonRadius;
    }

private:
    double mass;          // Mass of the black hole in kilograms
    double horizonRadius; // Event horizon radius in meters
};

// Advance the simulation by one time step using basic Euler integration
void stepSimulation(BlackHole &blackHole, std::vector<Particle> &particles, double deltaTimeSeconds) {
    for (auto &particle : particles) {
        Vector3 acceleration = blackHole.accelerationFor(particle);
        particle.velocity += acceleration * deltaTimeSeconds;
        particle.position += particle.velocity * deltaTimeSeconds;
    }
}

// Utility to print out the state of the system in a friendly format
void printState(const std::vector<Particle> &particles, int step) {
    std::cout << "Step " << std::setw(3) << step << ":\n";
    for (size_t i = 0; i < particles.size(); ++i) {
        const auto &p = particles[i];
        std::cout << "  Particle " << i << " | Position: (" << std::fixed << std::setprecision(2) << p.position.x
                  << ", " << p.position.y << ", " << p.position.z << ")";
        std::cout << " Velocity: (" << p.velocity.x << ", " << p.velocity.y << ", " << p.velocity.z << ")\n";
    }
}

int main() {
    // Create a black hole roughly equivalent to a 5-solar-mass stellar black hole
    const double solarMass = 1.98847e30;
    BlackHole blackHole(5.0 * solarMass, 15000.0); // 15 km event horizon (rough approximation)

    // Seed a handful of particles around the black hole with initial tangential velocity
    std::vector<Particle> particles{
        {{100000.0, 0.0, 0.0}, {0.0, 2500.0, 0.0}},
        {{0.0, -120000.0, 0.0}, {3200.0, 0.0, 0.0}},
        {{-140000.0, 140000.0, 0.0}, {-2100.0, -2100.0, 0.0}},
        {{80000.0, -80000.0, 0.0}, {1800.0, 1800.0, 0.0}},
    };

    const double deltaTime = 0.1; // seconds per simulation step
    const int totalSteps = 120;   // run a few seconds of simulated time

    for (int step = 0; step < totalSteps; ++step) {
        stepSimulation(blackHole, particles, deltaTime);
        printState(particles, step);

        // If any particle crosses the event horizon, let the user know
        for (size_t i = 0; i < particles.size(); ++i) {
            if (blackHole.isInsideEventHorizon(particles[i])) {
                std::cout << "  -> Particle " << i
                          << " has crossed the event horizon! (Capturing it in the black hole)\n";
            }
        }
    }

    std::cout << "Simulation complete. Increase totalSteps or adjust particle count to explore further.\n";
    return 0;
}
