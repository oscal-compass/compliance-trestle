import os
from pathlib import Path
from trestle.core.base_model import OscalBaseModel
from trestle.core.models.file_content_type import FileContentType
from trestle.core import utils
from trestle.utils import fs


def load_list(filepath):
    aliases_not_to_be_stripped = []
    instances_to_be_merged: List[OscalBaseModel] = []
    # TODO: FIXME: fs.get_stripped_contextual_model fails without absolute file path!!! FIX IT!!
    collection_model_type, collection_model_alias = fs.get_stripped_contextual_model(filepath.absolute())
    
    for path in Path.iterdir(filepath):

        # ASSUMPTION HERE: if it is a directory, there's a file that can not be decomposed further.
        if path.is_dir():
            continue
        model_type, model_alias, model_instance = load_distributed(path)

        instances_to_be_merged.append(model_instance)
        aliases_not_to_be_stripped.append(model_alias.split('.')[-1])

    return collection_model_type, collection_model_alias, instances_to_be_merged


def load_dict(filepath):
    model_dict = {}
    collection_model_type, collection_model_alias = fs.get_stripped_contextual_model(filepath.absolute())
    for path in Path.iterdir(filepath):
        #model_type, model_alias = fs.get_stripped_contextual_model(path.absolute())
        #model_instance = model_type.oscal_read(path)
        model_type, model_alias, model_instance = load_distributed(path)
        field_name = path.parts[-1].split('__')[0]
        model_dict[field_name] = model_instance

    return collection_model_type, collection_model_alias, model_dict

def load_distributed(file_path: Path, collection_type = None):

    # If the path contains a list type model
    if collection_type is list:
        return load_list(file_path) 

    # If the path contains a dict type model
    if collection_type is dict:
        return load_dict(file_path)

    # Get current model
    primary_model_type, primary_model_alias = fs.get_stripped_contextual_model(file_path.absolute())
    primary_model_instance = primary_model_type.oscal_read(file_path)
    primary_model_dict = primary_model_instance.__dict__
    
    # Is model decomposed?
    file_dir = file_path.parent
    decomposed_dir = file_dir / file_path.parts[-1].split(".")[0]

    if decomposed_dir.exists():
        aliases_not_to_be_stripped = []
        instances_to_be_merged: List[OscalBaseModel] = []

        for path in Path.iterdir(decomposed_dir):
            
            if path.is_file():
                model_type, model_alias, model_instance = load_distributed(path)
                aliases_not_to_be_stripped.append(model_alias.split('.')[-1])
                instances_to_be_merged.append(model_instance)

            elif path.is_dir():
                model_type, model_alias = fs.get_stripped_contextual_model(path.absolute())
                # Only load the directory if it is a collection model. Otherwise do nothing - it gets loaded when iterating
                # over the model file
                if '__root__' in model_type.__fields__.keys() and utils.is_collection_field_type(model_type.__fields__['__root__'].outer_type_):
                    # TODO: This directory is a decomposed List or Dict
                    collection_type = model_type.__fields__['__root__'].outer_type_.__origin__
                    model_type, model_alias, model_instance = load_distributed(path, collection_type)
                    aliases_not_to_be_stripped.append(model_alias.split('.')[-1])
                    instances_to_be_merged.append(model_instance)
    
        for i in range(len(aliases_not_to_be_stripped)):
            alias = aliases_not_to_be_stripped[i]
            instance = instances_to_be_merged[i]
            if hasattr(instance, "__dict__") and "__root__" in instance.__dict__:
                instance = instance.__dict__["__root__"]
            primary_model_dict[alias] = instance

        merged_model_type, merged_model_alias = fs.get_stripped_contextual_model(file_path.absolute(), aliases_not_to_be_stripped)
        merged_model_instance = merged_model_type(**primary_model_dict)
        return merged_model_type, merged_model_alias, merged_model_instance

    else:
        return primary_model_type, primary_model_alias, primary_model_instance
