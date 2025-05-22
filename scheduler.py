import logging
from logging.handlers import RotatingFileHandler
import schedule
import time
import subprocess
import sys

# Configure logging with rotation
log_handler = RotatingFileHandler(
    './logs/scheduler.log',
    maxBytes=1024 * 1024,  # 1 MB per file
    backupCount=5  # Keep 5 backup files
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        log_handler,
        logging.StreamHandler(sys.stdout)
    ]
)

def run_script(script_name):
    try:
        logging.info(f"Starting {script_name}")
        result = subprocess.run([sys.executable, script_name], check=True)
        if result.returncode == 0:
            logging.info(f"{script_name} completed successfully")
            return True
        else:
            logging.error(f"{script_name} failed with return code {result.returncode}")
            return False
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running {script_name}: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error running {script_name}: {str(e)}")
        return False

def daily_task():
    logging.info("Starting daily task")
    
    # Run channel_content.py first
    if run_script('channel_content.py'):
        # Only run teleflash.py if channel_content.py was successful
        run_script('teleflash.py')
    else:
        logging.error("Skipping teleflash.py due to channel_content.py failure")

# Schedule the task to run at 9 AM every day
schedule.every().day.at("06:00").do(daily_task)

logging.info("Scheduler started. Will run scripts daily at 06:00")

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(60)