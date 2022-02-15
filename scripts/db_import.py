import argparse

import yaml

import netbook
from netbook import db

netbook.init()
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inventory")


def import_inventory(file: str):
    with open(file) as io:
        inventory = yaml.safe_load(io)

        for folder in inventory.get("folders", []):
            parent = db.Folder.get(folder.pop("folder", None))
            try:
                parent.create_folder(**folder)
            except db.errors.AlreadyExist:
                pass

        for device in inventory.get("devices", []):
            parent = db.Folder.get(device.pop("folder", None))
            try:
                device = parent.create_device(**device)
                device.set_fact(name="system", value={
                    "hostname": device.name,
                    "hw": {
                        "model": "junos/vmx",
                    }
                })
            except db.errors.AlreadyExist:
                pass

        for group in inventory.get("groups", []):
            parent = db.Folder.get(group.pop("folder", None))
            try:
                devices = group.pop("devices", [])
                group = parent.create_group(**group)
                for device in devices:
                    group.add_device(db.Device.get(device))
            except db.errors.AlreadyExist:
                pass


def create_users():
    for user in ["admin", "guest"]:
        db.User.create(name=user, password=user)


def main(args) -> int:
    if args.inventory:
        import_inventory(args.inventory)
    else:
        import_inventory("inventory/demo.yaml")
        import_inventory("inventory/vlab.yaml")

    create_users()

    return 0


if __name__ == "__main__":
    exit(main(parser.parse_args()))
