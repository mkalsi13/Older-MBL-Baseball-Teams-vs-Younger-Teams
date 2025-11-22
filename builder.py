import pandas as pd

# ---- Load Baseball Databank CSVs (put this .py in same folder as the CSVs) ----
bat = pd.read_csv("Batting.csv")
master = pd.read_csv("Master.csv")
teams = pd.read_csv("Teams.csv")

# ---- Player age per season ----
master_sub = master[["playerID", "birthYear"]].dropna()
bat = bat.merge(master_sub, on="playerID", how="left")

bat["age"] = bat["yearID"] - bat["birthYear"]

# Plate appearances as weight (AB + BB + HBP + SF)
bat["PA"] = bat["AB"].fillna(0) + bat["BB"].fillna(0) + \
            bat["HBP"].fillna(0) + bat["SF"].fillna(0)

# Filter out rows with missing or weird ages
bat = bat[(bat["age"].notna()) & (bat["age"] >= 18) & (bat["age"] <= 45)]

# ---- Team-level weighted average age ----
# For each team-season, weight player ages by PA (so regulars count more)
def weighted_age(group):
    total_pa = group["PA"].sum()
    if total_pa == 0:
        return group["age"].mean()
    return (group["age"] * group["PA"]).sum() / total_pa

team_age = (
    bat.groupby(["yearID", "teamID"])
       .apply(weighted_age)
       .reset_index(name="avg_age")
)

# ---- Team performance: runs per game, win percentage ----
teams_sub = teams[["yearID", "teamID", "lgID", "franchID", "G", "R", "W", "L"]].dropna()

# Runs per game & win %
teams_sub["runs_per_game"] = teams_sub["R"] / teams_sub["G"]
teams_sub["win_pct"] = teams_sub["W"] / (teams_sub["W"] + teams_sub["L"])

# ---- Merge age with performance ----
team_age_perf = team_age.merge(
    teams_sub,
    on=["yearID", "teamID"],
    how="inner"
)

# Optional: focus on modern era only
team_age_perf = team_age_perf[team_age_perf["yearID"] >= 1970]

# Save clean CSV for D3
team_age_perf.to_csv("team_age_performance.csv", index=False)

print("Wrote team_age_performance.csv with columns:")
print(team_age_perf.columns)
