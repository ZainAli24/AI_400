import time
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def send_email_task(email: str, message: str):
    """Simulate sending an email"""
    logger.info(f"Sending email to {email}")
    time.sleep(2)  # Simulate email sending
    logger.info(f"Email sent to {email}")
    return {"status": "sent", "email": email}


def process_data_task(data: Dict):
    """Simulate data processing"""
    logger.info(f"Processing data: {data}")
    time.sleep(3)  # Simulate processing
    logger.info("Data processing complete")
    return {"status": "processed", "data": data}


def generate_report_task(report_id: int):
    """Simulate report generation"""
    logger.info(f"Generating report {report_id}")
    time.sleep(5)  # Simulate report generation
    logger.info(f"Report {report_id} generated")
    return {"status": "completed", "report_id": report_id}
