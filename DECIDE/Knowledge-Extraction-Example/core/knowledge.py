from itertools import combinations, product
import torch

from utils.utils import html_parser, is_short_post
from utils.utils import is_same, compute_min_distance, opposite_verdict
from utils.utils import clean_knowledge, remove_duplicate_knowledge, knowledge_conflict_solve

from config.regex import (
    ONLY_VERSION_PATTERN,
    NAME_WITH_VERSION_PATTERN,
    VERSION_PATTERN
)
from config.library import COMPONENT_LIST
from config.config import ANSWER, QUESTION 
from config.config import T5
from config.config import QUESTION_TEMPLATE

KNOWLEDGE = "knowledge"
EVA = "eva"

class Post(object):
    def __init__(self, post_type: str, _id: str, _title: str, _body: str, _tags: list, _score: str, _predictor=None):
        self.id = _id
        self.title = _title if post_type == QUESTION else None
        self.body = _body
        self.tags = _tags if post_type == QUESTION else None
        self.score = _score
        self.predictor = _predictor
        if post_type == QUESTION:
            self.post_content = ''
            self.p_content = ''
            self.ol_ul_content = ''
            self.short_post = ''
            self.qa_candidate_content = ''
            self.eva_list = ''
            self.ol_ul_knowledge = ''
        elif post_type == ANSWER:
            self.post_content, self.p_content, self.ol_ul_content = html_parser(_body)
            self.short_post = is_short_post(self.post_content)
            self.qa_candidate_content, self.eva_list, self.ol_ul_knowledge = self.post_parser()

    def get_content(self):
        print(self.post_content)


    def p_parser(self):
        eva_list = []
        for p in self.p_content:
            flag, res = self.ev_extractor(p, "p")
            if flag == EVA:
                eva_list.append(res)
            else:
                raise Exception(f"Unexpected knowledge from <p>. Post id: {self.id}")
        
        return eva_list

    def ol_ul_parser(self):
        li_list = []
        li_eva_list = []
        ul_ol_knowledge = []

        for ol_ul in self.ol_ul_content:
            li_knowledge = []
            # is_knowledge = True
            for li in ol_ul:
                flag, res = self.ev_extractor(li, "li")
                if flag == KNOWLEDGE:
                    if res != None:
                        li_knowledge.extend(res)
                elif flag == EVA:
                    # is_knowledge = False
                    li_list.append(li)
                    li_eva_list.append(res)
            if len(li_knowledge) > 0:
                knowledge_candidate = combinations(li_knowledge, 2)
                for knowledge in knowledge_candidate:
                    if is_same(knowledge[0].split()[0], knowledge[1].split()[0]):
                        continue
                    else:
                        ul_ol_knowledge.append((knowledge[0], knowledge[1], 'yes', 0))

        return li_list, li_eva_list, ul_ol_knowledge

    def post_parser(self):
        qa_candidate_content = []
        eva_list = []
        knowledge = []

        if len(self.ol_ul_content) > 0:
            li_list, li_eva_list, ul_ol_knowledge = self.ol_ul_parser()
            assert len(li_list) == len(li_eva_list), f'Error in ol_ul_parser: {self.id}'
            qa_candidate_content.extend(li_list)
            eva_list.extend(li_eva_list)
            knowledge = ul_ol_knowledge
        if len(self.p_content) > 0:
            p_entity_version = self.p_parser()
            assert len(self.p_content) == len(p_entity_version), f'Error in p_parser: {self.id}'
            qa_candidate_content.extend(self.p_content)
            eva_list.extend(p_entity_version)

        assert len(qa_candidate_content) == len(eva_list), f'Error in post_parser: {self.id}'
        return qa_candidate_content, eva_list, knowledge

    # find entity name in a 'entity-version' format string
    def find_entity(self, ev_str):
        for entity in COMPONENT_LIST:
            if entity in ev_str:
                return entity
        return ""

    def format_entity_version(self, ev_str: str):
        entity_list = []
        version_list = []
        entity = self.find_entity(ev_str)
        if entity == "":
            raise Exception("Entity name not found")
        
        version_regex = VERSION_PATTERN.findall(ev_str)
        for version in version_regex:
            v_strip = version[0].strip()
            if v_strip == "":
                continue
            v = v_strip[:-1] if v_strip[-1] == "." or v_strip[-1] == "," else v_strip
            # if v == "32" or v == "64":
            #     v += "-bit"
            version_list.append(v)
            entity_list.append(entity)

        assert len(entity_list) == len(version_list), f'entity_list and version_list length not equal, {self.id}'
        return entity_list, version_list
    
    # identify entity name and version number, then match them
    def ev_extractor(self, content: str, tag: str):
        entity_list = []
        version_list = []
        ev_list = []
        save_content = content

        # find definite entity name and version number
        definite_list = []
        for single_reg in NAME_WITH_VERSION_PATTERN:
            regex_match_list = single_reg.findall(save_content)
            if len(regex_match_list) == 1:
                if regex_match_list[0][0].strip() == content.strip() and tag == "li":
                    res_entity, res_version = self.format_entity_version(
                        regex_match_list[0][0]
                    )
                    assert len(res_entity) == len(res_version), f'Error in ev_extractor: {self.id}'
                    if len(res_entity) == 0:
                        knowledge_candidate = None
                    else:
                        knowledge_candidate = []
                        for i in range(len(res_entity)):
                            knowledge_candidate.append(f"{res_entity[i]} {res_version[i]}")
                        # knowledge_candidate = f"{res_entity[0]} {res_version[0]}"
                    return KNOWLEDGE, knowledge_candidate
                else:
                    definite_list.append(regex_match_list[0][0].strip())
                    save_content, n = single_reg.subn(" **** ", save_content)
            elif len(regex_match_list) > 1:
                for regex_match in regex_match_list:
                    definite_list.append(regex_match[0].strip())
                save_content, n = single_reg.subn(" **** ", save_content)
            else:
                continue

        for ev in definite_list:
            res_entity, res_version = self.format_entity_version(ev)
            entity_list.extend(res_entity)
            version_list.extend(res_version)
        single_entity = []
        single_version = []

        tmp_content = save_content
        for entity in COMPONENT_LIST:
            if entity in tmp_content:
                if entity in ['wxpython', 'tensorflow-gpu', 'flask-sqlalchemy', 'tesnorflow-core-platform', 'tensorflow-transform']:
                    tmp_content = tmp_content.replace(entity, "!!!")
                single_entity.append(entity)

        for single_reg in ONLY_VERSION_PATTERN:
            res = single_reg.findall(save_content)
            if len(res) != 0:
                for version in res:
                    single_version.append(version[0].strip())

        entity_wait_list = []
        version_wait_list = []
        for version in single_version:
            v_strip = version.strip()
            if v_strip == "":
                continue
            v = v_strip[:-1] if v_strip[-1] == "." or v_strip[-1] == "," else v_strip
            v = v[1:] if v[0] == "(" else v
            if v not in version_list:
                version_wait_list.append(v)

        # entity_wait_list = list(set(entity_wait_list))
        entity_wait_list = list(set(single_entity))
        version_wait_list = list(set(version_wait_list))

        add_entity_list = []
        add_version_list = []

        if len(version_wait_list) > 0 and len(entity_wait_list) > 0:
            pred_res = self.predictor.predict(content)
            words = pred_res["words"]
            pos = pred_res["pos"]
            assert len(words) == len(pos), f'Error in predictor (words and pos): {self.id}'
            wp_zip = list(zip(words, pos))

            entity_idx = {}
            version_idx = {}
            final_zip = list(wp_zip)
            for idx, item in enumerate(final_zip):
                if item[0] in version_wait_list:
                    if item[0] not in version_idx.keys():
                        version_idx[item[0]] = [idx]
                    else:
                        version_idx[item[0]].append(idx)
                elif item[0] in entity_wait_list:
                    if item[0] not in entity_idx.keys():
                        entity_idx[item[0]] = [idx]
                    else:
                        entity_idx[item[0]].append(idx)
            
            if len(entity_idx) > 0 and len(version_idx) > 0:

                if len(entity_idx) >= len(version_idx):
                    for version, vidx_list in version_idx.items():
                        min_dist = 99999999
                        min_entity = ""
                        for entity, eidx_list in entity_idx.items():
                            dist = compute_min_distance(vidx_list, eidx_list, final_zip)
                            if dist < min_dist:
                                min_dist = dist
                                min_entity = entity

                        if min_dist < 9999:
                            add_entity_list.append(min_entity)
                            add_version_list.append(version)
                else:
                    for entity, eidx_list in entity_idx.items():
                        min_dist = 99999999
                        min_version = ""
                        for version, vidx_list in version_idx.items():
                            dist = compute_min_distance(vidx_list, eidx_list, final_zip)
                            if dist < min_dist:
                                min_dist = dist
                                min_version = version
                        if min_dist < 9999:
                            add_entity_list.append(entity)
                            add_version_list.append(min_version)


        entity_list = entity_list + add_entity_list
        version_list = version_list + add_version_list

        
        entity_wait_set = set(entity_wait_list)
        entity_set = set(entity_list)
        extra_entity = list(entity_wait_set.difference(entity_set))

        extra_version = version_wait_list if len(version_wait_list) > 0 and len(entity_wait_list) == 0 else []

        ev_list = []
        for entity, version in zip(entity_list, version_list):
            ev_list.append(f"{entity} {version}")
        ev_list = list(set(ev_list))

        eva_res = {
            'ev_list': ev_list,
            "extra_entity": extra_entity,
            'extra_version': extra_version
        }

        return EVA, eva_res

class PostKnowledge(object):
    def __init__(self, _answer: Post, _model_name, _model=None, _tokenizer=None, _device='cpu'):
        self.answer = _answer
        self.tokenizer = _tokenizer
        self.model = _model
        self.model_name = _model_name
        self.device = _device
        self.lib_final_ev_knowledge = self.knowledge_extract()
        self.final_lib_knowledge = self.knowledge_consolidation()

    # -------------- model: T5 ----------------
    def compute_loss(self, input_ids, answer):
        input_ids = input_ids.to(self.device)
        labels = self.tokenizer(answer, return_tensors="pt").input_ids
        labels = labels.to(self.device)
        res = self.model.forward(input_ids, labels=labels)
        torch.cuda.empty_cache()
        return res.loss.tolist()

    def run_model(self, input_string, **generator_args):
        input_ids = self.tokenizer.encode(input_string, return_tensors="pt")
        input_ids = input_ids.to(self.device)
        # print_gpu_utilization()
        res = self.model.generate(input_ids, **generator_args)
        return input_ids, self.tokenizer.batch_decode(res, skip_special_tokens=True)

    # -------------- generate input ----------------
    def lib_question_template(self, ev1, ev2):
        question1 = f"Is {ev1} compatible with {ev2}?"
        question2 = f"Is {ev1} not compatible with {ev2}?"
        return [question1, question2]
    
    def generate_input_string(self, context, question):
        if self.model_name == T5:
            input_string = question.lower() + ' \\n ' + context.lower()
        return input_string
    
    def ask_QA(self, input):
        if self.model_name == T5:
            input_ids, res = self.run_model(input)
            loss = self.compute_loss(input_ids, res)
            return input_ids, res, loss

    def get_QA_knowledge(self, candidate, context):
        qa_knowledge = []
        for c in candidate:
            questions = []
            pos_answer = []
            neg_answer = []
            questions = self.lib_question_template(c[0], c[1])
            for question in questions:
                model_input = self.generate_input_string(context, question)
                input_ids, res, loss = self.ask_QA(model_input)
                if self.model_name == T5:
                    verdict = res[0].lower()
                if QUESTION_TEMPLATE == 'all':
                    if 'not' in question:
                        neg_answer.append((verdict, loss))
                    else:
                        pos_answer.append((verdict, loss))
                elif QUESTION_TEMPLATE == 'pos':
                    pos_answer.append((verdict, loss))
                elif QUESTION_TEMPLATE == 'neg':
                    neg_answer.append((verdict, loss))
            
            final_ans = ''
            final_loss = 1
            final_ans, final_loss = self.choose_answer(pos_answer, neg_answer)
            qa_knowledge.append((c[0], c[1], final_ans, final_loss))
        
        return qa_knowledge

    def choose_answer(self, answer_list1, answer_list2=None):
        LOSS = 1
        VERDICT = 0
        answer = []
        if QUESTION_TEMPLATE == 'all':
            for pos_ans, neg_ans in zip(answer_list1, answer_list2):
                if pos_ans[VERDICT] != neg_ans[VERDICT]:
                    answer.append((pos_ans[VERDICT], min(pos_ans[LOSS], neg_ans[LOSS])))
                else:
                    if pos_ans[LOSS] < neg_ans[LOSS]:
                        answer.append((pos_ans[VERDICT], pos_ans[LOSS]))
                    elif pos_ans[LOSS] > neg_ans[LOSS]:
                        answer.append((opposite_verdict(pos_ans[VERDICT]), neg_ans[LOSS]))
                    else:
                        answer.append(('unknown', pos_ans[LOSS]))
        elif QUESTION_TEMPLATE == 'pos':
            for pos_ans in answer_list1:
                answer.append((pos_ans[VERDICT], pos_ans[LOSS]))
        elif QUESTION_TEMPLATE == 'neg':
            for neg_ans in answer_list2:
                answer.append((opposite_verdict(neg_ans[VERDICT]), neg_ans[LOSS]))
        
        loss = 9999
        selected_answer = ''
        for ans in answer:
            if ans[LOSS] < loss:
                selected_answer = ans[VERDICT]
                loss = ans[LOSS]
        return selected_answer, loss

    def knowledge_extract(self):
        lib_final_ev_knowledge = []

        for qa_content, eva in zip(self.answer.qa_candidate_content, self.answer.eva_list):
            ev_num = len(eva['ev_list'])
            extra_entity_num = len(eva["extra_entity"])
            extra_version_num = len(eva["extra_version"])

            # no need to calculate knowledge candidate
            if (ev_num + extra_entity_num + extra_version_num) < 2:
                continue
            lib_ev_candidate = []
            lib_extra_candidate = []
            # generate lib_ev_candidate and lib_extra_candidate
            for ev_tuple in list(combinations(eva['ev_list'], 2)):
                if is_same(ev_tuple[0].split()[0], ev_tuple[1].split()[0]):
                    continue
                lib_ev_candidate.append(ev_tuple)
            for ev_tuple in list(product(eva['ev_list'], eva["extra_entity"])):
                if is_same(ev_tuple[0].split()[0], ev_tuple[1].split()[0]):
                    continue
                lib_extra_candidate.append(ev_tuple)
            # ------------------------------------------
            # ask QA
            lib_ev_knowledge = self.get_QA_knowledge(lib_ev_candidate, qa_content)
            lib_final_ev_knowledge.extend(lib_ev_knowledge)
        return lib_final_ev_knowledge

    def knowledge_consolidation(self):
        lib_knowledge_list = self.lib_final_ev_knowledge + self.answer.ol_ul_knowledge
        # strip version, standardize entity name, and sort entity name
        lib_clean_knowledge_list = clean_knowledge(lib_knowledge_list)

        # remove duplicate knowledge
        non_repeat_lib_knowledge_list = remove_duplicate_knowledge(lib_clean_knowledge_list)

        # solve knowledge conflict
        final_lib_knowledge = knowledge_conflict_solve(non_repeat_lib_knowledge_list)
        return final_lib_knowledge

    def get_knowledge(self):
        print('Knowledge extract:')
        for knowledge in self.final_lib_knowledge:
            relation = 'compatible' if knowledge[2] == 'yes' else 'incompatible'
            print(f'(\'{knowledge[0]}\', \'{knowledge[1]}\', \'{relation}\')')
