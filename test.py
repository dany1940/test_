import json
import logging
from enum import Enum
from functools import cached_property

from functools import lru_cache
from pydantic import ConfigDict
from pydantic import ValidationError
from pydantic import computed_field
from pydantic import field_validator
from pydantic.dataclasses import dataclass

VOWELS = {"a", "e", "i", "o", "u"}
FURTHER_DISCOUNT = 500

class FuelType(Enum):
    PETROL = "Petrol"
    DIESEL = "Diesel"
    ELECTRIC = "Electric"


@dataclass
class VehicleConfig:
    __pydantic_config__ = ConfigDict(use_enum_values=True, extra="forbid")
    code: str
    wheels: float
    chassis: int
    engine: int
    fuel: FuelType = FuelType.ELECTRIC
    cost: float | None = 0
    discount: float | None = 0



    @field_validator("code", mode="before")
    @classmethod
    @lru_cache(maxsize=None)
    def sanitise_cod(cls, code: str) -> str:
        code = code[::-1].lower()
        for character in code:
            if any(
                (
                    (character in VOWELS),
                    (not character.isalpha()),
                    (character.isspace()),
                )
            ):
                code = code.replace(character, "")

        return code

    @computed_field
    @cached_property
    def vehicle_cost(self) -> float:
        if self.fuel == "Electric":
            self.discount = (self.chassis + self.engine) * 0.15
            self.cost = self.chassis + self.engine - self.discount
        else:
            self.cost = self.wheels + self.chassis + self.engine
        return self.cost


def read_file(input_file: str) -> VehicleConfig | json.decoder.JSONDecodeError:
    with open(input_file, "r") as file:
        try:
            rows: VehicleConfig = json.load(file)
            return rows
        except json.decoder.JSONDecodeError as e:
            raise e


def execute():
    rows = read_file("test.json")
    total_cost: float = 0
    result = []
    for data in rows:
        try:
            VehicleConf = VehicleConfig(**data)
        except ValidationError as e:
            logging.exception(e.errors, data)
            raise e
        total_cost += VehicleConf.vehicle_cost
        result.append(VehicleConf)
    print(result)
    if total_cost % 2 == 0:
        total_cost = total_cost - FURTHER_DISCOUNT
    print(total_cost)  # could write the data back or add it to  a db
    return total_cost




if __name__ == "__main__":
    execute()
