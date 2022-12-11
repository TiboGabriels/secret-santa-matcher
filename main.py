import os
import json
import smtplib
import random
import csv
from dotenv import load_dotenv


def main():
    load_dotenv()
    live_mode = os.getenv("LIVE_MODE", False)
    email_from = os.getenv("EMAIL_FROM")
    name_from = os.getenv("NAME_FROM")
    people_json_file = os.getenv("PEOPLE_JSON_FILE")
    export_csv = os.getenv("EXPORT_CSV")
    export_csv_file = os.getenv("EXPORT_CSV_FILE")

    print("Loading people from {}".format(people_json_file))
    with open(people_json_file) as f:
        people = json.load(f)
        f.close()

    matched_people = match_people(people)

    if export_csv == "True":
        print("Exporting matches to {}".format(export_csv_file))
        with open("output/{}".format(export_csv_file), "w") as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'email', 'recipient'])
            writer.writeheader()
            writer.writerows(matched_people)
            f.close()

    if live_mode == 'True':
        print("Running in live mode")

        smtp_server = os.getenv("LIVE_SMTP_SERVER")
        smtp_port = int(os.getenv("LIVE_SMTP_PORT"))
        smtp_user = os.getenv("LIVE_SMTP_USERNAME")
        smtp_password = os.getenv("LIVE_SMTP_PASSWORD")
        print("Connecting to SMTP server {}:{} as {}".format(smtp_server, smtp_port, smtp_user))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.ehlo(name="secret_santa")
            server.login(smtp_user, smtp_password)
            send_emails(matched_people, server, email_from, name_from)

    else:
        print("Running in test mode")

        print("Matched people: {}".format(matched_people))

        smtp_server = os.getenv("TEST_SMTP_SERVER")
        smtp_port = int(os.getenv("TEST_SMTP_PORT"))
        smtp_user = os.getenv("TEST_SMTP_USERNAME")
        smtp_password = os.getenv("TEST_SMTP_PASSWORD")
        print("Connecting to SMTP server {}:{} as {}".format(smtp_server, smtp_port, smtp_user))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            send_emails(matched_people, server, email_from, name_from)


def match_people(groups):
    matched_people = []
    for group in groups:
        eligible_people = []
        for other_group in groups:
            if other_group["name"] != group["name"]:
                for other_person in other_group["members"]:
                    if not any(other_person.get("name") == match.get("recipient")
                               for match in matched_people):
                        eligible_people.append(other_person)
        for person in group["members"]:
            recipient = eligible_people.pop(random.randint(0, len(eligible_people) - 1))
            matched_people.append(person | {"recipient": recipient["name"]})
    return matched_people


def send_emails(matched_people, server, email_from, name_from):
    count = 0
    for match in matched_people:
        print("Sending email to {}".format(match["email"]))
        subject = "Secret Santa"
        from_email = "{} <{}>".format(name_from, email_from)
        to_email = "{} <{}>".format(match["name"], match["email"])
        text = """
Gelukkige feestdagen, {}
Jij mag een cadeautje geven aan {}. Veel plezier!
            """.format(match["name"], match["recipient"])
        message = 'Subject: {}\n\n{}'.format(subject, text)
        server.sendmail(from_email, to_email, message)
        count += 1
    print("Sent {} emails".format(count))


if __name__ == "__main__":
    main()
