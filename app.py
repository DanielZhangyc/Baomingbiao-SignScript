import streamlit as st
import requests
import datetime
import time as t
import json
import os
from collections import deque

def load_default_config():
    config_path = "PRIVATE_DEFAULT_INFO.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def submit_form(signup_time, token, bm_id, fields, log_container):
    try:
        while True:
            current_time = datetime.datetime.now()
            target_time = datetime.datetime.strptime(signup_time, "%Y-%m-%d %H:%M:%S")
            
            if current_time > target_time:
                t.sleep(0.1)
                code = 403
                while code != 200:
                    resp = requests.post(
                        "https://api.jingjia6.com/bm/bm",
                        headers={
                            "token": token,
                            "referer": "https://servicewechat.com/wx2b732132f727acb0/199/page-frame.html"
                        },
                        json={
                            **fields,
                            "bm_id": bm_id
                        },
                        verify=False
                    )
                    data = resp.json()
                    code = data['status']
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_container.info(f"[{current_time}] Response: {data}")
                    t.sleep(0.82)
                st.balloons()  # 添加气球效果
                return "提交成功！🎉"  # 添加表情符号增强视觉效果
            else:
                current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
                log_container.info(f"[{current_time_str}] 等待中...")
                t.sleep(0.1)
                
    except Exception as e:
        return f"发生错误: {str(e)}"

def clamp_time(hour, minute, second):
    """限制时间在有效范围内"""
    hour = max(0, min(hour, 23))
    minute = max(0, min(minute, 59))
    second = max(0, min(second, 59))
    return hour, minute, second

def main():
    # 使用markdown居中显示标题
    st.markdown("<h1 style='text-align: center;'>报名表提交</h1>", unsafe_allow_html=True)
    
    # 加载默认配置
    default_config = load_default_config()
    
    # 初始化session state
    if 'fields' not in st.session_state:
        st.session_state.fields = {'field.0': ''}

    # 初始化时间状态
    if 'time_values' not in st.session_state:
        current_time = datetime.datetime.now()
        st.session_state.time_values = {
            'hour': current_time.hour,
            'minute': current_time.minute,
            'second': current_time.second
        }

    # 使用两列布局
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("基本信息")
        
        # 日期选择
        today = datetime.datetime.now().date()
        tomorrow = today + datetime.timedelta(days=1)
        
        date_options = {
            "今天": today,
            "明天": tomorrow
        }
        selected_date_label = st.radio("选择日期", list(date_options.keys()))
        selected_date = date_options[selected_date_label]
        
        # 时间选择 - 使用水平布局并带有范围检查
        st.write("选择时间")
        time_cols = st.columns(3)  # 均匀分配三列
        
        # 使用on_change回调进行范围检查
        def on_time_change():
            h, m, s = clamp_time(
                st.session_state.hour_input,
                st.session_state.minute_input,
                st.session_state.second_input
            )
            st.session_state.time_values = {'hour': h, 'minute': m, 'second': s}
        
        hour = time_cols[0].number_input(
            "时", 
            value=st.session_state.time_values['hour'],
            key="hour_input",
            on_change=on_time_change
        )
        minute = time_cols[1].number_input(
            "分", 
            value=st.session_state.time_values['minute'],
            key="minute_input",
            on_change=on_time_change
        )
        second = time_cols[2].number_input(
            "秒", 
            value=st.session_state.time_values['second'],
            key="second_input",
            on_change=on_time_change
        )
        
        selected_time = datetime.time(
            st.session_state.time_values['hour'],
            st.session_state.time_values['minute'],
            st.session_state.time_values['second']
        )
        
        token = st.text_input("Token", value=default_config.get('token', ''))
        bm_id = st.text_input("BM ID")

    with col2:
        st.subheader("动态字段")
        # 添加和删除字段的按钮
        col3, col4 = st.columns(2)
        with col3:
            if st.button("添加字段"):
                next_index = len(st.session_state.fields)
                st.session_state.fields[f'field.{next_index}'] = ''
                
        with col4:
            if st.button("删除字段") and len(st.session_state.fields) > 1:
                last_key = f'field.{len(st.session_state.fields) - 1}'
                del st.session_state.fields[last_key]

        # 显示所有字段的输入框
        for field_key in sorted(st.session_state.fields.keys()):
            st.session_state.fields[field_key] = st.text_input(
                field_key,
                value=st.session_state.fields[field_key],
                key=f"input_{field_key}"
            )

    # 添加日志显示区域
    log_container = st.empty()

    if st.button("提交"):
        signup_datetime = datetime.datetime.combine(selected_date, selected_time).strftime("%Y-%m-%d %H:%M:%S")
        result = submit_form(
            signup_datetime,
            token,
            bm_id,
            st.session_state.fields,
            log_container
        )
        if "成功" in result:
            st.success(result)
        else:
            st.error(result)

if __name__ == "__main__":
    main()
