# Lizz-Bitcoin-Compatible-Conditional-and-Flexible-Multi-Party-Payment-Channel

Lizz is a Bitcoin-compatible multi-party conditional payment channel. It is designed to rely on digital signatures and time locks in order to minimize the requirements for blockchain system scripting functionality. A semi-trusted board of users coordinates user payments and verifies that payment conditions are met.

## Prerequisites

1. **Install Bitcoin Core 0.20.1**:
   - Download Bitcoin Core 0.20.1 from the official [Bitcoin Core website](https://bitcoin.org/en/bitcoin-core/).
   - Install Bitcoin Core by following the instructions provided on the website.

2. **Set Up `bitcoin.conf`**:
   - Configure the `bitcoin.conf` file with the necessary parameters for `regtest` mode. Refer to the provided `bitcoin.conf` file in this repository for the required settings.

## Installation and Setup

1. **Install Bitcoin Core**:
   - Install Bitcoin Core 0.20.1 by following the installation instructions on the official website.

2. **Configure Environment Variables**:
   - Add the path to the Bitcoin Core binaries to your system's environment variables.
     ```
     \path\to\bitcoin-0.20.1\bin
     ```

3. **Run Bitcoin Core**:
   - Open a command line window and run the following command to start Bitcoin Core in `regtest` mode:
     ```bash
     bitcoind -regtest -datadir=\path\to\BitcoinNet -conf=\path\to\bitcoin.conf
     ```

4. **Generate Accounts and UTXOs**:
   - Run `user_gen.py` to generate the required number of users and UTXOs:
     ```bash
     python user_gen.py
     ```

5. **Open and Update Channels**:
   - Run `main_join.py` to open the payment channels and perform channel updates:
     ```bash
     python main_join.py
     ```

## Running `main_join.py`

The `main_join.py` script has been updated to include two main functions: `join_test` and `main`. The `main` function is used to run the system and update the channels, while the `join_test` function is used to test the impact of user joins on the system.

### Main Function
The `main` function is called within a loop for different numbers of users to test the scalability and performance of the system. The parameters include the number of users, the number of committee members, and the committee threshold.

### Join Test Function
The `join_test` function is used to analyze the impact of adding new users to the system. This function can be uncommented and used as needed.

### Example Usage

The current setup of the `main_join.py` script will iterate over different user counts and execute the main system updates for each configuration.

```python
if __name__ == "__main__":
    # Uncomment the following lines to test the impact of user joins
    # with open("users_96.txt", "r") as f:
    #     user_list = json.load(f)
    # print(f"Testing user count: 6, committee count: 3, committee threshold: 2.")
    # join_test(user_list)

    user_counts = [6, 12, 24, 48, 96]
    committee_num = 3
    committee_threshold = 2
    for user_num in user_counts:
        print(f"Testing user count: {user_num}, committee count: {committee_num}, committee threshold: {committee_threshold}.")
        main(user_num, committee_num, committee_threshold)

## Files and Directories

- `bitcoin.conf`: Configuration file for Bitcoin Core in `regtest` mode.
- `user_gen.py`: Script to generate users and UTXOs.
- `main_join.py`: Main script to open payment channels, perform channel updates, and test the system.

## Troubleshooting

- Ensure Bitcoin Core is properly installed and the environment variables are correctly set.
- Verify that `bitcoind` is running in `regtest` mode with the correct `datadir` and `conf` file.
- Check the paths in the commands and ensure they match your installation directories.

For any issues or questions, please open an issue in this repository or refer to the Bitcoin Core documentation.
