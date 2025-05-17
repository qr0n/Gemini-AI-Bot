import os
import json


def find_config(version):
    """
    Locates and copies the config file for the given version.
    Prevents publishing sensitive keys by working with temp configs.
    """
    print(f"Locating config for {version}...")

    try:
        with open(f"./helper-assets/{version}", "r") as config_file:
            with open("temp_config.json", "w") as copy:
                copy.write(config_file.read())
        return customize_config(version)
    except FileNotFoundError:
        print(f"❌ Config for {version} not found.")
        return -1


def prompt_dict(data: dict, prefix="") -> dict:
    """
    Recursively prompt user to customize values in a nested dictionary.
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"\n🔽 Entering config for: {prefix + key}")
            result[key] = prompt_dict(value, prefix=prefix + key + ".")
        else:
            user_input = input(f"{prefix + key} [{value}]: ") or value
            result[key] = user_input
    return result


def customize_config(version):
    with open(f"./helper-assets/{version}", "r") as config_version:
        config_dict = json.load(config_version)

    print(
        "\n➡️  Customize your config:\n"
        " - Press [Enter] to accept default.\n"
        " - Or type your new value and press [Enter] to override.\n"
    )

    config_dict = prompt_dict(config_dict)

    os.makedirs(f"./stable/{version}", exist_ok=True)
    with open(f"./stable/{version}/config.json", "w") as dump:
        json.dump(config_dict, dump, indent=4)

    print("✅ Config saved.")
    return True


def main():
    while True:
        print("🔧 Nugget Tech Config Builder")
        versions = [v for v in os.listdir("./stable") if os.path.isdir(f"./stable/{v}")]
        version = input(
            f"Enter the version of Nugget you're using (or type 'exit' to quit):\n{chr(10).join(versions)}\n> "
        )
        if version.lower() == "exit":
            break
        if find_config(version=version) == -1:
            continue
        else:
            break


if __name__ == "__main__":
    main()
