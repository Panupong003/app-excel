import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Excel Diff Checker (Summary Mode)")

st.title("🔍 โปรแกรมวิเคราะห์ความแตกต่าง Excel (พร้อมตารางสรุป)")
st.write("อัปโหลดไฟล์ Excel เพื่อเปรียบเทียบ (ระบบจะเทียบโดยใช้คอลัมน์แรกเป็นหลัก)")

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
                st.divider()
                st.subheader(f"📊 ผลการเปรียบเทียบ: ไฟล์ที่ 1 🆚 ไฟล์ที่ {i+1}")
                
                df_base = dfs[0].set_index(key_col)
                df_target = dfs[i].set_index(key_col)

                # หาชื่อคอลัมน์ที่เหมือนกัน
                common_cols = df_base.columns.intersection(df_target.columns)
                
                # แยกประเภทข้อมูล
                added_idx = df_target.index.difference(df_base.index)
                dropped_idx = df_base.index.difference(df_target.index)
                common_idx = df_base.index.intersection(df_target.index)

                # วิเคราะห์รายการที่แก้ไข
                df_base_sub = df_base.loc[common_idx, common_cols].astype(str)
                df_target_sub = df_target.loc[common_idx, common_cols].astype(str)
                diff_mask = (df_target_sub != df_base_sub).any(axis=1)
                modified_df = df_target.loc[common_idx][diff_mask]

                # --- ส่วนที่เพิ่ม: ตารางสรุปภาพรวม ---
                summary_data = {
                    "ประเภทการเปลี่ยนแปลง": ["🆕 รายการใหม่ (Added)", "❌ รายการที่หายไป (Deleted)", "📝 รายการที่แก้ไข (Modified)"],
                    "จำนวน (รายการ)": [len(added_idx), len(dropped_idx), len(modified_df)]
                }
                summary_df = pd.DataFrame(summary_data)
                
                st.write("### 📌 ตารางสรุปภาพรวม")
                st.table(summary_df) # แสดงเป็นตารางแบบคงที่ ดูง่าย

                # ฟังก์ชันไฮไลต์สี
                def highlight_diff(data, df_compare, shared_columns):
                    attr = 'background-color: #ffcccc'
                    styles = pd.DataFrame('', index=data.index, columns=data.columns)
                    for col in shared_columns:
                        if col in data.columns and col in df_compare.columns:
                            diff_mask = data[col].astype(str) != df_compare.loc[data.index, col].astype(str)
                            styles[col] = diff_mask.map({True: attr, False: ''})
                    return styles

                # แสดงรายละเอียดใน Tabs
                t1, t2, t3 = st.tabs(["📝 รายละเอียดการแก้ไข", "🆕 รายการใหม่", "❌ รายการที่หายไป"])

                with t1:
                    if not modified_df.empty:
                        st.dataframe(modified_df.style.apply(lambda x: highlight_diff(modified_df, df_base, common_cols), axis=None), use_container_width=True)
                    else:
                        st.write("✅ ไม่มีการแก้ไขข้อมูลในรายการเดิม")

                with t2:
                    if not added_idx.empty:
                        st.dataframe(df_target.loc[added_idx], use_container_width=True)
                    else:
                        st.write("ไม่มีรายการเพิ่มใหม่")

                with t3:
                    if not dropped_idx.empty:
                        st.dataframe(df_base.loc[dropped_idx], use_container_width=True)
                    else:
                        st.write("ไม่มีรายการที่ถูกลบ")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
else:
    st.warning("⚠️ กรุณาอัปโหลดไฟล์ Excel อย่างน้อย 2 ไฟล์")
