# tools/simulate_attack.py

import time
import random

LOG_FILE = "./logs/simulated_auth.log"

attackers = ["45.33.32.156", "192.168.1.100", "10.0.0.55"]
users = ["root", "admin", "ubuntu", "test", "user"]

def simulate_brute_force(ip, count=8):
    """
    Writes fake failed logins to the log file.
    Simulates a hacker trying passwords repeatedly.
    """
    print(f"\n[ATTACKER] Starting brute force from {ip}")
    print(f"[ATTACKER] Will try {count} passwords...\n")

    with open(LOG_FILE, 'a') as f:
        for i in range(count):
            # Write one fake failed login line
            line = (
                f"Mar 12 03:14:{i+10} server sshd[1234]: "
                f"Failed password for {random.choice(users)} "
                f"from {ip} port 22 ssh2\n"
            )
            f.write(line)
            f.flush()  # Make sure it's written immediately

            print(f"  Attempt {i+1}: Failed password from {ip}")
            time.sleep(0.5)  # Half second between attempts

    print(f"\n[ATTACKER] Done! Wrote {count} fake attacks to log.")


if __name__ == "__main__":
    random_attacker = random.choice(attackers)
    simulate_brute_force(random_attacker)