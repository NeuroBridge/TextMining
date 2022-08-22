# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 00:58:16 2022

@author: Lenovo
"""

def combine_wtsv(wtsv_path, ner_output):

    
    # divide the whole output file into multiple article-level output files
    # for articles with annotation in wtsv format
    
    num = 0
    lines = open(ner_output, encoding = 'utf-8').read().split('\n')[:-1]
    documents =  Document(conll_path, "test", False)
    for file in documents.files:
        f = open('output_cv_conll/output_'+file.split('.')[0] + '.txt', 'w', encoding = 'utf-8')
        doc = documents.sens_doc[file]
        
        for i in range(len(doc)):
            if len(doc[i])<200:
                for j in range(len(doc[i])):
                    prefix = 'http://maven.renci.org/NeuroBridge/neurobridge#'
                    true_label, pred_label = lines[num].split('  ')[1:]
                    true_label, pred_label = true_label.strip(), pred_label.strip()
                    if true_label != 'O':
                        true_label = prefix + true_label.split('-')[-1]
                    else:
                        true_label = '_'
                    if pred_label != 'O':
                        pred_label = prefix + pred_label.split('-')[-1]
                    else:
                        pred_label = '_'
                    f.write(doc[i][j].text + '\t' + true_label + '\t' + pred_label + '\n')
                    # commented line is the way of outputing wtsv files
                    # f.write(detail[i][g].order + '\t' + detail[i][g].loc + '\t' + detail[i][g].text + '\t' + true_label + '\t' + pred_label + '\n')
                    num += 1
                    print(num)
                f.write('\n')
        f.close()




def combine_conll(conll_path, ner_output):

    
    # divide the whole output file into multiple article-level output files
    # for articles without annotation in conll format

    num = 0
    lines = open(ner_output, encoding = 'utf-8').read().split('\n')[:-1]
    prefix = 'http://maven.renci.org/NeuroBridge/neurobridge#'
    for file in os.listdir(conll_path):
        f = open('output_conll/output_'+file, 'w', encoding = 'utf-8')
        
        # following commented lines of codes are used to add header of wtsv files
        # f.write('#FORMAT=WebAnno TSV 3.3\n')
        # f.write('#T_SP=webanno.custom.ConceptLayer|identifier\n\n\n')
        
        
        document = [sen.split('\n') for sen in open(conll_path+file, 'r', encoding = 'utf-8').read().split('\n\n')[:-1]]
        offset = 0
        num_ent = 0
        for i in range(len(document)):
            
            tokens = [j.split(' ')[0] for j in document[i]]
            # header = TreebankWordDetokenizer().detokenize(tokens).replace(' , ',',').replace(' .','.').replace(' !','!').replace(' ?','?').replace(' : ',': ').replace(' \'', '\'')
            previous_label = '_'
            for j in range(len(document[i])):
                true_label, pred_label = lines[num].split('  ')[1:]
                true_label, pred_label = true_label.strip(), pred_label.strip()
                if true_label != 'O':
                    true_label = prefix + true_label.split('-')[-1]
                else:
                    true_label = '_'
                if pred_label != 'O':
                    pred_label = prefix + pred_label.split('-')[-1]
                else:
                    pred_label = '_'
                token = tokens[j]
                f.write(token + '\t' + true_label + '\t' + pred_label + '\n')
                # f.write(str(i+1) + '-' + str(j+1) + '\t' + str(offset) + '-' + str(offset+len(token))+ '\t' + token + pred_label + '\n')
                offset = offset+len(token)+1 
                num += 1
            f.write('\n')
        f.close()







def article_labeling(inputpath, outputfile):

    csv_path = open('output.csv','w',encoding  = 'utf-8')
    csv_output = csv.writer(csv_path)    

    for i in os.listdir(inputpath):
      # the following line is used to choose 316 test articles   
      # if i.split('.')[0].split('_')[1]+'.wtsv' not in os.listdir("OUTPUT_Annotated_Papers_51") or i.split('.')[0].split('_')[1]+'.wtsv' in os.listdir("test_conll"):
        offsets = [{}]
        file = open(inputpath+i, 'r', encoding = 'utf-8').read().split('\n')
        true_labels, pred_labels, tokens = [],[], []
        pre_label = ''
        pre_loc = -1000
        
        # locate entities identified by 2 stage NER model
        for j in range(len(file)):
            if file[j]:
                tokens.append(file[j].split('\t')[0])
                if file[j].split('\t')[-1] != '_':
                    true_labels.append(file[j].split('\t')[-2])
                    pred_labels.append(file[j].split('\t')[-1])
                    if file[j].split('\t')[-1] != pre_label:
                        offset = [n_token, n_token+1]
                        pre_label = file[j].split('\t')[-1]
                        label = file[j].split('\t')[-1].split('#')[-1]
                        for j in range(j+1, len(f)):
                            if file[j].split('\t')[-1] == pre_label:
                                offset[-1] += 1
                            else:
                                break

                        if label not in offsets[0].keys():
                            offsets[0][label] = [offset]
                        else:
                            offsets[0][label].append(offset)
                else:
                    pre_label = ''
        pred = Counter(pred_labels)
        
        
        # evaluate 2 stage pipeline performance in article level 
        true_set = set([i.split('#')[-1] for i in true_labels if i != '_'])
        pred_set = set([i.split('#')[-1] for i in pred_labels if i != '_'])
        union = true_set & pred_set
        csv_output.writerow([i, len(union)/len(pred_set), len(union)/len(true_set)])
        
        # find a best snippet
        sens = open(inputpath+i, 'r', encoding = 'utf-8').read().split('\n\n')
        predicted = [[k.split('\t')[-1].split('#')[0] for k in j.split('\n')] for j in sens][:-1]
        words= [[k.split('\t')[0] for k in j.split('\n')] for j in sens][:-1]
        maximum = 0
        argmax = 0
        
        for j in range(len(predicted)):
            num_ent = predicted[j].count('http://maven.renci.org/NeuroBridge/neurobridge')
            if num_ent > maximum:
                maximum = num_ent
                argmax = j

        # generate NBC and snippet for each article
        j =  open('preprocessed/' + i.split('_')[1].split('.')[0] + '.json').read()
        j = json.loads(j)
        j["abstract"] = str(j["abstract"])
        j["title"] = str(j["title"])
        j['pmid'] = str(j['pmid'])
        j['NBC'] = [i.split('#')[-1] for i in pred if i != '_']
        j["offsets"] = offsets
        j["text"] = TreebankWordDetokenizer().detokenize(tokens).replace(' , ',',').replace(' .','.').replace(' !','!').replace(' ?','?').replace(' : ',': ').replace(' \'', '\'')
        x = open('output_316_jsons/' + i.split('_')[1].split('.')[0] + '.json', 'w', encoding = 'utf-8')
        json.dump(j, x)
