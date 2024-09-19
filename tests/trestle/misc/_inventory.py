# test.py
from uuid import uuid4

from trestle.oscal.common import InventoryItem, ResponsibleParty

try:
    role_id = 'x'
    party_uuids = [str(uuid4())]
    rp = ResponsibleParty(
        role_id=role_id,
        party_uuids=party_uuids,
    )
    list_rp = [rp]
    item = InventoryItem(
        uuid=str(uuid4()),
        description='an item',
        props=[],
        links=[],
        responsible_parties=list_rp,
        implemented_components=[],
    )
except Exception as e:
    raise RuntimeError(f'{e}')
