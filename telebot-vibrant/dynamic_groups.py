import users_list
import os

def generate_group_file(file_path="group_data.txt"):
    group_map = {}  # { "English IELTS 2025": [ "Name — Status\nLogin..." ] }

    for attr_name in dir(users_list):
        attr = getattr(users_list, attr_name)
        if isinstance(attr, type) and hasattr(attr, 'grs'):
            groups = [g.strip() for g in attr.grs.split(",")]
            for group in groups:
                if group not in group_map:
                    group_map[group] = []
                group_map[group].append(
                    f"{attr.realname}\nLogin and password: {attr.Password}\n"
                )

    with open(file_path, "w", encoding="utf-8") as f:
        for group, members in group_map.items():
            f.write(f"###{group}\n")
            for student in members:
                f.write(student + "\n---\n")
            f.write("###END\n")

def load_groups_from_file(file_path="group_data.txt"):
    if not os.path.exists(file_path):
        generate_group_file(file_path)

    group_map = {}
    current_group = None
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("###") and line != "###END":
                current_group = line[3:]
                group_map[current_group] = []
            elif line == "###END":
                current_group = None
            elif current_group and line != "---":
                group_map[current_group].append(line)
    return group_map
