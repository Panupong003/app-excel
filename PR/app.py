import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Excel Diff Checker - Full Report")

st.title("🔍 รายงานวิเคราะห์ความแตกต่าง Excel (แบบละเอียด)")
st.write("ระบบจะเปรียบเทียบไฟล์ที่ 2, 3, 4 เทียบกับไฟล์ที่ 1 (ฐานหลัก)")

# 1. ส่วนการนำเข้าไฟล์
col1, col2, col3, col4 = st.columns(4)
files = []
with col1: files.append(st.file_uploader("ไฟล์ที่ 1 (ฐานหลัก)", type=['xlsx']))
with col2: files.append(st.file_uploader("ไฟล์ที่ 2", type=['xlsx']))
with col3: files.append(st.file_uploader("ไฟล์ที่ 3", type=['xlsx']))
with col4: files.append(st.file_uploader("ไฟล์ที่ 4", type=['xlsx']))

uploaded_files = [f for f in files if f is not None]

if len(uploaded_files) >= 2:
    if st.button('🚀 เริ่มวิเคราะห์และแสดงผลทั้งหมด', use_container_width=True):
        try:
            dfs = [pd.read_excel(f) for f in uploaded_files]
            key_col = dfs[0].columns[0]
            st.success(f"✅ ใช้คอลัมน์แรก '{key_col}' เป็นตัวเชื่อมข้อมูล")

            for i in range(1, len(dfs)):
                st.write("")
                st.write("")
                st.header(f"📂 การเปรียบเทียบ: ไฟล์ที่ 1 🆚 ไฟล์ที่ {i+1}")
                st.divider()
                
                df_base = dfs[0].set_index(key_col)
                df_target = dfs[i].set_index(key_col)

                # หาข้อมูลร่วมและที่ต่าง
                common_cols = df_base.columns.intersection(df_target.columns)
                added_idx = df_target.index.difference(df_base.index)
                dropped_idx = df_base.index.difference(df_target.index)
                common_idx = df_base.index.intersection(df_target.index)

                # วิเคราะห์รายการที่แก้ไข
                df_base_sub = df_base.loc[common_idx, common_cols].astype(str)
                df_target_sub = df_target.loc[common_idx, common_cols].astype(str)
                diff_mask = (df_target_sub != df_base_sub).any(axis=1)
                modified_df = df_target.loc[common_idx][diff_mask]

                # --- ส่วนที่ 1: ตารางสรุปภาพรวม ---
                st.subheader("📌 1. สรุปจำนวนการเปลี่ยนแปลง")
                summary_df = pd.DataFrame({
                    "สถานะ": ["📝 แก้ไขข้อมูล (Modified)", "🆕 เพิ่มเข้ามา (Added)", "❌ ถูกลบออก (Deleted)"],
                    "จำนวน (รายการ)": [len(modified_df), len(added_idx), len(dropped_idx)]
                })
                st.table(summary_df)

                # ฟังก์ชันไฮไลต์สี
                def highlight_diff(data, df_compare, shared_columns):
                    attr = 'background-color: #ffcccc'
                    styles = pd.DataFrame('', index=data.index, columns=data.columns)
                    for col in shared_columns:
                        if col in data.columns and col in df_compare.columns:
                            diff_mask = data[col].astype(str) != df_compare.loc[data.index, col].astype(str)
                            styles[col] = diff_mask.map({True: attr, False: ''})
                    return styles

                # --- ส่วนที่ 2: แสดงตารางรายละเอียดเรียงต่อกัน ---
                
                # 2.1 ตารางแก้ไข
                st.subheader("📝 2. รายละเอียดข้อมูลที่ 'แก้ไข'")
                if not modified_df.empty:
                    st.write("*(ช่องสีแดงคือจุดที่ข้อมูลเปลี่ยนไปจากไฟล์ที่ 1)*")
                    st.dataframe(modified_df.style.apply(lambda x: highlight_diff(modified_df, df_base, common_cols), axis=None), use_container_width=True)
                else:
                    st.info("ไม่มีข้อมูลที่ถูกแก้ไข")

                # 2.2 ตารางข้อมูลใหม่
                st.subheader("🆕 3. รายละเอียดข้อมูลที่ 'เพิ่มเข้ามา'")
                if not added_idx.empty:
                    st.dataframe(df_target.loc[added_idx], use_container_width=True)
                else:
                    st.info("ไม่มีข้อมูลเพิ่มใหม่")

                # 2.3 ตารางข้อมูลที่หายไป
                st.subheader("❌ 4. รายละเอียดข้อมูลที่ 'ถูกลบออก'")
                if not dropped_idx.empty:
                    st.dataframe(df_base.loc[dropped_idx], use_container_width=True)
                else:
                    st.info("ไม่มีข้อมูลที่ถูกลบ")

                st.write("---") # เส้นคั่นจบการเทียบ 1 คู่

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
else:
    st.warning("⚠️ กรุณาอัปโหลดไฟล์ Excel อย่างน้อย 2 ไฟล์เพื่อเริ่มการวิเคราะห์")
