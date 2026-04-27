import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Excel Diff Checker (Fixed)")

st.title("🔍 โปรแกรมวิเคราะห์ความแตกต่าง Excel (Version: Flexible)")
st.write("อัปโหลดไฟล์ Excel เพื่อเปรียบเทียบ (ระบบจะเทียบเฉพาะคอลัมน์ที่มีชื่อตรงกัน)")

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
            # อ่านไฟล์ทั้งหมด
            dfs = [pd.read_excel(f) for f in uploaded_files]
            
            # ใช้คอลัมน์แรกเป็น ID หลัก
            key_col = dfs[0].columns[0]
            st.success(f"ใช้คอลัมน์ '{key_col}' เป็นตัวหลักในการเปรียบเทียบ")

            for i in range(1, len(dfs)):
                st.divider()
                st.subheader(f"📊 ผลการเปรียบเทียบ: ไฟล์ที่ 1 🆚 ไฟล์ที่ {i+1}")
                
                # เตรียม DataFrame โดยเอาคอลัมน์แรกเป็น Index
                df_base = dfs[0].set_index(key_col)
                df_target = dfs[i].set_index(key_col)

                # --- ส่วนแก้ไข: หาคอลัมน์ที่มีร่วมกันเท่านั้น ---
                common_cols = df_base.columns.intersection(df_target.index if False else df_target.columns)
                
                # กรองให้เหลือแต่แถวที่มีทั้งสองฝั่ง (Common Rows)
                added = df_target.index.difference(df_base.index)
                dropped = df_base.index.difference(df_target.index)
                common_rows = df_base.index.intersection(df_target.index)

                # ฟังก์ชันไฮไลต์สี (ปรับปรุงให้รองรับข้อมูลต่างโครงสร้าง)
                def highlight_diff(data, df_compare, shared_columns):
                    attr = 'background-color: #ffcccc'
                    styles = pd.DataFrame('', index=data.index, columns=data.columns)
                    for col in shared_columns:
                        if col in data.columns and col in df_compare.columns:
                            # เทียบค่าโดยแปลงเป็น String เพื่อป้องกัน Error จากชนิดข้อมูลต่างกัน
                            diff_mask = data[col].astype(str) != df_compare.loc[data.index, col].astype(str)
                            styles[col] = diff_mask.map({True: attr, False: ''})
                    return styles

                t1, t2, t3 = st.tabs(["ค่าที่เปลี่ยนไป", "ข้อมูลใหม่", "ข้อมูลที่หายไป"])

                with t1:
                    if not common_rows.empty:
                        # เทียบเฉพาะคอลัมน์ที่มีชื่อเหมือนกัน
                        df_base_sub = df_base.loc[common_rows, common_cols]
                        df_target_sub = df_target.loc[common_rows, common_cols]
                        
                        # หาแถวที่มีความต่างอย่างน้อย 1 คอลัมน์
                        diff_mask = (df_target_sub.astype(str) != df_base_sub.astype(str)).any(axis=1)
                        diff_df = df_target.loc[common_rows][diff_mask]
                        
                        if not diff_df.empty:
                            st.write(f"พบ {len(diff_df)} แถวที่มีการแก้ไขข้อมูล")
                            st.dataframe(diff_df.style.apply(lambda x: highlight_diff(diff_df, df_base, common_cols), axis=None), use_container_width=True)
                        else:
                            st.write("✅ ข้อมูลในคอลัมน์ที่เหมือนกันตรงกันทุกรายการ")
                    else:
                        st.write("❓ ไม่พบข้อมูลที่มี ID ตรงกันเลย")

                with t2:
                    st.write(f"พบข้อมูลใหม่ {len(added)} รายการ (ที่มีในไฟล์ {i+1} แต่ไม่มีในไฟล์ 1)")
                    st.dataframe(df_target.loc[added], use_container_width=True)

                with t3:
                    st.write(f"พบข้อมูลที่หายไป {len(dropped)} รายการ (ที่มีในไฟล์ 1 แต่ไม่มีในไฟล์ {i+1})")
                    st.dataframe(df_base.loc[dropped], use_container_width=True)

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดทางเทคนิค: {e}")
            st.info("คำแนะนำ: ตรวจสอบว่าคอลัมน์แรกของทุกไฟล์มีชื่อเหมือนกันเป๊ะๆ (รวมถึงช่องว่าง)")
else:
    st.warning("⚠️ กรุณาอัปโหลดไฟล์ Excel อย่างน้อย 2 ไฟล์")
