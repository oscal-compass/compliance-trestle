import atheris
import sys
import json
import io
from pydantic import ValidationError


with atheris.instrument_imports():
    from trestle.oscal.catalog import Catalog
    from trestle.common.err import TrestleError


catalogg = {
    "catalog": {
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "metadata": {
            "title": "Fuzz Seed Catalog",
            "last-modified": "2026-02-10T14:58:41Z",
            "version": "1.0.0",
            "oscal-version": "1.1.3"
        },
        "groups": [
            {
                "id": "grp-1",
                "title": "Baseline Group",
                "controls": [
                    {
                        "id": "ac-1",
                        "title": "Access Control 1"
                    }
                ]
            }
        ]
    }
}
seed = json.dumps(catalogg).encode("utf-8")

def mut(data, fdp):
    """Deeply walks the JSON structure to mutate values while preserving keys."""
    if isinstance(data, dict):
        for key in list(data.keys()):
            
            if fdp.ConsumeBool():
                data[key] = mut(data[key], fdp)
        return data
    
    elif isinstance(data, list):
        if len(data) > 0:
            
            idx = fdp.ConsumeIntInRange(0, len(data) - 1)
            data[idx] = mut(data[idx], fdp)
        return data
    
    elif isinstance(data, str):
        try:
            mutated_bytes = atheris.Mutate(data.encode('utf-8'), len(data) + 64)
            return mutated_bytes.decode('utf-8', errors='ignore')
        except Exception:
            return data
            
    elif isinstance(data, (int, float)):
        
        return data + fdp.ConsumeIntInRange(-100, 100)
    
    return data

def CustomMutator(data, max_size, seed):
    """Structure-aware entry point for Atheris."""
    try:
      
        js = json.loads(data)
        fdp = atheris.FuzzedDataProvider(data)
        
        
        mutated_obj = mut(js, fdp)
        
       
        return json.dumps(mutated_obj).encode('utf-8')
    except Exception:
        return atheris.Mutate(data, max_size)

def TestOneInput(data):
    """The entry point called by the fuzzer."""
    
    if not data:
        return

    try:

        obj = Catalog.parse_raw(data)


        exported = obj.json(by_alias=True, exclude_none=True)
        obj2 = Catalog.parse_raw(exported)

        if obj != obj2:
            
            raise RuntimeError("Idempotency violation detected")

    except (ValidationError, json.JSONDecodeError, UnicodeDecodeError, ValueError):

        return 
    except (TrestleError, RecursionError, AttributeError) as e:
        print(f"CRASH DETECTED: {type(e).__name__}: {e}")
        raise e
    
def main():
    atheris.Setup(
        sys.argv, 
        TestOneInput, 
        custom_mutator=CustomMutator,
        initial_inputs=[seed]
    )
    atheris.Fuzz()

if __name__ == "__main__":
    main()