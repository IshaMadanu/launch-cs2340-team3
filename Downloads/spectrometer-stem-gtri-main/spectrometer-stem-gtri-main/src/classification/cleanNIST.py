import pandas as pd
import re



def clean_number(x):
   if pd.isna(x):
       return None
   x = str(x)
   x = x.replace('="', '').replace('"', '')
   m = re.search(r'[-+]?\d*\.?\d+(?:e[-+]?\d+)?', x)
   return float(m.group()) if m else None


df = pd.read_csv("lines1.txt") 


df["obs_wl_air(nm)"] = df["obs_wl_air(nm)"].apply(clean_number)
df["intens"] = df["intens"].apply(clean_number)


df = df.dropna(subset=["obs_wl_air(nm)", "intens"])


df["species"] = df["element"] + "_" + df["sp_num"].astype(str)


lines = (
   df.groupby(["species", "obs_wl_air(nm)"])["intens"]
     .sum()
     .reset_index()
)


lines["intens"] = (
   lines.groupby("species")["intens"]
        .transform(lambda x: x / x.max())
)


lines.to_csv("cleaned_lines.csv", index=False)


print("Saved cleaned_lines.csv")
