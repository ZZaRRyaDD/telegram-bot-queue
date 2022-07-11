import os
import random

from database import GroupActions, UserActions


def check_admin(id: int) -> bool:
    """Check for admin user."""
    return id == int(os.getenv("ADMIN_ID"))


def check_user(id: int) -> bool:
    """Check register user or not."""
    return UserActions.get_user(id) is not None


def is_headman(id: int) -> bool:
    """Is user headman?"""
    return UserActions.get_user(id).is_headman


def member_group(id: int) -> bool:
    """Check for member of some group."""
    return UserActions.get_user(id).group is not None


def check_empty_headman(id: int) -> bool:
    """Check for empty headman."""
    return is_headman(id) and not member_group(id)


def check_headman_of_group(id: int) -> bool:
    """Check headman how owner of group."""
    return is_headman(id) and member_group(id)


def check_count_subject_group(id: int) -> bool:
    """Check for count of subjects."""
    return bool(
        GroupActions.get_group_with_subjects(
            UserActions.get_user(id).group
        ).subjects
    )


def polynomial_hash(string: str) -> int:
    """Calculate polinomial hash."""
    second_prime_const = 2 ** 64 - 59
    first_prime_const = random.randint(0, second_prime_const)
    hash_code = 0
    for letter in enumerate(string):
        hash_code = (
            ord(letter[1]) *
            first_prime_const ** (len(string) - letter[0] - 1)
        )
    return hash_code % second_prime_const
