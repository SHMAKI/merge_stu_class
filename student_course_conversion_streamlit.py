#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import streamlit as st
from itertools import product
import os
import base64
from PIL import Image
import re

# def file_downloader(filename, file_label='File'):
#     with open(filename, 'rb') as f:
#         data = f.read()
        
def try_read_df(f):
    if f.endswith("xlsx"):
        try:
            return pd.read_excel(f)
        except UnicodeDecodeError:
            return pd.read_excel(f, encoding="CP932")
#         except Exception as err:
#             print(f"Unexpected {err=}, {type(err)=}")
    
    elif f.endswith("csv"):
        try:
            return pd.read_csv(f)
        except UnicodeDecodeError:
            return pd.read_csv(f, encoding="CP932")
#         except Exception as err:
#             print(f"Unexpected {err=}, {type(err)=}")
    
    else:
        print("This file is not xlsx or csv")

st.title('学生コース登録用ファイル変換')
st.text('学生リストと講義リストを入力とし，\nmoodleのコースフォーマットリストを返します．\n姓名メールアドレス等個人情報が含まれるデータは入力しないで下さい．')

uploaded_file1 = st.file_uploader("学生のデータが入ったファイルを入力して下さい．", type=["xlsx", "csv"])

if uploaded_file1 is not None:

    dat_all = try_read_df(uploaded_file1)
    st.text("続いて，usernameと学年の列を選択して下さい．")
    
    colname_username = st.selectbox(
    'usernameの列を選択:',
    dat_all.columns.tolist())
    
    colname_grade = st.selectbox(
    '学年の列を選択:',
    dat_all.columns.tolist())
    
    st.text('学生のデータ：')
    st.dataframe(dat_all)
    
uploaded_file2 = st.file_uploader("講義一覧のファイルをアップロードして下さい．", type=["xlsx", "csv"])

if uploaded_file2 is not None:

    dat_course = try_read_df(uploaded_file2)
    st.text("続いて，category_path, shortnameの列を選択して下さい")
    
    colname_shortname = st.selectbox(
    'shortnameの列を選択：',
    dat_course.columns.tolist())
    
    colname_category_path = st.selectbox(
    'category_pathの列を選択：',
    dat_course.columns.tolist())
    
    st.text('講義のデータ：')
    st.dataframe(dat_course)


if st.button('ファイル変換実行'):
    if (uploaded_file1 is not None) & (uploaded_file2 is not None):
        st.success('データ変換を開始します．')
        unique_grade = dat_all[colname_grade].unique()

        cols = ['username', 'course1', 'role1']
        df = pd.DataFrame(index=[], columns=cols)

        for grade in unique_grade:
            #学生データの読み込み、mをつける。とりあえず今はテストデータを流しておく
            dat_stdent = dat_all[dat_all[colname_grade]==grade]
            i = int(re.sub(r"\D", "", grade))
            selected_stdent = dat_stdent[colname_username] 
            #カテゴリーパスがi+1年生のコースを取ってくる。
            select_courseTF = dat_course[colname_category_path].str.contains(str(i) + "年生")
            #selected_course = dat_course.loc[select_courseTF, :].shortname #fullnameではない
            selected_course = dat_course.loc[select_courseTF, colname_shortname]

            #臨床実習に入っている2022-med-0
            selected_course=selected_course[~selected_course.str.contains("2022-med-0")]
            # i+1年生のコースと学生の総当たりでデータフフレームを作り、role1にstudent1を登録
            out_df = pd.DataFrame(list(product(selected_stdent, selected_course)), columns=cols[:2])
            out_df["role1"] ="student"
            df = pd.concat([df, out_df], axis=0)
            # 各学年ごとの登録用csvファイルを吐き出す
            csv = df.to_csv(index=False)

        st.success('変換終了')
        st.download_button(label='変換ファイルのダウンロード 📥',
                                data=csv,
                                file_name= 'student_class.csv')
#         b64 = base64.b64encode(csv.encode()).decode()
#         href = f'<a href="data:application/octet-stream;base64,{b64}" download="student_class.csv">download</a>'
#         st.markdown(f"変換データをダウンロードする： {href}", unsafe_allow_html=True)
    else:
        st.warning("全てのデータを入力して下さい")
