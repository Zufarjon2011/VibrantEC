import users_list


class IELTSGroup:
    students = []
    for attr_name in dir(users_list):
        attr = getattr(users_list, attr_name)
        if isinstance(attr, type) and hasattr(attr, 'grs') and "English" in attr.grs:
            # Присваиваем новый статус в зависимости от курса
            if "Intermediate" in attr.grs:
                status = "Intermediate Student"
            elif "IELTS 2025" in attr.grs:
                status = "IELTS Student"
            else:
                status = "Student🧑‍🎓"

            # Добавляем пользователя с обновленным статусом, логином и паролем
            students.append(f"{attr.realname} — {status}\n"
                            f"Login and password: {attr.Password}\n\n")


class MathGroup:
    teachers = []
    for attr_name in dir(users_list):
        attr = getattr(users_list, attr_name)
        if isinstance(attr, type) and hasattr(attr, 'grs') and "Math" in attr.grs:
            teachers.append(f"{attr.realname} — {attr.status}\n"
                            f"Login and password: {attr.Password}\n\n")
