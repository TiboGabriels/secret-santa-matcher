import os
import json
import smtplib
import random

from dotenv import load_dotenv


def main():
    load_dotenv()
    live_mode = os.getenv("LIVE_MODE")
    email_from = os.getenv("EMAIL_FROM")
    people_json_file = os.getenv("PEOPLE_JSON_FILE")

    print("Loading people from {}".format(people_json_file))
    try:
        with open(people_json_file) as f:
            people = json.load(f)
            f.close()
    except Exception as e:
        print("Error loading people from {}: {}".format(people_json_file, e))

    matched_people = match_people(people)

    if live_mode:
        print("Running in live mode")

    else:
        print("Running in test mode")
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT"))
        smtp_user = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            send_emails(matched_people, server, email_from)


def match_people(groups):
    matched_people = []
    for group in groups:
        eligible_people = []
        for other_group in groups:
            if other_group["name"] != group["name"]:
                for other_person in other_group:
                    eligible_people.append(other_person)
        for person in group:
            recipient = eligible_people.pop(random.randint(0, len(eligible_people) - 1))
            matched_people.append({"giver": person, "recipient": recipient})
    return matched_people


def send_emails(matched_people, server, email_from):
    for person in matched_people:
        print("Sending email to {}".format(person["email"]))
        server.sendmail(email_from, person["email"], "Hello {}".format(person["name"]))
