import itertools
import numpy as np

class IdentityCategory():
    def __init__(self, category_name, identity_names, identity_keys, identity_class_names=None, identity_value_classes=None, all_surveys=None, reference_value=None, exclude_counts_lt=1):
        self.category_name = category_name
        self.identity_names = identity_names
        self.identity_keys = identity_keys
        if (not identity_class_names is None) and (not identity_value_classes is None):
            self.identity_class_names = identity_class_names
            self.identity_value_classes = identity_value_classes # num_classes x num_sets_of_values_per_class x num_identities
            self.reference_value = reference_value if not reference_value is None else identity_class_names[0]
        else:
            assert not all_surveys is None
            all_identity_values = self.get_identity_values(all_surveys)
            class_names, class_counts = np.unique(all_identity_values, return_counts=True)
            self.identity_class_names = class_names[class_counts>=exclude_counts_lt].tolist()
            self.identity_value_classes = [(name,) for name in self.identity_class_names]
            self.reference_value = reference_value
        self.n_classes = len(self.identity_value_classes)

    def get_label(self, identity_value):
        for class_idx, identity_value_class in enumerate(self.identity_value_classes):
            if identity_value in identity_value_class:
                return class_idx
    
    def get_labels(self, surveys):
        identity_values = self.get_identity_values(surveys)
        data_idxs = []
        labels = []
        for value_idx, identity_value in enumerate(identity_values):
            label = self.get_label(identity_value)
            if not label is None:
                data_idxs.append(value_idx)
                labels.append(label)
        return np.array(data_idxs), np.array(labels)
    
    def get_identity_values_single_key(self, surveys, id_key):
        if isinstance(id_key, str):
            id_key = (id_key,)
        identity_values = []
        for survey in surveys:
            identity_val = survey
            for key in id_key:
                identity_val = identity_val[key]
            identity_values.append(identity_val)
        return identity_values
    
    def get_identity_values(self, surveys):
        identity_values = []
        for identity_key in self.identity_keys:
            identity_values.append(self.get_identity_values_single_key(surveys, identity_key))
        if len(identity_values) == 1:
            return identity_values[0]
        return list(zip(*identity_values))
    
    def __str__(self):
        return self.category_name
    
    def __repr__(self):
        return self.category_name
    
def get_basic_regression_categories(surveys, exclude_counts_lt=1, exclude_categories=[]):
    identity_values = [
        ("age", ("age",), "18-24 years old"),
        ("gender", ("gender",), "Male"),
        ("education", ("education",), "University Bachelors Degree"),#"Graduate / Professional degree"
        ("employment_status", ("employment_status",), "Working full-time"),
        ("birth_region", ('location', 'birth_region'), "Europe"),
        ("reside_region", ('location', 'reside_region'), "Europe"),
        ("religion", ('religion', 'simplified'), "Christian"),
        ("ethnicity", ('ethnicity', 'simplified'), "White"),
        ("chosen_model", ('chosen_model',), "gpt-3.5-turbo"),
        ("conversation_type", ('conversation_type',), "unguided"),
    ]
    
    classification_categories = [
        IdentityCategory(identity_name, [identity_name], [identity_key], all_surveys=surveys, reference_value=reference, exclude_counts_lt=exclude_counts_lt)
        for identity_name, identity_key, reference in identity_values
        if not identity_name in exclude_categories
    ]
    return classification_categories

def get_limited_controls():
    category_to_controls = {
        "age": ["gender", "ethnicity", "conversation_type"],
        "gender": ["age", "ethnicity", "conversation_type"],
        "ethnicity": ["age", "gender", "conversation_type"],
        "education": ["gender", "ethnicity", "conversation_type"],
        "employment_status": ["gender", "ethnicity", "conversation_type"],
        "birth_region": ["age", "gender", "conversation_type"],
        "reside_region": ["age", "gender", "conversation_type"],
        "religion": ["conversation_type"],
    }
    return category_to_controls
    

def get_user_id_category(surveys):
    return IdentityCategory("user_id", ["user_id"], [("user_id",)], all_surveys=surveys, reference_value=None)