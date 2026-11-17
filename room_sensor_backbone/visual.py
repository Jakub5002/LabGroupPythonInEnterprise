import json
from datetime import datetime
import matplotlib.pyplot as plt

snap = json.load(open("latest.json", encoding="utf-8"))
s, pts, sm = snap["series"], snap["points"], snap["summary"]

if not pts:
    print("Brak punktów: nic do narysowania.")
else:
    t = [datetime.fromisoformat(p["time"]) for p in pts]
    v = [p["value"] for p in pts]

    fig, ax = plt.subplots()
    ax.plot(t, v, marker="o", markersize=3, linewidth=1)
    if sm["mean"] is not None:
        ax.axhline(sm["mean"], linestyle="--", label="średnia")
    if sm["sample_sd"] is not None and sm["mean"] is not None:
        ax.axhspan(sm["mean"] - sm["sample_sd"], sm["mean"] + sm["sample_sd"],
                   alpha=0.15, label="±1 SD")
    ax.set_xlabel("czas (UTC)")
    ax.set_ylabel(f"{s['metric']} [{s['unit']}]")
    ax.set_title(f"{s['room']} / {s['sensor_id']}")
    ax.legend()
    fig.autofmt_xdate()
    plt.show()