from datasets import load_dataset
import numpy as np

##  Data Loaders

def load_prism(conversation_type=None, max_conversation_len=None):
    '''Loads Prism Dataset'''
    surveys = load_dataset("HannahRoseKirk/prism-alignment", "survey")
    conversations = load_dataset("HannahRoseKirk/prism-alignment", "conversations")
    conversations = filter_conversations(conversations["train"], conversation_type=conversation_type, max_conversation_len=max_conversation_len)
    surveys = filter_surveys(conversations, surveys)
    return conversations, surveys


def filter_conversations(conversations, conversation_type=None, max_conversation_len=None):
    filtered = []
    for conversation in conversations:
        if conversation_type is None or conversation["conversation_type"] == conversation_type:
            chosen_conversation_turns = [turn for turn in conversation["conversation_history"] if not turn["if_chosen"]==False]
            if max_conversation_len is not None and len(chosen_conversation_turns)//2 > max_conversation_len:
                chosen_conversation_turns = chosen_conversation_turns[:2*max_conversation_len]
            filtered.append({
                "user_id": conversation["user_id"],
                "chosen_model": chosen_conversation_turns[1]["model_name"],
                "conversation_type": conversation["conversation_type"],
                "conversation_turns": len(chosen_conversation_turns),
                "conversation_history": chosen_conversation_turns,
            })
    return filtered

def filter_surveys(conversations, surveys):
    '''Creates a list of user surveys, with the survey at idx i corresponding to the user in conversation i at idx i'''
    filtered_surveys = []
    for utterance in conversations:
        user_id = utterance["user_id"]
        user_idx = int(user_id.replace("user", ""))
        survey = surveys["train"][user_idx]
        assert survey["user_id"] == user_id
        filtered_surveys.append(survey)
    return filtered_surveys

def update_surveys(surveys, additional_info):
    for survey_idx, survey in enumerate(surveys):
        for k, v in additional_info.items():
            survey[k] = v[survey_idx]

## Data Utilities

def split_k_fold_by_user(users, labels, random_seed=12, k=10):
    '''
    For each label value, split the data idxs with that label k-fold but make sure that instances of the same user identity are in the same fold.
    Assumes that each user only corresponds to a single label value. 
    Returns data idxs of split.
    '''
    if not random_seed is None:
        np.random.seed(random_seed)
    label_vals = set(labels)
    all_split_idxs = [[] for _ in range(k)]

    for label_val in label_vals:
        # class_data = data[labels == label_val]
        class_users = users[labels == label_val]
        class_user_set = np.unique(class_users)
        np.random.shuffle(class_user_set)
        user_splits = np.array_split(class_user_set, k)
        if len(user_splits[-1]) == 0:
            return None
        split_idxs = [np.arange(len(users))[np.any(users.reshape(-1,1) == user_split.reshape(1,-1), axis=1)] for user_split in user_splits]
        for fold_idx, idxs in enumerate(split_idxs):
            all_split_idxs[fold_idx].append(idxs)
            
    # print([[len(x) for x in xs] for xs in all_split_idxs])
    all_split_idxs = [np.concatenate(idxs) for idxs in all_split_idxs]
    return all_split_idxs

def conversation_to_prompt(conversations, use_model_responses=True, remove_final_response=False):
    prompts = []
    for conversation in conversations:
        prompt = []
        last_turn_assistant=False
        for turn in conversation["conversation_history"]:
            if turn['role'] == 'model' or turn['role'] == "assistant":
                if last_turn_assistant: #have to add this because 216 of the conversations in the dataset have an error where they duplicate the same model response multiple times
                    continue
                prompt.append({'role': 'assistant', 'content': turn['content'] if use_model_responses else ''})
                last_turn_assistant = True
            else:
                prompt.append({'role': turn['role'], 'content': turn['content']})
                last_turn_assistant = False
        if remove_final_response:
            if prompt[-1]["role"] == "assistant":
                prompt = prompt[:-1]
        prompts.append(prompt)
    return prompts