# How to Setup

To set up the project, please follow the steps below:

## Step 1: Create `.env` File

Create a file named `.env` and set the following variables inside it:

```
TELEGRAM_NOTIFICATION=True
TELEGRAM_BOT_TOKEN=your_token
```

## Step 2: Edit `config.py`

In the `config.py` file, modify the `run_data` dictionary according to your requirements. You can add, edit, or remove any exchanges as needed.

## Step 3: Install Dependencies

Install all the project dependencies by running the following command:

```
pip install -r requirements.txt
```

## Step 4: Run the Server

Start the server by running the following command:

```
python main.py
```

This will initiate the server and make it ready to process requests.

## Step 5: Create a New Strategy

To create a new strategy, utilize the base class provided in the `strategies` folder. You can create your own strategy by extending this base class and implementing the necessary methods. Refer to the `SampleStrategy.py` file for a reference implementation.

Note: Whenever the bot enters or exits a trade, you will receive a notification on Telegram.

Contributions to the project are highly appreciated. Feel free to contribute and improve the codebase.

Thank you for using this project!
