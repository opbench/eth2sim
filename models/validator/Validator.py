from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple, Dict

from eth2spec.phase0.spec import(
    Slot, Epoch, CommitteeIndex, ValidatorIndex, Root,
    BeaconState, Attestation, SignedBeaconBlock,
    MAX_VALIDATORS_PER_COMMITTEE, SYNC_COMMITTEE_SIZE, 
    VALIDATOR_REGISTRY_LIMIT,
    on_tick, get_current_slot
)


from eth2spec.utils.ssz.ssz_typing import List, uint64

from eth2spec.test.helpers.keys import pubkeys, pubkey_to_privkey

frequency = 1


class Duty(object):
    """
    A data store class for recording duty of validator at a specific slot
        
    Attributes:
        time: Simulation time in milliseconds.
        slot: Slot index when performing duty.
        duty_type: Type of duty (p: propose, a: attest, s: sync committee).
    """
    time_ms: uint64
    slot: Slot
    duty_type: str
        
    def __init__(self, time, slot, duty_type):
        self.time = time
        self.slot = slot
        self.duty_type = duty_type


class ValidatorData:
    """
    A data store class for representing states of validator
        
    Attributes:
        slot: Current ongoing slot.
        time_ms: Current simulation time in milliseconds.
        head_root: Current head root, returned by `get_head` on validator's `Store`
        current_epoch: Current epoch
        current_attest_slot: Lastest slot to attest in the current epoch
        current_committee_index: Lastest committee index to attest in the current epoch
        current_committee: 
        next_attest_slot: Last computed slot to attest in the next epoch
        next_committee_index: Last computed committee index to attest in the next epoch
        next_committee: List[ValidatorIndex, MAX_VALIDATORS_PER_COMMITTEE]
        current_sync_committee: 

        is_received_block: Indicate whether the block is received from the proposer
    """

    slot: Slot
    time_ms: uint64
    head_root: Root
    current_epoch: Epoch
    current_attest_slot: Slot
    current_committee_index: CommitteeIndex
    current_committee: List[ValidatorIndex, MAX_VALIDATORS_PER_COMMITTEE]
    next_attest_slot: Slot
    next_committee_index: CommitteeIndex
    next_committee: List[ValidatorIndex, MAX_VALIDATORS_PER_COMMITTEE]
    current_sync_committee: List[List[uint64, 2], SYNC_COMMITTEE_SIZE]
    last_slot_attested: Optional[Slot]
    last_slot_sync_committee: Optional[Slot]
    current_proposer_duties: Sequence[bool]
    last_slot_proposed: Optional[Slot]
    recorded_attestations: List[Root, 2048]
    is_received_block: bool


class Validator:
    """
    A class for representing a validator
        
    Attributes:
        validator_index: Unique index number of validator
        pub_key: Validator public key
        priv_key: Validator private key
        state_store: Static cache for expensive operations.
        `state_store` stores a map from `(current_state_hash, to_slot)` calling
        `process_slots(current_state, to_slot)`.
    """

    validator_index: ValidatorIndex
    pub_key: int
    priv_key: int
    state_store: Dict[Tuple[Root, Slot], BeaconState] = {}


    def __init__(self, validator_index:ValidatorIndex = 0):
        """
        Validator constructor
        The validator is initialised from some base state, and given a `validator_index`
        """

        self.validator_index = validator_index
        self.pub_key = pubkeys[validator_index]
        self.priv_key = pubkey_to_privkey[self.pubkey]
        self.duty_history = List[Duty, VALIDATOR_REGISTRY_LIMIT]
        self.data = ValidatorData()


    def log_attestation(self, item:Attestation) -> None:
        """
        Recording validator's attestation duty in local history
        """
        
        self.duty_history.append(Duty(
            time=self.data.time_ms,
            slot=item.data.slot,
            move="a"
        ))

        self.update_attest_move()

    def log_propose(self, item:SignedBeaconBlock) -> None:
        """
        Recording validator's propose duty in local history
        """
        
        self.duty_history.append(Duty(
            time=self.data.time_ms,
            slot=item.message.slot,
            move="p"
        ))

        self.update_propose_move()

    def update_attest_move(self):
        """
        When was the last attestation?
        """
        slots_attested = sorted([history.slot for history in self.duty_history if history.move == "a"], reverse=True)
        self.data.last_slot_attested = None if len(slots_attested) == 0 else slots_attested[0]

        
    def update_propose_move(self):
        """
        When was the last block proposal?
        """
        slots_proposed = sorted([log.slot for log in self.history if log.move == "p"], reverse=True)
        self.data.last_slot_proposed = None if len(slots_proposed) == 0 else slots_proposed[0]


    def attest(self):
        """
        Returns an honest attestation from `validator`.

        Args:
            

        Returns:
            Attestation: The attestation
        """
        pass


    def propose(self):
        """
        Returns a block using the current LMD-GHOST head and all known attestations aggregated.
        Args:

        Returns:
            Block: The new candidate block
        """
        pass

    def update_time(self, frequency:uint64 = frequency) -> None:
        """
        Update validators' clocks by one frequency.

        Args:
            frequency: Simulation update rate

        Returns:
            None
        """

        self.data.time_ms += int(1000 / frequency)

        if self.data.time_ms % 1000 == 0:
            # The store is updated each second in the specs
            on_tick(self.store, self.store.time + 1)

            # If a new slot starts, update
            if get_current_slot(self.store) != self.data.slot:
                self.update_data()

    def update_data(self) -> None:
        pass