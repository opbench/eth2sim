from typing import List, Set, Optional, Sequence, Tuple, Dict
from dataclasses import dataclass, field

from eth2spec.phase0.spec import(
    VALIDATOR_REGISTRY_LIMIT,
    ValidatorIndex, Slot,
    BeaconState, Attestation, SignedBeaconBlock,
)

from models.validator.Validator import Validator

@dataclass
class Network:
    validators: List[Validator, VALIDATOR_REGISTRY_LIMIT]
    sync_committees: List[Validator, VALIDATOR_REGISTRY_LIMIT] = field(default_factory=list)