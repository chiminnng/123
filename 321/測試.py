import streamlit as st
import pandas as pd
import os
import base64

# ===== 頁面設定 =====
st.set_page_config(page_title="NBA 球隊正負值分析與勝率預測")
st.title("NBA 球隊正負值分析與勝率預測")
pd.options.display.float_format = '{:.2f}'.format

# ===== 資料夾路徑 =====
csv_dir = "程式專題"
logo_dir = "程式專題"

# ===== 讀取所有 CSV 檔案 =====
csv_files = [f for f in os.listdir(csv_dir) if f.endswith('_plus_minus.csv')]
if not csv_files:
    st.error("找不到 CSV 檔案，請確認資料夾內有資料")
    st.stop()

dfs = [pd.read_csv(os.path.join(csv_dir, f)) for f in csv_files]
df_all = pd.concat(dfs, ignore_index=True)

# ===== 球隊中英文 =====
team_name_mapping = {
    'Golden State Warriors': "勇士", 'Los Angeles Lakers': "湖人", 'Denver Nuggets': "金塊",
    'Los Angeles Clippers': "快艇", 'Phoenix Suns': "太陽", 'Sacramento Kings': "國王",
    'Minnesota Timberwolves': "灰狼", 'Oklahoma City Thunder': "雷霆", 'Portland Trail Blazers': "拓荒者",
    'Utah Jazz': "爵士", 'Dallas Mavericks': "獨行俠", 'Houston Rockets': "火箭",
    'Memphis Grizzlies': "灰熊", 'New Orleans Pelicans': "鵜鶘", 'San Antonio Spurs': "馬刺",
    'New York Knicks': "尼克", 'Boston Celtics': "賽爾提克", 'Brooklyn Nets': "籃網",
    'Philadelphia 76ers': "76人", 'Toronto Raptors': "暴龍", 'Chicago Bulls': "公牛",
    'Cleveland Cavaliers': "騎士", 'Detroit Pistons': "活塞", 'Indiana Pacers': "溜馬",
    'Milwaukee Bucks': "公鹿", 'Atlanta Hawks': "老鷹", 'Charlotte Hornets': "黃蜂",
    'Miami Heat': "熱火", 'Orlando Magic': "魔術", 'Washington Wizards': "巫師"
}

all_teams = sorted(df_all['球隊'].unique())
chinese_team_to_en = {v: k for k, v in team_name_mapping.items()}
chinese_team_list = [team_name_mapping.get(t, t) for t in all_teams]

# ===== 選擇主場與客場 =====
col1, col2 = st.columns(2)
with col1:
    chinese_team_name1 = st.selectbox("請選擇 **主場** 球隊：", chinese_team_list)
with col2:
    chinese_team_name2 = st.selectbox("請選擇 **客場** 球隊：", chinese_team_list)

team_name1 = chinese_team_to_en.get(chinese_team_name1, chinese_team_name1)
team_name2 = chinese_team_to_en.get(chinese_team_name2, chinese_team_name2)

def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def show_team_logo(team_name):
    exts = ['.png', '.jpg']
    for ext in exts:
        logo_path = os.path.join(logo_dir, f"{team_name}{ext}")
        if os.path.exists(logo_path):
            img_base64 = get_image_base64(logo_path)
            zh_name = team_name_mapping.get(team_name, team_name)
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <img src="data:image/png;base64,{img_base64}" width="150"><br>
                    <p style="font-size:16px; color: gray;">{zh_name}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            return
    st.write(f"找不到 {team_name} 隊徽")

# ===== 計算球隊平均正負值 =====
def get_team_stats(team_name):
    team_df = df_all[df_all['球隊'] == team_name]
    avg_pm = team_df['平均正負值'].mean()
    return team_df, avg_pm

if team_name1 and team_name2:

    if team_name1 == team_name2:
        st.warning("請選擇不同的兩支球隊")
        st.stop()

    team1_df, team1_avg = get_team_stats(team_name1)
    team2_df, team2_avg = get_team_stats(team_name2)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"{team_name_mapping.get(team_name1, team_name1)} 球員平均正負值")
        show_team_logo(team_name1)
        st.dataframe(team1_df[['球員', '平均正負值']].set_index('球員'))
        st.write(f"**全隊平均正負值：** `{team1_avg:.2f}`")

    with col2:
        st.subheader(f"{team_name_mapping.get(team_name2, team_name2)} 球員平均正負值")
        show_team_logo(team_name2)
        st.dataframe(team2_df[['球員', '平均正負值']].set_index('球員'))
        st.write(f"**全隊平均正負值：** `{team2_avg:.2f}`")

    # ===== 勝率計算 =====
    def get_adjusted_win_rate(pm1, pm2):
        diff = abs(pm1 - pm2)
        if diff <= 5:
            bonus = 0.10
        elif diff <= 8:
            bonus = 0.15
        elif diff <= 10:
            bonus = 0.20
        else:
            bonus = 0.30

        base_home = 0.6
        base_away = 0.4

        if pm1 > pm2:
            home_final = base_home + bonus
            away_final = base_away - bonus
        elif pm1 < pm2:
            home_final = base_home - bonus
            away_final = base_away + bonus
        else:
            home_final = base_home
            away_final = base_away

        total = home_final + away_final
        return home_final / total, away_final / total

    home_win_rate, away_win_rate = get_adjusted_win_rate(team1_avg, team2_avg)

    # ===== 顯示預測結果 =====
    st.subheader("勝率預測結果")
    st.write(f"**{team_name_mapping.get(team_name1, team_name1)}（主場）預測勝率：** `{home_win_rate:.2%}`")
    st.write(f"**{team_name_mapping.get(team_name2, team_name2)}（客場）預測勝率：** `{away_win_rate:.2%}`")

