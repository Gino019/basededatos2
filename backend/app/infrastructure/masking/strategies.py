import hashlib
from typing import Any
from faker import Faker

from app.domain.interfaces.masking_strategy import MaskingStrategy


class SubstitutionStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        provider = options.get("provider", "name")
        seed_value = f"{provider}:{value}"
        numeric_seed = int(hashlib.sha256(seed_value.encode("utf-8")).hexdigest(), 16) % (2**32)
        faker = Faker()
        faker.seed_instance(numeric_seed)
        try:
            fake_func = getattr(faker, provider)
            return fake_func()
        except AttributeError:
            return faker.word()


class HashingStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        salt = options.get("salt", "")
        payload = f"{value}{salt}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


class RedactionStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        mask_char = options.get("mask_char", "*")
        return mask_char * len(str(value))


class NullificationStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        return None
