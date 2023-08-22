from core.knowledge import Post, PostKnowledge
from config.config import T5_MODEL, T5, ANSWER

import xml.etree.ElementTree as ET
from allennlp_models.pretrained import load_predictor
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

STRUCTURE_MODEL_NAME = 'structured-prediction-biaffine-parser'

def parse_xml_data(line_data):
    line_data = line_data.strip()
    xml_parse = ET.fromstring(line_data)
    res = xml_parse.attrib
    return res


def main(model_name):
    predictor = load_predictor(STRUCTURE_MODEL_NAME)
    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device = 'cpu'
    tokenizer = T5Tokenizer.from_pretrained(T5_MODEL)
    model = T5ForConditionalGeneration.from_pretrained(T5_MODEL)
    model = model.to(device)
    # print(f'Successfully load T5 model in device: {device}.')
    post_f = open('./data/post.xml', 'r')
    post_data = post_f.readlines()
    for p_data in post_data:
        if p_data.strip() == '':
            continue
        parsed_data = parse_xml_data(p_data)
        answer_Post = Post(
            ANSWER,
            parsed_data['Id'],
            '',
            parsed_data['Body'],
            '',
            parsed_data['Score'],
            predictor
        )
        post_knowledge = PostKnowledge(answer_Post, model_name, model, tokenizer, device)
        print(f'Extracting knowledge from Stack Overflow post: https://stackoverflow.com/questions/{parsed_data["Id"]}')
        post_knowledge.get_knowledge()
        print('--------------------------------')

    post_f.close()

if __name__ == '__main__':
    model_name = T5
    main(model_name)