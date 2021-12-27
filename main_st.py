import streamlit as st
import os
import sys
import plotly as py
import plotly.graph_objs as go
from pandas_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report

project = 'Model_training'  # 工作项目根目录
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")).replace("\\", "/") + '/' + project )
# st.write(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")).replace("\\", "/") + '/' + project)

from Model_training.main import *
from Model_training.tfidf_value import *
from Online_API.utils import *
from internal import *

import time
import base64


# 可以修改的值
Cancer_type_list = ["lymph", "liver", "glioma", "esophageal", "lung", "gist","breast"] # 癌种
t_tag = ["ihc_k", "fish_k","mol_k"] # 数据增强删除或替换的label

# 标题
st.sidebar.title('R_squared_pipe')
st.sidebar.markdown("genowis info restructuring and reasoning pipeline")

# 数据质控
st.sidebar.markdown('**数据质控**')

#检查标注数据、上传标注数据文件
to_upload_file = st.sidebar.radio('Would you like to upload new doccano data?',(False,True))
# st.set_option('deprecation.showfileUploaderEncoding', False)
# uploaded_file = st.sidebar.file_uploader("Choose a Doccano JSON file", type=["json","json1"])
if to_upload_file:
    # 不显示上传文件产生的警告信息
    st.set_option('deprecation.showfileUploaderEncoding', False)
    uploaded_file = st.file_uploader("Choose a JSON file", type="json")
    #检查标注数据
    if st.button("Inspect Annotated data"):
        if uploaded_file:
            data = uploaded_file.getvalue()
            result_temp = pd.DataFrame()
            count=1
            for value in data.split("\n"):
                if len(value) > 0:
                    temp = {}
                    value = value.replace("null", "None")
                    temp.setdefault('line_index', []).append(count)
                    count += 1
                    text = eval(value)["text"]
                    temp.setdefault('text', []).append(text)
                    labels = eval(value)['labels']
                    for value in labels:
                        temp.setdefault(value[2], []).append(text[value[0]:value[1]])
                    temp_df = pd.DataFrame.from_dict(temp, orient='index').T
                    result_temp = pd.concat([result_temp, temp_df], ignore_index = True)
            result_temp['line_index']=result_temp['line_index'].fillna(method='ffill')

            st.dataframe(result_temp, height=800)
            st.write('标注数据分布')
            report = ProfileReport(result_temp,samples=None, correlations=None, missing_diagrams=None, duplicates=None, interactions=None,html={"style":{"full_width":True}})
            st_profile_report(report)
            csv = result_temp.to_csv(index=False,sep="\t",encoding="utf_8")
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}">Download csv File</a> (right-click and save as &lt;some_name&gt;.csv)'
            st.markdown(href, unsafe_allow_html=True)
else:
    pass


#选择癌种
st.sidebar.markdown('**模型训练**')
Cancer_type = st.sidebar.selectbox('Choose cancer type',Cancer_type_list)

#自动计算归一模块中使用的tfidf值
tfidf = TFIDF_cal(cancer_type=Cancer_type)
tfidf.to_file()

#上传文件
if st.sidebar.button('Upload'):
    if os.path.exists(
            join(path_base, "Model_training/doccano_file/doccano_{}.json".format(Cancer_type)).replace("\\", "/")):
        os.remove(join(path_base, "Model_training/doccano_file/doccano_{}.json".format(Cancer_type)).replace("\\", "/"))
        st.write('删除旧的标注文件：%s'%Cancer_type)
    else:
        st.write("要删除的旧的标注文件不存在 ！")
    if uploaded_file is not None:
        data=uploaded_file.getvalue()
        with open(
            join(path_base, "Model_training/doccano_file/doccano_{}.json".format(Cancer_type)).replace("\\", "/"),
            "w", encoding="utf-8") as f:
            for value in data.split("\n"):
                if len(value)>0:
                    f.write(str(value).strip())
                    f.write('\n')
            # f.write("\n")
            f.close()
        st.write("新的标注文件上传成功 ！")
if os.path.exists(join(path_base, "Model_training/doccano_file/doccano_{}.json".format(Cancer_type)).replace("\\", "/")):
    st.sidebar.markdown("exist !")
else:
    st.sidebar.markdown("not exist !")



# 选择训练集、测试集、验证集比例
r1 = st.sidebar.selectbox('Choose the ratio of training set', (0.8, 0.7))
# r2 = st.sidebar.selectbox('Choose the ratio of validation set', (0.9,0.8))

#选择是否数据增强
use_augment = st.sidebar.radio(
    'Would you like to use data augmentation?',
    (False,True))
if use_augment:
    st.sidebar.markdown('--------------------------------------------------')
    t_tag_list = st.sidebar.multiselect('Choose t_tag_list',t_tag)
    # select='conca'、'del'、'subs'
    select = st.sidebar.selectbox('Choose t_tag_list',('conca','del','subs'))  # 选择增强策略
    N = st.sidebar.slider('Select the number of items to be augmented',0, 1000, 200)  # 需要增强的条数，根据实际需要选择
    iterations = st.sidebar.slider('Select the times of iterations',0, 10, 2)  # 迭代次数
    M = st.sidebar.slider('Select the number of items to concat',0, 5, 1)  # M为拼接的条数，比如M=2，就是拼接两条病例,默认为1
    ratio = st.sidebar.slider('Select the ratio to be deleted',0, 100, 50)  # 删除的比例，默认为0.5
    st.sidebar.markdown('--------------------------------------------------')
    # 训练模型
    if st.sidebar.button('Train with augmentation'):
        st.write("训练开始：")
        main(use_augment, Cancer_type, r1, r1 + 0.1, t_tag_list, select, N, iterations, M, ratio*0.01)
        st.write("训练结束。")
else:
    st.sidebar.markdown("no augmentation")
    if st.sidebar.button('Train without augmentation'):
        st.write("训练开始：")
        main(use_augment,Cancer_type,r1,r1+0.1)
        st.write("训练结束。")

###############################################################################################
# 读取读取文件
if st.sidebar.button("See evaluation"):
    if os.path.exists(join(path_base, "Model_training/{}_output.txt".format(Cancer_type)).replace("\\", "/")):
        evaluate_path=join(path_base, "Model_training/{}_output.txt".format(Cancer_type)).replace("\\", "/")
        file=open(evaluate_path,'r',encoding='UTF-8')
        data = ''.join(file.readlines())
        value_list=[]
        for value in data.split('\n'):
            if len(value) > 0:
                value_list.append(value)

        value_list_str="".join(value_list).replace( ' ' , '' )
        index_list=[]
        for m in re.finditer("label_accuracy", value_list_str):
            index_list.append(m.end())
        for m in re.finditer("label_recall", value_list_str):
            index_list.append(m.start())
            index_list.append(m.end())
        for m in re.finditer("label_wrong", value_list_str):
            index_list.append(m.start())
        label_accuracy = eval(value_list_str[index_list[0]+1:index_list[1]])
        label_recall = eval(value_list_str[index_list[2]+1:index_list[3]])
        # st.write(label_accuracy.values())

        # 可视化
        pyplt = py.offline.plot
        # Trace1
        trace_basic1 = go.Bar(
            x=list(label_accuracy.keys()),
            y=[v[2] for v in label_accuracy.values()],
            name='label_accuracy'
        )
        trace_basic2 = go.Bar(
            x=list(label_recall.keys()),
            y=[v[2] for v in label_recall.values()],
            name='label_recall'
        )
        trace = [trace_basic1, trace_basic2]
        # Layout
        layout_basic = go.Layout(
            title='accuracy & recall',
            template="plotly_dark", #画布
            xaxis={"tickangle": 0} # x轴坐标倾斜60度
        )
        # Figure
        figure_basic = go.Figure(data=trace, layout=layout_basic)
        st.plotly_chart(figure_basic)

        b64 = base64.b64encode(data.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}">Download TXT File</a> (right-click and save as &lt;some_name&gt;.txt)'
        st.markdown(href, unsafe_allow_html=True)
    else:
        st.write("the file is nonexistent or nonreadable !")


##############################################################################################
st.sidebar.markdown('**模型预测**')

#选择是否单条预测
Single_prediction = st.sidebar.radio('Would you like to predict One case?',("No","Yes"))

#预测单条病例文本
# if st.sidebar.button("Forecast single case text"):
def pred(Cancer_type,text):
    #Cancer_type='esophageal'
    if os.path.exists(join(path_base, 'Online_API/model_zoo/{}.pkl').format(Cancer_type).replace("\\", "/")):
        try:
            BiLSTMCRF_MODEL_PATH = join(path_base, 'Online_API/model_zoo/{}.pkl').format(Cancer_type).replace("\\", "/")
            bilstm_model = load_model(BiLSTMCRF_MODEL_PATH)
            # word = '(\r|\n|\s){1}'
            # text = re.sub(word, '', text)
            return bilstm_model.word_label_pred([text], Cancer_type)
        except:
            return "请输入文本或导入模型pkl文件！"
    else:
        return "没有找到模型pkl文件！"

# st.sidebar.markdown('单条病例文本预测')
if Single_prediction == "Yes":
    #st.write("单条病例文本预测：")
    text=st.text_area('',height=200)
    result=pred(Cancer_type,text)
    st.write(result)
    # st.write('-------------------------------')

#批量病例文本预测
t = time.time()
time.sleep(5)

upload_to_structure = st.sidebar.radio('Would you like to upload file to be structured?',("No","Yes"))
st.sidebar.markdown('批量病例文本预测')
if upload_to_structure == "Yes":
    #st.write("选择上传待结构化文件：")
    st.set_option('deprecation.showfileUploaderEncoding', False)
    uploaded_file = st.file_uploader("Choose a CSV/EXCEL file", type=["csv","xlsx"])

    if uploaded_file:
        if st.button('Upload excel file'):
            data = pd.read_excel(uploaded_file)
            data.to_excel(join(path_base, "EIR_Uploaded/{}_{}.xlsx".format(Cancer_type,int(t))).replace("\\", "/"))
        elif st.button('Upload csv file'):
            data = pd.read_csv(uploaded_file)
            data.to_csv(join(path_base, "EIR_Uploaded/{}_{}.csv".format(Cancer_type,int(t))).replace("\\", "/"))
    else:
        pass

#参数设置

parameter_setting = st.sidebar.radio('Do you need to set parameters ?',("No","Yes"))
if parameter_setting == "Yes":
    st.sidebar.markdown('--------------------------------------------------')
    redundancy = st.sidebar.text_area('redundancy : list',value='[]')
    args.redundancy =eval(redundancy)
    translation_basic_update = st.sidebar.text_area('translation_basic_update : dict',value='{}')
    args.translation_basic_update =eval(translation_basic_update)
    translation_diag_update = st.sidebar.text_area('translation_diag_update : dict',value='{}')
    args.translation_diag_update =eval(translation_diag_update)
    helpers_main = st.sidebar.text_area('helpers_main : list',value='[]')
    args.helpers_main =eval(helpers_main)
    args.by_cancer = Cancer_type
    args.method_window = st.sidebar.slider('Select the method_window',0, 30, 15)
    helpers_rightward = st.sidebar.text_area('helpers_rightward : list',value='[]')
    args.helpers_rightward =eval(helpers_rightward)
    top_level = st.sidebar.text_area('top_level : list',value='[]')
    args.top_level =eval(top_level)
    nest_labels = st.sidebar.text_area('nest_labels : list',value='[]')
    args.nest_labels = eval(nest_labels)
    args.use_dict = st.sidebar.radio('Would you like to use dict ?',(False,True))
    args.use_normer = st.sidebar.radio('Would you like to use normer ?',(True,False))
    args.use_normer_reasoner = st.sidebar.radio('Would you like to use reasoner ?',(True,False))
    st.sidebar.markdown('--------------------------------------------------')
else:
    pass

if st.sidebar.button("Predict"):
    path_temp = join(path_base, "EIR_Uploaded/").replace("\\", "/")
    file_list=[]
    for file in os.listdir(path_temp):
        if file.split('.')[1] in ['xlsx','csv','xls'] and file.split('.')[0].split('_')[0]==Cancer_type:
            file_list.append(file)

    file_target=sorted(file_list,key = lambda i:i.split('.')[0].split('_')[1],reverse=True)[0]
    path= join(path_temp, file_target).replace("\\", "/")

    selected_column = '病理诊断'

    # 读取文件时，首先验证文件格式是否符合要求
    error = Check_readfile(path, selected_column)
    st.write(error)

    if error == 'correct':
        start = time.time()
        ###########################################################################################
        # 文件切分对象
        DS = DataSpliter(selected_column=selected_column, path=path)
        # 输出文件切分结果字典
        DataSpliter_output_dict = DS.split()

        # 预处理类对象
        Prepro = PreProcessor(input_dict=DataSpliter_output_dict)
        # 输出预处理文本字典
        t_start = time.time()
        Preproces_output_dict = Prepro.process_ner()
        t_end = time.time()
        time_used = str(round(t_end - t_start, 2)) + ' second\n'
        st.write("preprocess time:{}".format(time_used))

        # 创建预测模型类对象
        model = ModelPredict(cancer_type=Cancer_type, preprocess_dict=Preproces_output_dict)
        # 输出预测后四元组list
        t_start = time.time()
        predict_tuple_list = model.predict_to_lists()

        t_end = time.time()
        time_used = str(round(t_end - t_start, 2)) + ' second\n'
        st.write("predict time:{}".format(time_used))

        use_dict = args.use_dict
        if not use_dict:
            NER, ratio = predict_tuple_list, 1
        else:
            # 字典生成的四元组list
            t_start = time.time()
            dict_extract_dict = main_dict_batch(input_dict=Preproces_output_dict, disease=Cancer_type)

            t_end = time.time()
            time_used = str(round(t_end - t_start, 2)) + ' second\n'
            st.write("main_dict_batch time:{}".format(time_used))

            # 预测和字典生成的四元组list合并
            t_start = time.time()
            Mg = Merger(trust='m', policy='a')
            NER, ratio = Mg.merge(dict_extract_dict, predict_tuple_list)
            t_end = time.time()
            time_used = str(round(t_end - t_start, 2)) + ' second\n'
            st.write("Merger time:{}".format(time_used))


        # 进行最后环节的封装
        raw = DataSpliter_output_dict['raw']
        No_NER = DataSpliter_output_dict['No_NER']
        st.write('开始封装处理！')
        t_start = time.time()

        ec = Encapsulator(by_cancer=args.by_cancer, redundancy=args.redundancy, translation_basic_update=args.translation_basic,
                      translation_diag_update=args.translation_diag, helpers_main=args.helpers_main, top_level=args.top_level,
                      method_window=args.method_window, helpers_rightward=args.helpers_rightward, nest_labels=args.nest_labels)
        encap_result = ec.encap(raw, No_NER, NER)
        t_end = time.time()
        time_used = str(round(t_end - t_start, 2)) + ' second\n'
        st.write("Encapsulate time:{}".format(time_used))
        st.write('完成封装处理！')

        use_normer = args.use_normer
        use_normer_reasoner = args.use_normer_reasoner

        if use_normer:
            if use_normer_reasoner:
                # 进入归一和推理环
                st.write('开始推理...')
                t_start = time.time()
                reasoner = Reasoner(Cancer_type)
                json_result = reasoner.reasoner_123(encap_result)
                t_end = time.time()
                time_used = str(round(t_end - t_start, 2)) + ' second\n'
                st.write("Reasoner time:{}".format(time_used))
                st.write('完成推理！')
            else:
                # 进入归一环节
                st.write('开始归一...')
                t_start = time.time()
                normer = Reasoner(Cancer_type)
                json_result = normer.normalization(encap_result)
                t_end = time.time()
                time_used = str(round(t_end - t_start, 2)) + ' second\n'
                st.write("Normer time:{}".format(time_used))
                st.write('完成归一!')

            end = time.time()
            st.write('共封装JSON对象{}个!'.format(len(json_result)))
            st.write('cost time (min):', round((end - start) / 60))

            file = json.dumps(json_result, indent=True, ensure_ascii=False).encode('UTF-8')
            st.write('saving to local file ‘/JSON_result/result.JSON’...')
            if os.path.exists('JSON_result'):
                pass
            else:
                os.mkdir('JSON_result')

            f = open('JSON_result/result.JSON', 'wb')
            f.write(file)
            f.close()
        else:
            end = time.time()
            st.write('共封装JSON对象{}个!'.format(len(encap_result)))
            st.write('cost time (min):', round((end - start) / 60))

            file = json.dumps(encap_result, indent=True, ensure_ascii=False).encode('UTF-8')
            st.write('saving to local file ‘/JSON_result/result.JSON’...')
            if os.path.exists('JSON_result'):
                pass
            else:
                os.mkdir('JSON_result')

            f = open('JSON_result/result.JSON', 'wb')
            f.write(file)
            f.close()
    else:
        st.write(error)

st.sidebar.markdown('结果下载')
if st.sidebar.button("Download JSON file"):
    with open(join(path_base, "JSON_result/result.JSON").replace("\\", "/"),'r',encoding='utf8')as fp:
        #json_data = json.load(fp)
        b64 = base64.b64encode(fp.read().encode()).decode()
        href = f'<a href="data:file/json;base64,{b64}">Download json File</a> (right-click and save as &lt;some_name&gt;.json)'
        st.markdown(href, unsafe_allow_html=True)


