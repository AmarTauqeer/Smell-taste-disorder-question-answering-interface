import json

if __name__ == '__main__':
    question_ids = [8, 9, 12, 13, 14, 15, 16, 17, 18, 21, 22, 23, 23]

    questions_preprocessed = []

    with open('../resources/qald-6-test-multilingual.json', encoding="utf8") as json_file:
        data = json.load(json_file)
        questions = data['questions']
        for question in questions:
            qid = question['id']
            if qid in question_ids:
                multilang_qs = question['question']
                for multilang_q in multilang_qs:
                    lang = multilang_q['language']
                    if lang == 'en':
                        questions_preprocessed.append({
                            'id': qid,
                            'question': multilang_q['string'],
                            'file': 'question_{}.nxhd'.format(qid)})
                        break
    with open('../resources/questions.json', 'w', encoding='utf8') as json_d:
        json.dump({'questions': questions_preprocessed}, json_d)
