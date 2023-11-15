# TalkyHand

This project focuses on developing an interactive system that recognizes hand gestures and translates them into American Sign Language (ASL) alphabet. It serves as both a sign language translator and an interactive prompter. The system incorporates features such as hand tracking, gesture recognition, motion recognition, and speech recognition, providing a comprehensive solution for communication. The user interface allows for dynamic interaction, with networking capabilities enabling communication between devices. Please refer to the setup guide for installation and usage instructions.

More details are available in the [project report](deliverables/TalkyHand%20-%20Report.pdf).

## Setup Guide

To ensure optimal display, use a resolution of 1920x1080 with resizing set at 100%. The project has been tested with Python 3.9.0 and Python 3.11.5.

1. Clone the repository:

```bash
git clone https://github.com/iantonov99/TalkyHand.git
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the application:

```bash
python userInterface.py
```

## Network Setup

For single computer testing:

Create a file named `.env` with the following content:

```env
HOSTNAME = "localhost"
PORT = 5555
```

If connecting to another computer:

1. Specify the other PC's IP address as the `HOSTNAME` in the `.env` file.
2. Use the same `PORT` on both computers.

Make sure that the firewall is not blocking the connection, that the port is open, and that the two computers are on the same network.
If the computers are on different networks, port forwarding is required.

## Authors

- **Arturo Benedetti**
    - GitHub: [benedart](https://github.com/benedart)
- **If Antonov**
    - GitHub: [iantonov99](https://github.com/iantonov99)
- **Sibilla Silbano**
    - GitHub: [allibiss](https://github.com/allibiss)
