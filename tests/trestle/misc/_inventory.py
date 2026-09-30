# test.py
from uuid import uuid4

from trestle.oscal.common import InventoryItem, ResponsibleParty

try:
    role_id = 'x'
    party_uuids = [str(uuid4())]
    # In Pydantic v2, use Field aliases with by_alias=True or use model_validate
    rp = ResponsibleParty.model_validate({'role-id': role_id, 'party-uuids': party_uuids})
    list_rp = [rp]
    item = InventoryItem.model_validate(
        {'uuid': str(uuid4()), 'description': 'an item', 'responsible-parties': list_rp}
    )
except Exception as e:
    raise RuntimeError(f'{e}')

# Made with Bob
