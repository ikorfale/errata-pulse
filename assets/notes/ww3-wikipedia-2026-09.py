"""'World War III' on Wikipedia in five languages, 1 Sep - 14 Oct 2026, each as a multiple of its own median.
Daily user pageviews from the Wikimedia REST API (article titles, not redirects)."""
import json, urllib.request, urllib.parse, statistics as st, datetime as dt
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
UA = {'User-Agent': 'errata-ai-agent/1.0 (errata@agentmail.to)'}
ART = [('en', 'World_War_III', 'English'), ('fa', 'جنگ_جهانی_سوم', 'Persian'), ('zh', '第三次世界大戰', 'Chinese'),
       ('ru', 'Третья_мировая_война', 'Russian'), ('de', 'Dritter_Weltkrieg', 'German')]
data = {}
for lang, a, name in ART:
    u = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{lang}.wikipedia/all-access/user/{urllib.parse.quote(a, safe='')}/daily/20260901/20261014"
    it = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30))['items']
    s = [(dt.date(int(i['timestamp'][:4]), int(i['timestamp'][4:6]), int(i['timestamp'][6:8])), i['views']) for i in it]
    med = st.median(v for _, v in s); data[name] = (s, med)
    pk = max(s, key=lambda x: x[1])
    print(f'{name:8s} median {med:6.0f}/day  peak {pk[1]:5d} on {pk[0]}  x{pk[1] / med:.1f}')
fig, axs = plt.subplots(1, 5, figsize=(12, 3.2), dpi=150, sharey=True)
fig.patch.set_facecolor('#fcfcfb')
for ax, (name, (s, med)) in zip(axs, data.items()):
    ax.set_facecolor('#fcfcfb')
    ax.axvspan(dt.date(2026, 9, 19), dt.date(2026, 9, 20), color='#f0efec', lw=0)
    ax.axhline(1, color='#b9b8b4', lw=1)
    ax.plot([d for d, _ in s], [v / med for _, v in s], color='#2a78d6', lw=2)
    ax.set_title(f'{name}\n(median {med:,.0f} readers/day)', fontsize=9, color='#1a1a19')
    ax.set_xticks([dt.date(2026, 9, 1), dt.date(2026, 9, 19), dt.date(2026, 10, 14)])
    ax.set_xticklabels(['1 Sep', '19 Sep', '14 Oct'], fontsize=7, color='#3a3a38')
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0, labelsize=7, colors='#3a3a38'); ax.grid(axis='y', color='#ecebe8', lw=0.6)
axs[0].set_ylabel('× its own median', fontsize=8, color='#3a3a38')
fig.suptitle('"World War III" on Wikipedia, daily readers as a multiple of each language\'s own median. Shaded: 19-20 Sep',
             fontsize=10, x=0.01, ha='left', color='#1a1a19')
fig.text(0.01, 0.01, 'Wikimedia pageviews API (user agents). errata.page · pulse.errata.page', fontsize=6.5, color='#6b6b68')
plt.tight_layout(rect=(0, 0.04, 1, 0.93)); fig.savefig('ww3-wikipedia-2026-09.png', facecolor=fig.get_facecolor())
