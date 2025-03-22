import argparse
import logging
import csv
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SKIP_FIELDS = [
    "name",
    "revisionDate",
    "creationDate",
    "deletedDate",
    "id",
    "organizationId",
    "folderId",
    "type",
    "favorite",
    "reprompt",
    "login",
    "collectionIds",
    "passwordHistory"
]


def json_object_to_markdown(json_object: dict, markdown: str = None, level: int = 1):
    if markdown is None:
        markdown = ""
    for key, value in json_object.items():
        if key in SKIP_FIELDS:
            continue
        if isinstance(value, dict):
            markdown += f"{'#' * level} {key}\n"
            markdown = json_object_to_markdown(value, markdown, level + 1)
        elif isinstance(value, list):
            markdown += f"{'#' * level} {key}\n"
            for item in value:
                markdown = json_object_to_markdown(item, markdown, level + 1)
        elif value is not None:
            markdown += f"{key}: {value}\n"

    return markdown


def format_otpauth(value):
    if value is None:
        return ""
    elif value.startswith('otpauth'):
        return value
    else:
        return f"otpauth://totp/?secret={value}&algorithm=SHA1&digits=6&period=30"


def main():
    parser = argparse.ArgumentParser(
        description="This is a simple program that convert bitwarden json file to Apple Passwords CSV file.")
    parser.add_argument("--input", help="The input bitwarden json file path", required=True)
    parser.add_argument("--output", help="The output Apple Passwords CSV file path", required=True)

    args = parser.parse_args()
    fieldnames = ['Title', 'Notes', 'Username', 'Password', 'OTPAuth', 'URL']

    with open(args.input, "r") as input_file, open(args.output, "w") as output:
        data = json.load(input_file)
        if 'items' not in data:
            logger.error("The input file is not a valid bitwarden json file.")
            return

        if "encrypted" in data and data["encrypted"]:
            logger.error("The input file is encrypted. Please decrypt it first.")
            return

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for item in data['items']:
            notes = json_object_to_markdown(item)
            writer.writerow({
                'Title': item['name'],
                'Notes': notes,
                'Username': item['login']['username'] if "login" in item else None,
                'Password': item['login']['password'] if "login" in item else None,
                'OTPAuth': format_otpauth(item['login']['totp']) if "login" in item else None,
                'URL': ", ".join([row["uri"] for row in item["login"]["uris"]]) if "login" in item and "uris" in item[
                    "login"] else None
            })


if __name__ == "__main__":
    main()
