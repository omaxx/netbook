import argparse

import yaml

from netbook.db import Folder, Device
from netbook.db.errors import AlreadyExist

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inventory")


def import_inventory(file: str):
    with open(file) as io:
        inventory = yaml.safe_load(io)

        for folder in inventory.get("folders", []):
            parent = Folder.get(folder.pop("folder", None))
            try:
                parent.create_folder(**folder)
            except AlreadyExist:
                pass

        for device in inventory.get("devices", []):
            parent = Folder.get(device.pop("folder", None))
            try:
                parent.create_device(**device)
            except AlreadyExist:
                pass

        for group in inventory.get("groups", []):
            parent = Folder.get(group.pop("folder", None))
            try:
                devices = group.pop("devices", [])
                group = parent.create_group(**group)
                for device in devices:
                    group.add_device(Device.get(device))
            except AlreadyExist:
                pass


def main(args):
    if args.inventory:
        import_inventory(args.inventory)
    else:
        import_inventory("inventory/demo.yaml")
        import_inventory("inventory/vlab.yaml")


if __name__ == "__main__":
    exit(main(parser.parse_args()))
