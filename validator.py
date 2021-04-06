from pathlib import Path
import random
from typing import Optional, Tuple

from remerkleable.basic import uint64

from colors import COLORS
from eth2spec.phase0 import spec
from eth2spec.phase0.spec import BLSPubkey

from py_ecc.bls12_381 import curve_order
from py_ecc.bls import G2ProofOfPossession as Bls


class Validator:
    index: Optional[spec.ValidatorIndex]
    counter: int
    startbalance: uint64
    privkey: int
    pubkey: BLSPubkey

    colorstep: int

    def __init__(self, counter: int, startbalance: uint64, keydir: Optional[str]):
        self.index = None
        self.counter = counter
        self.startbalance = startbalance
        self.privkey, self.pubkey = self.__init_keys(counter, keydir)
        self.colorstep = 2

    def color(self, otheridx=None):
        if otheridx:
            idx = otheridx
        else:
            idx = self.index if self.index is not None else self.counter
        return COLORS[idx % len(COLORS)]

    def index_from_state(self, state: spec.BeaconState):
        self.index = spec.ValidatorIndex(max(
            genesis_validator[0]
            for genesis_validator in enumerate(state.validators)
            if genesis_validator[1].pubkey == self.pubkey
        ))

    @staticmethod
    def __init_keys(counter: int, keydir: Optional[str]) -> Tuple[int, BLSPubkey]:
        pubkey = None
        privkey = None
        pubkey_file = None
        privkey_file = None
        keys = None
        if keydir is not None:
            keys = Path(keydir)

        if keys is not None and keys.is_dir():
            pubkey_file = (keys / f'{counter}.pubkey')
            privkey_file = (keys / f'{counter}.privkey')
            if pubkey_file.is_file() and privkey_file.is_file():
                print(f'[VALIDATOR# {counter}] Read keys from file')
                pubkey = pubkey_file.read_bytes()
                privkey = int(privkey_file.read_text())
        if privkey is None or pubkey is None:
            print(f'[VALIDATOR# {counter}] Generate and save keys')
            privkey = random.randint(1, curve_order)
            pubkey = Bls.SkToPk(privkey)
            if keys is not None:
                assert isinstance(pubkey_file, Path)
                pubkey_file.write_bytes(pubkey)
                privkey_file.write_text(str(privkey))
        return privkey, pubkey