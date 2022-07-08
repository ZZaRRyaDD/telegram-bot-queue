import os
import random

from database import UserActions


def check_admin(id) -> bool:
    """Check for admin user."""
    return id == int(os.getenv("ADMIN_ID"))


def check_user(id: int) -> bool:
    """Check register user or not."""
    return UserActions.get_user(id) is not None


def is_headman(id: int) -> bool:
    """Is user headman?"""
    return UserActions.get_user(id).is_headman


def check_empty_headman(id: int) -> bool:
    """Check for empty headman."""
    user = UserActions.get_user(id)
    return is_headman(id) and user.group is None


def check_headman_of_group(id: int) -> bool:
    """Check headman how owner of group."""
    user = UserActions.get_user(id)
    return is_headman(id) and user.group is not None


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
