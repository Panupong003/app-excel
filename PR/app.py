import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Excel Multi-File Diff Checker")

st.title("🔍 โปรแกรมวิเคราะห์ความแตกต่าง Excel (4 ไฟล์)")
st.write("อัปโหลดไฟล์ Excel เพื่อเปรียบเทียบข้อมูล (จะใช้ไฟล์แรกเป็นฐานหลักในการเปรียบเทียบ)")

# 1. ส่วนการนำเข้าไฟล์
col1, col2, col3, col4 = st.columns(4)
files = []
with col1: files.append(st.file_uploader("ไฟล์ที่ 1 (ฐานหลัก)", type=['xlsx']))
with col2: files.append(st.file_uploader("ไฟล์ที่ 2", type=['xlsx']))
with col3: files.append(st.file_uploader("ไฟล์ที่ 3", type=['xlsx']))
with col4: files.append(st.file_uploader("ไฟล์ที่ 4", type=['xlsx']))

uploaded_files = [f for f in files if f is not None]

if len(uploaded_files) >= 2:
    st.info(f"ขณะนี้อัปโหลดมาทั้งหมด {len(uploaded_files)} ไฟล์")
    
    if st.button('🚀 เริ่มวิเคราะห์ข้อมูล', use_container_width=True):
        try:
            dfs = [pd.read_excel(f) for f in uploaded_files]
            key_col = dfs[0].columns[0]
            st.success(f"ใช้คอลัมน์ '{key_col}' เป็นตัวหลักในการเปรียบเทียบ")

            for i in range(1, len(dfs)):
                # แก้ไขบรรทัดเจ้าปัญหาตรงนี้ครับ
                st.divider() 
                st.subheader(f"📊 ผลการเปรียบเทียบ: ไฟล์ที่ 1 🆚 ไฟล์ที่ {i+1}")
                
                df_base = dfs[0].set_index(key_col)
                df_target = dfs[i].set_index(key_col)

                added = df_target.index.difference(df_base.index)
                dropped = df_base.index.difference(df_target.index)
                common = df_base.index.intersection(df_target.index)

                def highlight_diff(data, df_compare):
                    attr = 'background-color: #ffcccc'
                    other = data.copy()
                    for col in data.columns:
                        if col in df_compare.columns:
                            # ตรวจสอบค่าที่ต่างกัน
                            diff_mask = data[col].astype(str) != df_compare.loc[data.index, col].astype(str)
                            other[col] = diff_mask.map({True: attr, False: ''})
                        else:
                            other[col] = ''
                    return other

                t1, t2, t3 = st.tabs([f"ค่าที่เปลี่ยนไป", "ข้อมูลใหม่", "ข้อมูลที่หายไป"])

                with t1:
                    mask = (df_target.loc[common].astype(str) != df_base.loc[common].astype(str)).any(axis=1)
                    diff_df = df_target.loc[common][mask]
                    if not diff_df.empty:
                        st.dataframe(diff_df.style.apply(highlight_diff, df_compare=df_base, axis=None), use_container_width=True)
                    else:
                        st.write("✅ ข้อมูลตรงกันทุกรายการ")

                with t2:
                    st.write(f"พบข้อมูลใหม่ {len(added)} รายการ")
                    st.dataframe(df_target.loc[added], use_container_width=True)

                with t3:
                    st.write(f"พบข้อมูลที่หายไป {len(dropped)} รายการ")
                    st.dataframe(df_base.loc[dropped], use_container_width=True)

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
else:
    st.warning("⚠️ กรุณาอัปโหลดไฟล์ Excel อย่างน้อย 2 ไฟล์")