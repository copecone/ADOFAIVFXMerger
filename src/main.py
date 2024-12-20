import os
import shutil
import sys
import time
import json
import hashlib

import requests
from program_util.constants import API_RESPONSE_CODE_MSG as API_MSG
from program_util.directory_util import check_dir

tagSpecifics = ["AddDecoration", "MoveDecorations"]

def main(args: list[str]) -> None:
    target = args[-1]
    files = args[:-1]

    check_dir(target)

    new_level = {"actions": [], "decorations": []}
    for index, path in enumerate(files):
        print(f"Processing {path}...")
        file_dir = os.path.dirname(path)

        with open(path, "r", encoding='utf-8') as f:
            content = f.read()

            start = time.time()
            response = requests.post("https://api.aef.kr/v1/util/fix_json", content)
            end = time.time()

            print(API_MSG.get(response.status_code, API_MSG["default"]), end="")
            if response.status_code != 200:
                print(); return

            print(" (took {:.3f}ms)".format((end - start) * 1000))

        data = json.loads(response.text[1:])
        if index == 0: # Initial Setting
            new_level["angleData"] = data["angleData"]
            new_level["settings"] = data["settings"]
            song_file_name = data["settings"]["songFilename"]
            shutil.copy(os.path.join(file_dir, song_file_name), os.path.join(target, song_file_name))

        hash_code = hashlib.sha3_512(path.encode('utf-8')).hexdigest()
        tag_prefix = hash_code + "_"

        asset_dir = os.path.join(target, hash_code)
        print(asset_dir)
        check_dir(asset_dir)

        deco_set = set()
        deco_ignore = [""]
        for action in data["actions"]:
            new_action = action

            if "tag" in new_action:
                new_action["tag"] = " ".join(map(lambda s: tag_prefix + s, new_action["tag"].split(" ")))
            if "eventTag" in new_action:
                new_action["eventTag"] = " ".join(map(lambda s: tag_prefix + s, new_action["eventTag"].split(" ")))

            if "decorationImage" in new_action:
                if new_action["decorationImage"] not in deco_ignore:
                    deco_set.add(new_action["decorationImage"])
                    new_action["decorationImage"] = os.path.join(hash_code, new_action["decorationImage"])

            new_level["actions"].append(new_action)

        for decoration in data["decorations"]:
            new_decoration = decoration

            if "tag" in new_decoration:
                new_decoration["tag"] = " ".join(map(lambda s: tag_prefix + s, new_decoration["tag"].split(" ")))

            if "decorationImage" in new_decoration:
                if new_decoration["decorationImage"] not in deco_ignore:
                    deco_set.add(new_decoration["decorationImage"])
                    new_decoration["decorationImage"] = os.path.join(hash_code, new_decoration["decorationImage"])

            new_level["decorations"].append(new_decoration)

        for deco in deco_set:
            deco_dir = os.path.dirname(deco)
            final_dir = os.path.join(asset_dir, deco_dir)
            if deco_dir != "":
                check_dir(final_dir)

            shutil.copy(os.path.join(file_dir, deco), os.path.join(asset_dir, deco))

    with open(os.path.join(target, "level.adofai"), "w", encoding = "utf-8") as f:
        f.write(json.dumps(new_level))

    return

if __name__ == '__main__':
    main(sys.argv[1:])