Experimental Pipeline: Cryptographic Evaluation of Password Manager
This pipeline is designed based on the ICT Course: Introduction to Cryptography slides (Sessions 4, 7, 8). It shifts the project from "app development" to "experimental analysis."

Stage 1: Block Cipher Mode Evaluation (Ref: Session 4)
Objective: Demonstrate why the choice of "Mode of Operation" matters for data confidentiality.

Scenario: Encrypt a vault containing multiple entries with similar usernames (e.g., "admin123", "admin456").
Experiment:
Implement a test script using AES-ECB (Electronic Code Book).
Implement a test script using AES-CBC (Cipher Block Chaining - current default).
Observation: Show that ECB produces identical ciphertext blocks for identical plaintext blocks, while CBC (with IV) does not.
Academic Value: Explains "Diffusion" and "Confusion" from the slides.
Stage 2: KDF Work Factor & UX Trade-off (Ref: Session 8)
Objective: Optimize the "Key Derivation" step for the Master Password.

Scenario: Measuring the time taken to unlock the vault.
Experiment:
Run PBKDF2-HMAC-SHA256 with $N \in {1,000, 10,000, 100,000, 400,000, 1,000,000}$ iterations.
Record T_derivation (msec).
Analysis: Plot a graph of Iterations vs. Time.
Academic Value: Discusses "Key Stretching" and the performance limits of CPU-bound hashes mentioned in Session 8.
Stage 3: Integrity Protection Analysis (Ref: Session 8 - MACs)
Objective: Evaluate how the system detects unauthorized file tampering.

Scenario: A "Man-in-the-disk" attacker modifies the encrypted vault file.
Experiment:
Open the .enc file in hex mode and change 1 byte of the ciphertext.
Attempt to decrypt using the correct Master Password.
Observation: Capture the InvalidToken / HMAC mismatch error.
Academic Value: Proves that "Encryption != Integrity". Explains why HMAC (Session 8) is required alongside AES (Session 4).
Stage 4: Salt Entropy & Vault Isolation (Ref: Session 7 - Hashing)
Objective: Demonstrate the risk of "Deterministic Salts."

Scenario: Two different vaults ("Work", "Personal") using the same Master Password.
Experiment:
Current implementation: Salt = Vault Name (Deterministic).
Proposed implementation: Salt = os.urandom(16) (Random).
Analysis: Show that if the salt is deterministic, the derived keys will be fixed for specific names, making rainbow tables easier to build for popular vault names.
5. Expected Output for the Report:
Table 1: Iteration Count vs. Unlock Time (ms).
Figure 1: Hex dump comparison of ECB vs CBC.
Screenshot: Error message when integrity check (HMAC) fails.
Conclusion: Quantitative recommendation for optimized security parameters.