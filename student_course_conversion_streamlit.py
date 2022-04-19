#!/usr/bin/env python
# coding: utf-8

# In[19]:


import pandas as pd
import streamlit as st
from itertools import product
import os
import base64
from PIL import Image
import re

def file_downloader(filename, file_label='File'):
    with open(filename, 'rb') as f:
        data = f.read()


# In[30]:


st.title('学生コース登録用ファイル変換')
st.text('学生リストと講義リストを入力とし，\nmoodleのコースフォーマットリストを返します．')


# In[31]:


uploaded_file1 = st.file_uploader("学生のデータが入ったエクセルファイルを入力して下さい．↓↓ usernameの列が必要です", type="xlsx")
colname_grade = st.text_input('学年の情報が含まれている列名を以下に入力して下さい↓↓ 例: 備考')
uploaded_file2 = st.file_uploader("講義一覧のcsvファイルをアップロードして下さい．↓↓ category_path, shortnameの列が必要です．", type="csv")

# uploaded_file2のcategory_pathがstr(i)年生という判断
# どの行がcategory_pathかを判断し， shortname


# In[ ]:


if (uploaded_file1 is not None) & (uploaded_file2 is not None) &  (colname_grade is not None):
    dat_all = pd.read_excel(uploaded_file1)
    dat_course = pd.read_csv(uploaded_file2)
    st.success('データ変換を開始します．')
    st.text('学生データ：')
    st.dataframe(dat_all)
    st.text('講義データ：')
    st.dataframe(dat_course)
    
    unique_grade = dat_all[colname_grade].unique()
    
    cols = ['username', 'course1', 'role1']
    df = pd.DataFrame(index=[], columns=cols)
    
    for grade in unique_grade:
        #学生データの読み込み、mをつける。とりあえず今はテストデータを流しておく
        dat_stdent = dat_all[dat_all[colname_grade]==grade]
        i = int(re.sub(r"\D", "", grade))
        selected_stdent = dat_stdent.username #.str.upper()
        #selected_stdent = pd.Series(["m00000", "m11111", "m22222"])
        #カテゴリーパスがi+1年生のコースを取ってくる。
        select_courseTF = dat_course.category_path.str.contains(str(i) + "年生")
        selected_course = dat_course.loc[select_courseTF, :].shortname #fullnameではない
        #臨床実習に入っている2022-med-0
        selected_course=selected_course[~selected_course.str.contains("2022-med-0")]
        # i+1年生のコースと学生の総当たりでデータフフレームを作り、role1にstudent1を登録
        out_df = pd.DataFrame(list(product(selected_stdent, selected_course)), columns=cols[:2])
        out_df["role1"] ="student"
        df = pd.concat([df, out_df], axis=0)
        # 各学年ごとの登録用csvファイルを吐き出す
        csv = df.to_csv(index=False)
    
    st.success('変換終了')
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="student_class.csv">download</a>'
    st.markdown(f"変換データをダウンロードする： {href}", unsafe_allow_html=True)
else:
    st.warning("全てのデータを入力して下さい")

