import os
from pathlib import Path
from trestle.core.base_model import OscalBaseModel
from trestle.core.models.file_content_type import FileContentType
from trestle.core import utils
from trestle.utils import fs


def distributed_load(file_path: Path, collection_type = None):

    # If the path contains a list type or dict type model
    if collection_type is list or collection_type is dict:
        aliases_not_to_be_stripped = []
        instances_to_be_merged: List[OscalBaseModel] = []
        collection_model_type, collection_model_alias = fs.get_stripped_contextual_model(file_path.absolute())
        
        for path in Path.iterdir(file_path):
            model_type, model_alias = fs.get_stripped_contextual_model(path)
            model_instance = model_type.oscal_read(path)

            instances_to_be_merged.append(model_instance)
            aliases_not_to_be_stripped.append(model_alias.split('.')[-1])

        #collection_model_instance = collection_model_type.parse_obj(instances_to_be_merged)
        #return collection_model_type, collection_model_alias, collection_model_instance
        return collection_model_type, collection_model_alias, instances_to_be_merged


    # Get current model
    primary_model_type, primary_model_alias = fs.get_stripped_contextual_model(file_path.absolute())
    primary_model_instance = primary_model_type.oscal_read(file_path)
    primary_model_dict = primary_model_instance.__dict__
    
    # Is model decomposed?
    file_dir = file_path.parent
    decomposed_dir = file_dir / primary_model_alias.split('.')[-1]
    if decomposed_dir.exists():
        aliases_not_to_be_stripped = []
        instances_to_be_merged: List[OscalBaseModel] = []
        for path in Path.iterdir(decomposed_dir):
            # If a model is not decomposed, load that model
            if path.is_file():
                model_type, model_alias, model_instance = distributed_load(path)
                aliases_not_to_be_stripped.append(model_alias.split('.')[-1])
                instances_to_be_merged.append(model_instance)
            elif path.is_dir():
                model_type, model_alias = fs.get_stripped_contextual_model(path.absolute())
                if '__root__' in model_type.__fields__.keys() and utils.is_collection_field_type(model_type.__fields__['__root__'].outer_type_):
                    # TODO: This directory is a decomposed List or Dict
                    collection_type = model_type.__fields__['__root__'].outer_type_.__origin__
                    model_type, model_alias, model_instance = distributed_load(path, collection_type)
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


def distributed_load_old(file_path: Path):
    '''This assumes you are in the directory where the model exists. Loads everything in the directory into a model'''

    # Get model alias
    primary_model_type, primary_model_alias = fs.get_stripped_contextual_model(file_path.absolute())

    # Is model decomposed?
    file_dir = file_path.parent
    decomposed_dir = file_dir / primary_model_alias.split('.')[-1]
    if decomposed_dir.exists():
        # Model is decomposed
        # Make a list of split models
        # Recursively merge

        aliases_not_to_be_stripped = []
        instances_to_be_merged: List[OscalBaseModel] = []
        is_list = False
        is_dict = False
        for path in Path.iterdir(decomposed_dir):
            if path.is_file():
                model_type, model_alias = fs.get_stripped_contextual_model(path.absolute())
                model_instance = model_type.oscal_read(path)

                if hasattr(model_instance, '__root__') and (isinstance(model_instance.__root__, dict)
                                                            or isinstance(model_instance.__root__, list)):
                    model_instance = model_instance.__root__
                    is_list = isinstance(model_instance.__root__, list)
                    is_dict = isinstance(model_instance.__root__, dict)

                instances_to_be_merged.append(model_instance)
                aliases_not_to_be_stripped.append(model_alias.split('.')[-1])
            elif path.is_dir():
                distributed_load(path)
        
        if is_list:
            return instances_to_be_merged

        merged_dict = primary_model_type.oscal_read(file_path.absolute()).__dict__
        for i in range(len(aliases_not_to_be_stripped)):
            alias = aliases_not_to_be_stripped[i]
            instance = instances_to_be_merged[i]
            merged_dict[alias] = instance

        primary_model_type_with_decomposed_fields, _ = fs.get_stripped_contextual_model(
            file_path.absolute(), aliases_not_to_be_stripped)
        merged_model = primary_model_type_with_decomposed_fields(** merged_dict)
        return merged_model


def load_model_recursive(model):
    # 1. Model decomposed? Check for directory with model alias

    # 2. List aliases of models under the directory

    # 3. Load each decomposed model

    # 4. Load stripped model without stripping the aliases of the ones under decomposed directory

    # 5. Insert the decomposed models into the stripped model
    return NotImplementedError()