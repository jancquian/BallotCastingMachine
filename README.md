# 🗳️ Ballot Casting Machine (Cryptographic Voting System)

This project is a thesis developed for a Bachelor’s degree in Computer Systems Engineering, focused on the application of cryptography in electronic voting systems.
It implements a secure and privacy-preserving voting protocol using advanced cryptographic techniques, deployed on a Raspberry Pi 5 (8GB RAM) as a prototype voting machine.

# 🎓 Academic Background

This system was developed as a final thesis project in Computer Systems Engineering, with a focus on applied cryptography and secure system design.

The goal was to design and implement a functional prototype of a secure electronic voting system that ensures:

Voter privacy
Data integrity
Secure vote processing
End-to-end verifiability

# 🖥️ Hardware Implementation

The system was deployed and tested on:

🧠 Raspberry Pi 5 (8GB RAM)
Linux-based environment
Local execution of cryptographic protocols
Prototype voting terminal setup

This demonstrates the feasibility of implementing cryptographic voting systems on low-cost embedded hardware.

# 🔐 Cryptographic Techniques Used

The system integrates multiple advanced cryptographic primitives:

  🔑 ElGamal Homomorphic Encryption
    Allows vote aggregation without decrypting individual ballots
  🧩 Shamir’s Secret Sharing Scheme
    Distributes decryption authority among multiple parties
  ✍️ Blind Signatures
    Ensures voter authentication without revealing identity
  🔄 Re-encryption & Permutation
    Breaks the link between voters and their votes
    
# 🎯 System Objectives

Preserve voter anonymity and privacy
Prevent vote manipulation and duplication
Ensure secure and verifiable vote tallying
Implement a distributed trust model
Demonstrate cryptographic voting in an embedded system environment

# 🛠️ Technologies Used

Raspberry Pi 5 (8GB RAM)
Linux environment
Cryptographic algorithms: ElGamal, Shamir Secret Sharing, Blind Signatures
Programming language: Python 

# 👨‍💻 Author
Juan Carlos Garcia Jimenez
Cristofer Montes Lozada
