"""
Gold Dealer - Read Only Public Website
Deploy on Railway
"""
from flask import Flask, render_template_string, request, redirect, session, Response
import os, mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = "gd_web_2025"

def get_cloud_db():
    return mysql.connector.connect(
        host=os.environ.get("MYSQLHOST","tramway.proxy.rlwy.net"),
        port=int(os.environ.get("MYSQLPORT","20602")),
        user=os.environ.get("MYSQLUSER","root"),
        password=os.environ.get("MYSQLPASSWORD","psTwPMlPTtIhaxgsQeFkFxIziyCMIucs"),
        database=os.environ.get("MYSQLDATABASE","railway"),
        charset="utf8mb4"
    )

class Row(dict):
    def __getitem__(self,k):
        if isinstance(k,int): return list(self.values())[k]
        return super().__getitem__(k)

def query(sql, params=()):
    try:
        conn = get_cloud_db(); cur = conn.cursor()
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        rows = [Row(zip(cols,r)) for r in cur.fetchall()]
        conn.close(); return rows
    except: return []

def query_one(sql, params=()):
    r = query(sql, params); return r[0] if r else None

BASE = """<!DOCTYPE html>
<html><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gold Dealer System</title>
<style>
:root{--gold:#C9A84C;--gold2:#E8C97A;--dark:#0a0a0a;--dark2:#111;--dark3:#1a1a1a;
--green:#27ae60;--red:#e74c3c;--text:#f0ead6;--muted:#888}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--dark);color:var(--text);font-family:-apple-system,'Segoe UI',sans-serif}
a{color:var(--gold);text-decoration:none}
.topbar{background:linear-gradient(135deg,#1a1200,#2a1e00);border-bottom:2px solid var(--gold);
padding:12px 20px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100}
.topbar h1{font-size:17px;color:var(--gold);font-weight:700}
.topbar .sub{font-size:11px;color:var(--muted)}
.logout{background:rgba(231,76,60,.15);color:var(--red);border:1px solid var(--red);
padding:6px 14px;border-radius:6px;font-size:12px;cursor:pointer}
.nav{display:flex;gap:6px;padding:10px 16px;overflow-x:auto;background:#111;
border-bottom:1px solid #222;scrollbar-width:none}
.nav a{white-space:nowrap;padding:7px 16px;border-radius:20px;font-size:13px;
background:#1a1a1a;color:var(--muted);border:1px solid #333}
.nav a.active{background:linear-gradient(135deg,var(--gold),var(--gold2));color:#000;font-weight:700}
.wrap{padding:16px;max-width:1100px;margin:0 auto}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:16px}
.stat{background:#161616;border:1px solid #2a2a2a;border-radius:12px;padding:16px;text-align:center}
.stat .val{font-size:22px;font-weight:700;margin-bottom:4px}
.stat .lbl{font-size:11px;color:var(--muted)}
.gold-c{color:var(--gold)}.green-c{color:var(--green)}.red-c{color:var(--red)}.muted{color:var(--muted)}
.card{background:#111;border:1px solid #222;border-radius:12px;margin-bottom:14px;overflow:hidden}
.card-head{padding:12px 16px;border-bottom:1px solid #222;font-size:14px;color:var(--gold);font-weight:600}
.scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:12px}
th{background:#1a1a1a;color:var(--gold);padding:9px 12px;text-align:left;white-space:nowrap;border-bottom:1px solid #333}
td{padding:8px 12px;border-bottom:1px solid #1a1a1a;vertical-align:middle}
tr:last-child td{border-bottom:none}
.badge{display:inline-block;padding:3px 9px;border-radius=10px;font-size:11px;font-weight:600;border-radius:8px}
.bg{background:rgba(39,174,96,.15);color:var(--green)}
.br{background:rgba(231,76,60,.15);color:var(--red)}
.bgold{background:rgba(201,168,76,.15);color:var(--gold)}
.canc{opacity:.4;text-decoration:line-through}
.login-wrap{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.login-box{background:#111;border:1px solid var(--gold);border-radius:16px;padding:28px 24px;width:100%;max-width:360px}
.login-box h1{color:var(--gold);text-align:center;margin-bottom:20px;font-size:22px}
.form-g{margin-bottom:12px}
.form-g label{display:block;font-size:12px;color:var(--gold);margin-bottom:5px;font-weight:600}
.form-g input{width:100%;background:#1a1a1a;border:1px solid #444;color:var(--text);
padding:10px 12px;border-radius:8px;font-size:14px;outline:none}
.form-g input:focus{border-color:var(--gold)}
.btn{width:100%;padding:11px;background:linear-gradient(135deg,var(--gold),var(--gold2));
color:#000;border:none;border-radius:8px;font-size:15px;font-weight:700;cursor:pointer;margin-top:8px}
.err{color:var(--red);font-size:13px;text-align:center;margin-top:8px}
.sync{font-size:11px;color:var(--muted);text-align:right;padding:4px 16px}
</style></head><body>
{% if user %}
<div class="topbar">
  <div><h1>✦ GOLD DEALER SYSTEM</h1><div class="sub">{{user.upper()}} &nbsp;|&nbsp; Read Only View</div></div>
  <form method="post" action="/logout"><button class="logout">Logout</button></form>
</div>
<nav class="nav">
  <a href="/dashboard" class="{{'active' if page=='dashboard' else ''}}">📊 Dashboard</a>
  <a href="/balance" class="{{'active' if page=='balance' else ''}}">⚖ Balance</a>
  <a href="/ledger" class="{{'active' if page=='ledger' else ''}}">📋 Ledger</a>
  <a href="/receipts" class="{{'active' if page=='receipts' else ''}}">⬇ Receipts</a>
  <a href="/issues" class="{{'active' if page=='issues' else ''}}">⬆ Issues</a>
  <a href="/dealers" class="{{'active' if page=='dealers' else ''}}">🏪 Dealers</a>
  <a href="/products" class="{{'active' if page=='products' else ''}}">📦 Products</a>
  <a href="/schedule" class="{{'active' if page=='schedule' else ''}}">🔔 Schedule</a>
</nav>
{% endif %}
{{content}}
</body></html>"""

def render(page, content, user=None):
    html = render_template_string(BASE, page=page, content=content, user=user or session.get("user",""))
    return Response(html, mimetype="text/html")

def login_req(f):
    from functools import wraps
    @wraps(f)
    def d(*a,**k):
        if not session.get("user"): return redirect("/")
        return f(*a,**k)
    return d

@app.route("/", methods=["GET","POST"])
def login():
    err=""
    if request.method=="POST":
        u=request.form.get("username","").strip()
        p=request.form.get("password","").strip()
        import hashlib
        hp=hashlib.sha256(p.encode()).hexdigest()
        row=query_one("SELECT * FROM users WHERE username=%s AND password=%s",(u,hp))
        if row: session["user"]=u; session["role"]=row["role"]; return redirect("/dashboard")
        else: err="Invalid credentials"
    html=f"""<div class="login-wrap"><div class="login-box">
    <h1>✦ Gold Dealer</h1>
    <form method="post">
    <div class="form-g"><label>USERNAME</label><input name="username" autocomplete="off"></div>
    <div class="form-g"><label>PASSWORD</label><input type="password" name="password"></div>
    <button class="btn">Login</button>
    </form>
    <div class="err">{err}</div>
    </div></div>"""
    return render("login", html, user="")

@app.route("/logout", methods=["POST"])
def logout():
    session.clear(); return redirect("/")

@app.route("/dashboard")
@login_req
def dashboard():
    today=str(date.today())
    tr=query_one("SELECT COUNT(DISTINCT bill_no) as c FROM receipts WHERE bill_date=%s AND cancelled=0",(today,))
    ti=query_one("SELECT COUNT(DISTINCT bill_no) as c FROM issues WHERE bill_date=%s AND cancelled=0",(today,))
    tg=query_one("SELECT COALESCE(SUM(pure_wt),0) as t FROM receipts WHERE bill_date=%s AND cancelled=0",(today,))
    sync=query_one("SELECT synced_at FROM last_sync WHERE id=1")
    dealers=query("SELECT id,dealer_name,dealer_code FROM dealers WHERE active=1 ORDER BY dealer_code")
    bal_rows=""
    for d in dealers[:8]:
        gr=query_one("SELECT COALESCE(SUM(r.pure_wt),0) as t FROM receipts r JOIN products p ON r.product_id=p.id WHERE r.dealer_id=%s AND r.cancelled=0 AND p.metal='Gold'",(d["id"],))
        gi=query_one("SELECT COALESCE(SUM(i.pure_wt),0) as t FROM issues i JOIN products p ON i.product_id=p.id WHERE i.dealer_id=%s AND i.cancelled=0 AND p.metal='Gold'",(d["id"],))
        g=round((gr["t"] if gr else 0)-(gi["t"] if gi else 0),3)
        color="green-c" if g>=0 else "red-c"
        bal_rows+=f"<tr><td>{d['dealer_code']}</td><td>{d['dealer_name']}</td><td class='{color}'>{g:,.3f}g</td></tr>"
    sync_txt=f"Last synced: {sync['synced_at']}" if sync else "Not synced yet"
    html=f"""<div class="wrap">
    <div class="sync">{sync_txt}</div>
    <div class="stats">
      <div class="stat"><div class="val gold-c">{tr['c'] if tr else 0}</div><div class="lbl">Today's Receipts</div></div>
      <div class="stat"><div class="val red-c">{ti['c'] if ti else 0}</div><div class="lbl">Today's Issues</div></div>
      <div class="stat"><div class="val green-c">{tg['t']:.3f}g</div><div class="lbl">Today Pure Received</div></div>
      <div class="stat"><div class="val gold-c">{len(dealers)}</div><div class="lbl">Active Dealers</div></div>
    </div>
    <div class="card"><div class="card-head">⚖ Dealer Gold Balances (Top 8)</div>
    <div class="scroll"><table><tr><th>Code</th><th>Dealer</th><th>Gold Balance</th></tr>{bal_rows}</table></div>
    </div></div>"""
    return render("dashboard", html)

@app.route("/balance")
@login_req
def balance():
    dealers=query("SELECT * FROM dealers WHERE active=1 ORDER BY dealer_code")
    rows=""; tg=ts=0
    for d in dealers:
        gr=query_one("SELECT COALESCE(SUM(r.pure_wt),0) as t FROM receipts r JOIN products p ON r.product_id=p.id WHERE r.dealer_id=%s AND r.cancelled=0 AND p.metal='Gold'",(d["id"],))
        gi=query_one("SELECT COALESCE(SUM(i.pure_wt),0) as t FROM issues i JOIN products p ON i.product_id=p.id WHERE i.dealer_id=%s AND i.cancelled=0 AND p.metal='Gold'",(d["id"],))
        sr=query_one("SELECT COALESCE(SUM(r.pure_wt),0) as t FROM receipts r JOIN products p ON r.product_id=p.id WHERE r.dealer_id=%s AND r.cancelled=0 AND p.metal='Silver'",(d["id"],))
        si=query_one("SELECT COALESCE(SUM(i.pure_wt),0) as t FROM issues i JOIN products p ON i.product_id=p.id WHERE i.dealer_id=%s AND i.cancelled=0 AND p.metal='Silver'",(d["id"],))
        g=round((gr["t"] if gr else 0)-(gi["t"] if gi else 0),3)
        s=round((sr["t"] if sr else 0)-(si["t"] if si else 0),3)
        tg+=g; ts+=s
        gc="green-c" if g>=0 else "red-c"
        rows+=f"<tr><td>{d['dealer_code']}</td><td>{d['dealer_name']}</td><td>{d['phone'] or '-'}</td><td class='{gc}'>{g:,.3f}</td><td>{s:,.3f}</td></tr>"
    rows+=f"<tr style='font-weight:700;background:#1a1a1a'><td colspan='3'>TOTAL</td><td class='gold-c'>{tg:,.3f}</td><td>{ts:,.3f}</td></tr>"
    html=f"""<div class="wrap">
    <div class="stats">
      <div class="stat"><div class="val gold-c">{tg:,.3f}g</div><div class="lbl">Total Gold Balance</div></div>
      <div class="stat"><div class="val muted">{ts:,.3f}g</div><div class="lbl">Total Silver Balance</div></div>
    </div>
    <div class="card"><div class="card-head">⚖ All Dealer Balances</div>
    <div class="scroll"><table><tr><th>Code</th><th>Dealer</th><th>Phone</th><th>Gold Balance (g)</th><th>Silver Balance (g)</th></tr>{rows}</table></div>
    </div></div>"""
    return render("balance", html)

@app.route("/ledger")
@login_req
def ledger():
    did=request.args.get("dealer_id")
    dealers=query("SELECT id,dealer_code,dealer_name FROM dealers WHERE active=1 ORDER BY dealer_code")
    dealer_opts="".join(f"<option value='{d['id']}' {'selected' if str(d['id'])==str(did) else ''}>{d['dealer_code']} - {d['dealer_name']}</option>" for d in dealers)
    bills_html=""
    if did:
        bills=query("""SELECT bill_no,bill_date,'Receipt' as type,COUNT(*) as items,SUM(pure_wt) as total_pure,MIN(cancelled) as cancelled
            FROM receipts WHERE dealer_id=%s GROUP BY bill_no,bill_date
            UNION ALL
            SELECT bill_no,bill_date,'Issue' as type,COUNT(*) as items,SUM(pure_wt) as total_pure,MIN(cancelled) as cancelled
            FROM issues WHERE dealer_id=%s GROUP BY bill_no,bill_date
            ORDER BY bill_date,bill_no""",(did,did))
        rows=""
        for b in bills:
            tc="bg" if b["type"]=="Receipt" else "br"
            canc="canc" if b["cancelled"] else ""
            rows+=f"""<tr class='{canc}'>
                <td><a href='/bill?bill_no={b["bill_no"]}&type={b["type"]}'>{b["bill_no"]}</a></td>
                <td>{b["bill_date"]}</td>
                <td><span class='badge {tc}'>{b["type"]}</span></td>
                <td>{b["items"]}</td>
                <td>{b["total_pure"]:.3f}</td>
                <td>{"Cancelled" if b["cancelled"] else "Active"}</td></tr>"""
        bills_html=f"""<div class="card"><div class="card-head">Bills</div>
        <div class="scroll"><table><tr><th>Bill No</th><th>Date</th><th>Type</th><th>Items</th><th>Pure (g)</th><th>Status</th></tr>{rows}</table></div></div>"""
    html=f"""<div class="wrap">
    <form method="get" style="margin-bottom:14px;display:flex;gap:10px;align-items:center">
      <select name="dealer_id" style="background:#1a1a1a;border:1px solid #444;color:#f0ead6;padding:9px 12px;border-radius:8px;font-size:14px;flex:1">
        <option value="">Select Dealer...</option>{dealer_opts}</select>
      <button type="submit" style="padding:9px 20px;background:linear-gradient(135deg,#C9A84C,#E8C97A);color:#000;border:none;border-radius:8px;font-weight:700;cursor:pointer">View</button>
    </form>
    {bills_html}</div>"""
    return render("ledger", html)

@app.route("/bill")
@login_req
def bill_detail():
    bill_no=request.args.get("bill_no","")
    btype=request.args.get("type","Receipt")
    if btype=="Receipt":
        rows=query("""SELECT p.product_name,p.metal,r.gross_wt,r.stone_wt,r.net_wt,r.touch,r.pure_wt,r.making_amt,r.other_amt,r.remarks,r.cancelled
            FROM receipts r JOIN products p ON r.product_id=p.id WHERE r.bill_no=%s""",(bill_no,))
    else:
        rows=query("""SELECT p.product_name,p.metal,i.gross_wt,i.stone_wt,i.net_wt,i.touch,i.pure_wt,i.making_amt,i.other_amt,i.remarks,i.cancelled
            FROM issues i JOIN products p ON i.product_id=p.id WHERE i.bill_no=%s""",(bill_no,))
    trs=""; total=0
    for r in rows:
        canc="canc" if r["cancelled"] else ""
        trs+=f"<tr class='{canc}'><td>{r['product_name']}</td><td>{r['metal']}</td><td>{r['gross_wt']:.3f}</td><td>{r['stone_wt']:.3f}</td><td>{r['net_wt']:.3f}</td><td>{r['touch']}</td><td>{r['pure_wt']:.3f}</td><td>{r['making_amt']:,.0f}</td><td>{r['other_amt']:,.0f}</td><td>{r['remarks'] or '-'}</td></tr>"
        if not r["cancelled"]: total+=r["pure_wt"]
    html=f"""<div class="wrap">
    <a href="/ledger" style="font-size:13px;color:var(--gold)">← Back to Ledger</a>
    <h2 style="color:var(--gold);margin:12px 0 4px">Bill: {bill_no} &nbsp;<span style="font-size:14px;color:var(--muted)">({btype})</span></h2>
    <div class="card"><div class="scroll"><table>
    <tr><th>Product</th><th>Metal</th><th>Gross</th><th>Stone</th><th>Net</th><th>Touch</th><th>Pure(g)</th><th>Making₹</th><th>Other₹</th><th>Remarks</th></tr>
    {trs}</table></div></div>
    <div style="text-align:right;color:var(--green);font-weight:700;font-size:16px">Total Pure: {total:.3f} g</div>
    </div>"""
    return render("ledger", html)

@app.route("/receipts")
@login_req
def receipts():
    rows=query("""SELECT r.bill_no,r.bill_date,d.dealer_name,COUNT(*) as items,SUM(r.pure_wt) as total_pure,MIN(r.cancelled) as cancelled
        FROM receipts r JOIN dealers d ON r.dealer_id=d.id
        GROUP BY r.bill_no,r.bill_date,d.dealer_name ORDER BY MIN(r.id) DESC LIMIT 100""")
    trs=""
    for r in rows:
        canc="canc" if r["cancelled"] else ""
        trs+=f"<tr class='{canc}'><td><a href='/bill?bill_no={r['bill_no']}&type=Receipt'>{r['bill_no']}</a></td><td>{r['bill_date']}</td><td>{r['dealer_name']}</td><td>{r['items']}</td><td>{r['total_pure']:.3f}</td><td>{'Cancelled' if r['cancelled'] else 'Active'}</td></tr>"
    html=f"""<div class="wrap"><div class="card"><div class="card-head">⬇ Recent Receipts</div>
    <div class="scroll"><table><tr><th>Bill No</th><th>Date</th><th>Dealer</th><th>Items</th><th>Pure (g)</th><th>Status</th></tr>{trs}</table></div></div></div>"""
    return render("receipts", html)

@app.route("/issues")
@login_req
def issues():
    rows=query("""SELECT i.bill_no,i.bill_date,d.dealer_name,COUNT(*) as items,SUM(i.pure_wt) as total_pure,MIN(i.cancelled) as cancelled
        FROM issues i JOIN dealers d ON i.dealer_id=d.id
        GROUP BY i.bill_no,i.bill_date,d.dealer_name ORDER BY MIN(i.id) DESC LIMIT 100""")
    trs=""
    for r in rows:
        canc="canc" if r["cancelled"] else ""
        trs+=f"<tr class='{canc}'><td><a href='/bill?bill_no={r['bill_no']}&type=Issue'>{r['bill_no']}</a></td><td>{r['bill_date']}</td><td>{r['dealer_name']}</td><td>{r['items']}</td><td>{r['total_pure']:.3f}</td><td>{'Cancelled' if r['cancelled'] else 'Active'}</td></tr>"
    html=f"""<div class="wrap"><div class="card"><div class="card-head">⬆ Recent Issues</div>
    <div class="scroll"><table><tr><th>Bill No</th><th>Date</th><th>Dealer</th><th>Items</th><th>Pure (g)</th><th>Status</th></tr>{trs}</table></div></div></div>"""
    return render("issues", html)

@app.route("/dealers")
@login_req
def dealers():
    rows=query("SELECT * FROM dealers WHERE active=1 ORDER BY dealer_code")
    trs=""
    for d in rows:
        bal=0
        try:
            gr=query_one("SELECT COALESCE(SUM(r.pure_wt),0) as t FROM receipts r JOIN products p ON r.product_id=p.id WHERE r.dealer_id=%s AND r.cancelled=0 AND p.metal='Gold'",(d["id"],))
            gi=query_one("SELECT COALESCE(SUM(i.pure_wt),0) as t FROM issues i JOIN products p ON i.product_id=p.id WHERE i.dealer_id=%s AND i.cancelled=0 AND p.metal='Gold'",(d["id"],))
            bal=round((gr["t"] if gr else 0)-(gi["t"] if gi else 0),3)
        except: pass
        gc="green-c" if bal>=0 else "red-c"
        trs+=f"<tr><td>{d['dealer_code']}</td><td>{d['dealer_name']}</td><td>{d['phone'] or '-'}</td><td>{d['address'] or '-'}</td><td class='{gc}'>{bal:,.3f}g</td></tr>"
    html=f"""<div class="wrap"><div class="card"><div class="card-head">🏪 Dealers</div>
    <div class="scroll"><table><tr><th>Code</th><th>Name</th><th>Phone</th><th>Address</th><th>Gold Balance</th></tr>{trs}</table></div></div></div>"""
    return render("dealers", html)

@app.route("/products")
@login_req
def products():
    rows=query("SELECT * FROM products WHERE active=1 ORDER BY metal,product_code")
    trs="".join(f"<tr><td>{r['product_code']}</td><td>{r['product_name']}</td><td>{r['metal']}</td><td>{r['category']}</td><td>{r['default_touch']}</td></tr>" for r in rows)
    html=f"""<div class="wrap"><div class="card"><div class="card-head">📦 Products</div>
    <div class="scroll"><table><tr><th>Code</th><th>Name</th><th>Metal</th><th>Category</th><th>Default Touch</th></tr>{trs}</table></div></div></div>"""
    return render("products", html)

@app.route("/schedule")
@login_req
def schedule():
    from datetime import date as ddate
    rows=query("""SELECT d.dealer_code,d.dealer_name,d.phone,s.schedule_type,s.days_interval,
        s.next_due_date,s.notes FROM dealer_payment_schedule s JOIN dealers d ON s.dealer_id=d.id
        WHERE d.active=1 ORDER BY s.next_due_date""")
    today=ddate.today(); trs=""
    for r in rows:
        diff=None; color=""
        try:
            diff=(ddate.fromisoformat(r["next_due_date"])-today).days
            color="red-c" if diff<0 else ("gold-c" if diff<=3 else "green-c")
        except: pass
        days_txt=f"{diff} days" if diff is not None else "-"
        trs+=f"<tr><td>{r['dealer_code']}</td><td>{r['dealer_name']}</td><td>{r['phone'] or '-'}</td><td>{r['next_due_date'] or '-'}</td><td class='{color}'>{days_txt}</td><td>{r['notes'] or '-'}</td></tr>"
    html=f"""<div class="wrap"><div class="card"><div class="card-head">🔔 Payment Schedule</div>
    <div class="scroll"><table><tr><th>Code</th><th>Dealer</th><th>Phone</th><th>Next Due</th><th>Days Left</th><th>Notes</th></tr>{trs}</table></div></div></div>"""
    return render("schedule", html)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5050)), debug=False)
