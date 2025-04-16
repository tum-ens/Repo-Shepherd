import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yaml
import utils.llm_api as llm_api

def convert_repo_to_txt():
    pass

def create_part(part_name, info, file_tree, model):
    '''
    Create the given section by gemini.
    :param: part_name: name of section
    :param: content: content of section
    btw, it seems that parameter can be improved. This will be done once UI is designed.
    :return: improved section
    '''
    with open("app/prompts/creation_prompt.yaml", 'r') as file:
        prompts_repo = yaml.safe_load(file)

    meta_prompt = prompts_repo["meta-prompt"]
    output_prompt = prompts_repo["output-meta"]
    # title need both title_prompt and about_prompt
    if info:
        output_prompt = prompts_repo["a_" + part_name] + info + "\n\n" + output_prompt

    if file_tree:
        file_tree_prompt = prompts_repo["file-tree"] + "\n\n" + file_tree
    else:
        file_tree_prompt = ""
    
    prompt = (meta_prompt + "\n\n"
        + prompts_repo[part_name] + "\n\n"
        + file_tree_prompt + "\n\n"
        + output_prompt + "\n\n"
    )
    # During development I use together_ai since it's faster.
    result = llm_api.gemini_api(prompt, model)

    # add section name if LLM misses it.
    if not result.startswith("##") and not part_name == "title":
        result = "## " + part_name[0].upper() + part_name[1:] + "\n\n" + result

    return result

def create_feature(existed_feature, file_tree, model):
    with open("app/prompts/creation_prompt.yaml", 'r') as file:
        prompts_repo = yaml.safe_load(file)
    features = [entry for entry in existed_feature if entry.strip()]
    
    if file_tree:
        file_tree_prompt = prompts_repo["file-tree"] + "\n\n" + file_tree
    else:
        file_tree_prompt = ""

    meta_prompt = prompts_repo["meta-prompt"]
    feature_prompt = prompts_repo["feature"] + "List only 1 feature. It should be different from:" + "\n\n"
    output_format = "You should only return feature and its description without any other sentences."

    prompt = meta_prompt + feature_prompt + str(features) + "\n\n" + file_tree_prompt + "\n\n" + output_format
    result = llm_api.gemini_api(prompt, model)
    return result


def structure_markdown(ordered_text, model):
    with open("app/prompts/creation_prompt.yaml", 'r') as file:
        prompts_repo = yaml.safe_load(file)

    instruction = prompts_repo["structure"]
    prompt = instruction + "\n\n" + ordered_text

    result = llm_api.gemini_api(prompt, model)
    return result
    