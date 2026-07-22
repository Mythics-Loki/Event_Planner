import os
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ==============================================================================
# PERSISTENT DATABASE SETUP
# ==============================================================================
basedir = os.path.abspath(os.path.dirname(__file__))

# Check if running on Vercel environment
if os.environ.get('VERCEL'):
    db_path = '/tmp/events.db'
else:
    db_path = os.path.join(basedir, 'events.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==============================================================================
# DATABASE MODELS
# ==============================================================================
class SystemConfiguration(db.Model):
    __tablename__ = 'system_configuration'
    id = db.Column(db.Integer, primary_key=True)
    global_margin_percent = db.Column(db.Float, default=17.0, nullable=False)

class Worker(db.Model):
    __tablename__ = 'worker'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    assigned_event = db.Column(db.String(150), default="Unassigned")

class EventExpense(db.Model):
    __tablename__ = 'event_expense'
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(150), nullable=False)
    catering_name = db.Column(db.String(150), nullable=False)
    hall_base = db.Column(db.Float, nullable=False)
    hall_final = db.Column(db.Float, nullable=False)
    total_revenue = db.Column(db.Float, nullable=False)
    profit_margin_earned = db.Column(db.Float, nullable=False)

# Safely initialize persistent database tables
with app.app_context():
    db.create_all()
    if not SystemConfiguration.query.first():
        default_config = SystemConfiguration(global_margin_percent=17.0)
        db.session.add(default_config)
        db.session.commit()

# ==============================================================================
# CSS STYLES
# ==============================================================================
HOGWARTS_CASTLE_CSS = """
<style>
    :root {
        --amber-glow: #FFB300;
        --candle-gold: #FFD54F;
        --parchment: #E8DFD1;
    }
    body { 
        font-family: 'Georgia', serif; 
        color: var(--parchment); 
        margin: 0; 
        padding: 0; 
        overflow-x: hidden;
    }
    
    /* Fullscreen Background Video */
    #bg-video {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: -2;
    }

    /* Minimal Dark Overlay for Contrast */
    .video-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.25);
        z-index: -1;
    }

    .navbar { 
        background-color: rgba(0, 0, 0, 0.4); 
        padding: 20px 30px; 
        text-align: center; 
        border-bottom: 2px solid var(--amber-glow); 
    }
    .navbar h1 { color: var(--candle-gold); margin: 0; font-size: 26px; text-transform: uppercase; }
    .container { max-width: 900px; margin: 40px auto; padding: 0 20px; position: relative; z-index: 1; }
    
    /* PURELY TRANSPARENT CARD CONTAINER */
    .card { 
        background: transparent; 
        border-radius: 12px; 
        border: 1px solid rgba(255, 213, 79, 0.4); 
        padding: 35px; 
        text-align: center; 
    }
    
    .house-grid-2x2 {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        grid-template-rows: repeat(2, 1fr);
        gap: 20px;
        margin-top: 25px;
    }

    /* PURELY TRANSPARENT BUTTONS (NO BLUR, NO BACKGROUND) */
    .house-btn {
        padding: 25px 15px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        font-family: 'Segoe UI', sans-serif;
        background: transparent;
        transition: all 0.3s ease;
    }
    .house-btn:hover { 
        transform: translateY(-4px); 
        background: rgba(255, 255, 255, 0.15); /* Light glow on hover */
    }

    /* Minimal Sharp Colored Borders */
    .gryffindor { border: 2px solid #EEBA30; }
    .slytherin { border: 2px solid #BDC3C7; }
    .hufflepuff { border: 2px solid #D4AF37; }
    .ravenclaw { border: 2px solid #946B2D; }
</style>
"""

RED_GOLD_CSS = """
<style>
    body { font-family: 'Segoe UI', sans-serif; background-color: #FDFBF7; margin: 0; padding: 0; }
    .navbar { background-color: #4A0E17; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #EEBA30; color: white; }
    .nav-links a { color: #FFF; text-decoration: none; font-weight: bold; }
    .container { max-width: 950px; margin: 30px auto; padding: 0 20px; }
    .card { background: #FFF; border-radius: 10px; border: 1px solid #EEBA30; padding: 25px; margin-bottom: 25px; }
    h2 { color: #740001; margin-top: 0; border-bottom: 2px solid #EEBA30; padding-bottom: 8px; }
    .btn { background: #740001; color: white; border: 1px solid #EEBA30; padding: 8px 16px; border-radius: 5px; cursor: pointer; font-weight: bold; }
    input, select { padding: 8px; border: 1px solid #CCC; border-radius: 5px; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { border: 1px solid #DDD; padding: 10px; text-align: left; }
    th { background-color: #740001; color: white; }
</style>
"""

BLUE_BRONZE_CSS = """
<style>
    body { font-family: 'Segoe UI', sans-serif; background-color: #F5F7FA; margin: 0; padding: 0; }
    .navbar { background-color: #000A1A; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #946B2D; color: white; }
    .nav-links a { color: #FFF; text-decoration: none; font-weight: bold; }
    .container { max-width: 950px; margin: 30px auto; padding: 0 20px; }
    .card { background: #FFF; border-radius: 10px; border: 1px solid #946B2D; padding: 25px; margin-bottom: 25px; }
    h2 { color: #0E1A40; margin-top: 0; border-bottom: 2px solid #946B2D; padding-bottom: 8px; }
    .stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 20px; }
    .stat-box { background: #EAEFF5; padding: 12px; border-radius: 6px; border-left: 3px solid #946B2D; text-align: center; }
    .stat-box h3 { margin: 0; font-size: 11px; color: #555; }
    .stat-box p { margin: 5px 0 0 0; font-weight: bold; font-size: 16px; color: #0E1A40; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { border: 1px solid #DDD; padding: 8px; text-align: left; }
    th { background-color: #0E1A40; color: white; }
    .btn { background: #0E1A40; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 15px; }
</style>
"""

GREEN_SILVER_CSS = """
<style>
    body { font-family: 'Segoe UI', sans-serif; background-color: #F4F7F5; margin: 0; padding: 0; }
    .navbar { background-color: #0F3424; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #BDC3C7; color: white; }
    .nav-links a { color: #FFF; text-decoration: none; font-weight: bold; }
    .container { max-width: 650px; margin: 30px auto; padding: 0 20px; }
    .card { background: #FFF; border-radius: 10px; border: 1px solid #BDC3C7; padding: 25px; margin-bottom: 25px; }
    h2 { color: #0F3424; margin-top: 0; border-bottom: 2px solid #BDC3C7; padding-bottom: 8px; }
    .form-group { margin-bottom: 15px; }
    label { display: block; margin-bottom: 5px; font-weight: bold; color: #1A4D36; font-size: 14px; }
    input { width: 100%; padding: 10px; border: 1px solid #CCC; border-radius: 5px; box-sizing: border-box; }
    .btn { background: #1A4D36; color: white; border: none; padding: 12px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; font-size: 15px; }
</style>
"""

PURPLE_GOLD_CSS = """
<style>
    body { font-family: 'Segoe UI', sans-serif; background-color: #FAFAFA; margin: 0; padding: 0; }
    .navbar { background-color: #2D1442; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #D4AF37; color: white; }
    .nav-links a { color: #FFF; text-decoration: none; font-weight: bold; }
    .container { max-width: 1100px; margin: 30px auto; padding: 0 20px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .card { background: #FFF; border-radius: 10px; border: 1px solid #DDD; padding: 25px; margin-bottom: 20px; }
    h2 { color: #2D1442; margin-top: 0; border-bottom: 2px solid #D4AF37; padding-bottom: 8px; }
    .form-group { margin-bottom: 15px; }
    label { display: block; margin-bottom: 5px; font-weight: bold; font-size: 14px; }
    input, select, textarea { width: 100%; padding: 10px; border: 1px solid #CCC; border-radius: 5px; box-sizing: border-box; }
    .btn { background: #D4AF37; color: #2D1442; border: none; padding: 12px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; font-size: 15px; margin-top: 10px; }
    .btn-pdf { background: #2D1442; color: #FFD54F; border: 1px solid #D4AF37; padding: 12px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; text-align: center; text-decoration: none; display: inline-block; box-sizing: border-box; margin-top: 15px; }
    .invoice-line { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed #DDD; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { border: 1px solid #DDD; padding: 8px; text-align: left; font-size: 13px; }
    th { background-color: #2D1442; color: white; }
</style>
"""

# ==============================================================================
# HTML TEMPLATES
# ==============================================================================
INDEX_HTML = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Hogwarts Suite</title>
    {HOGWARTS_CASTLE_CSS}
</head>
<body>
    <!-- Background Video directly from root directory -->
    <video autoplay loop muted playsinline id="bg-video">
        <source src="/background.mp4" type="video/mp4">
        Your browser does not support HTML5 video.
    </video>
    <div class="video-overlay"></div>

    <div class="navbar">
        <h1>VENIX CASTLE <span>// GREAT HALL HUB</span></h1>
    </div>
    <div class="container">
        <div class="card">
            <h2 style="color: var(--candle-gold); border: none; margin-bottom: 5px;">Main Stays</h2>
            <p style="color: #E8DFD1; opacity: 0.85;">Select a management workspace below.</p>
            
            <div class="house-grid-2x2">
                <a href="/gryffindor" class="house-btn gryffindor">
                    <span style="font-size: 18px;">Staff Ledger</span>
                    <small style="opacity: 0.85; margin-top: 5px;">(Worker Assignments)</small>
                </a>
                <a href="/manager" class="house-btn slytherin">
                    <span style="font-size: 18px;">Master Config</span>
                    <small style="opacity: 0.85; margin-top: 5px;">(Master Margin Config)</small>
                </a>
                <a href="/planner" class="house-btn hufflepuff">
                    <span style="font-size: 18px;">Event Planner</span>
                    <small style="opacity: 0.85; margin-top: 5px;">(Event Planner & Past Orders)</small>
                </a>
                <a href="/ravenclaw" class="house-btn ravenclaw">
                    <span style="font-size: 18px;">Profit and Loss</span>
                    <small style="opacity: 0.85; margin-top: 5px;">(P&L Financial Analytics)</small>
                </a>
            </div>
        </div>
    </div>
</body>
</html>
"""

PLANNER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Hufflepuff Planner</title>
    """ + PURPLE_GOLD_CSS + """
</head>
<body>
    <div class="navbar">
        <h1>HUFFLEPUFF PLANNER</h1>
        <div class="nav-links"><a href="/">Main Hall</a></div>
    </div>
    <div class="container">
        <div class="grid">
            <div class="card">
                <h2>Invoice Compiler</h2>
                <form method="POST" action="/planner">
                    <div class="form-group">
                        <label>Event Name</label>
                        <input type="text" name="event_title" placeholder="Grand Wedding Reception" required>
                    </div>

                    <div style="border: 1px solid #E2D3B4; background: #FDFBF7; padding: 15px; border-radius: 6px; margin-bottom: 15px;">
                        <h3 style="margin-top:0; font-size:14px; color:#2D1442;">Custom Catering Service Details</h3>
                        <div class="form-group">
                            <label>Catering Service / Vendor Name</label>
                            <input type="text" name="catering_name" placeholder="e.g. Royal Feast Caterers" required>
                        </div>
                        <div class="form-group">
                            <label>Cuisine / Service Description</label>
                            <input type="text" name="catering_style" placeholder="e.g. Multi-Cuisine Buffet" required>
                        </div>
                        <div class="form-group">
                            <label>Per Plate Rate Base Cost (₹)</label>
                            <input type="number" step="0.01" name="per_plate_cost" placeholder="850" required>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Customer / Guest Count</label>
                        <input type="number" name="guest_count" placeholder="Enter guest count" min="1" required>
                    </div>

                    <div class="form-group">
                        <label>Hall / Venue Name</label>
                        <input type="text" name="hall_name" placeholder="Great Oak Hall" required>
                    </div>
                    <div class="form-group">
                        <label>Hall Rental Base Cost (₹)</label>
                        <input type="number" step="0.01" name="hall_rent" placeholder="50000" required>
                    </div>

                    <div class="form-group">
                        <label>Decor Provider</label>
                        <input type="text" name="decor_company" placeholder="Royal Floral Decor" required>
                    </div>
                    <div class="form-group">
                        <label>Decor Base Cost (₹)</label>
                        <input type="number" step="0.01" name="decor_cost" placeholder="25000" required>
                    </div>

                    <button type="submit" class="btn">Compile Estimate</button>
                </form>
            </div>

            <div class="card">
                <h2>Current Estimate Proposal</h2>
                {% if report %}
                    <h3 style="color:#2D1442; margin-top:0;">{{ report.event_title }}</h3>
                    
                    <div class="invoice-line">
                        <span><b>Catering Service:</b></span>
                        <span>{{ report.c_name }}</span>
                    </div>
                    <div style="font-size:12px; color:#555; margin-bottom:8px;">
                        • Style: {{ report.c_style }}<br>
                        • {{ report.guest_count }} Guests @ ₹{{ "{:,.2f}".format(report.per_plate) }}/plate + Margin
                    </div>
                    <div class="invoice-line">
                        <span>Catering Total:</span>
                        <span><b>₹{{ "{:,.2f}".format(report.c_final) }}</b></span>
                    </div>

                    <div class="invoice-line" style="margin-top:12px;">
                        <span><b>Venue Rental:</b> {{ report.h_name }}</span>
                        <span><b>₹{{ "{:,.2f}".format(report.h_final) }}</b></span>
                    </div>

                    <div class="invoice-line">
                        <span><b>Decor Package:</b> {{ report.d_company }}</span>
                        <span><b>₹{{ "{:,.2f}".format(report.d_final) }}</b></span>
                    </div>

                    <hr style="border:none; border-top: 2px solid #2D1442; margin: 15px 0;">
                    
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:16px; font-weight:bold; color:#2D1442;">Estimated Total:</span>
                        <span style="font-size:22px; font-weight:bold; color:#2D1442;">₹{{ "{:,.2f}".format(report.grand_total) }}</span>
                    </div>

                    <a href="/print_invoice?title={{ report.event_title }}&c_name={{ report.c_name }}&c_style={{ report.c_style }}&guests={{ report.guest_count }}&plate_rate={{ report.per_plate }}&c_final={{ report.c_final }}&h_name={{ report.h_name }}&h_final={{ report.h_final }}&d_company={{ report.d_company }}&d_final={{ report.d_final }}&total={{ report.grand_total }}" 
                       target="_blank" class="btn-pdf">
                        📄 Print / Export PDF Invoice
                    </a>
                {% else %}
                    <p style="color: #777;">Fill in details on the left to generate an invoice proposal.</p>
                {% endif %}
            </div>
        </div>

        <div class="card">
            <h2>Saved Past Order Records</h2>
            {% if past_orders %}
            <table>
                <thead>
                    <tr>
                        <th>Order ID</th>
                        <th>Event Name</th>
                        <th>Catering Vendor</th>
                        <th>Total Revenue</th>
                        <th>Profit Earned</th>
                    </tr>
                </thead>
                <tbody>
                    {% for order in past_orders %}
                    <tr>
                        <td>#{{ order.id }}</td>
                        <td><b>{{ order.event_name }}</b></td>
                        <td>{{ order.catering_name }}</td>
                        <td>₹{{ "{:,.2f}".format(order.total_revenue) }}</td>
                        <td style="color: #2D6A4F; font-weight: bold;">+₹{{ "{:,.2f}".format(order.profit_margin_earned) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="color: #777;">No past orders recorded yet.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

GRYFFINDOR_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Gryffindor Desk</title>
    """ + RED_GOLD_CSS + """
</head>
<body>
    <div class="navbar">
        <h1>GRYFFINDOR DESK</h1>
        <div class="nav-links"><a href="/">Main Hall</a></div>
    </div>
    <div class="container">
        <div class="card">
            <h2>Register Staff Personnel</h2>
            <form method="POST" action="/add_worker">
                <div style="display: flex; gap: 10px;">
                    <input type="text" name="name" placeholder="Name" required style="flex: 2;">
                    <input type="text" name="role" placeholder="Role" required style="flex: 2;">
                    <input type="number" step="0.01" name="salary" placeholder="Salary (₹)" required style="flex: 1;">
                    <button type="submit" class="btn">Add Staff</button>
                </div>
            </form>
        </div>

        <div class="card">
            <h2>Worker Event Roster</h2>
            {% if workers %}
            <table>
                <thead>
                    <tr>
                        <th>Worker Name</th>
                        <th>Role</th>
                        <th>Salary</th>
                        <th>Assigned Event</th>
                        <th>Assign Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for worker in workers %}
                    <tr>
                        <td><b>{{ worker.name }}</b></td>
                        <td>{{ worker.role }}</td>
                        <td>₹{{ "{:,.2f}".format(worker.salary) }}</td>
                        <td><span style="color: #740001; font-weight: bold;">{{ worker.assigned_event }}</span></td>
                        <td>
                            <form method="POST" action="/assign_worker" style="display:flex; gap: 5px;">
                                <input type="hidden" name="worker_id" value="{{ worker.id }}">
                                <select name="event_name">
                                    <option value="Unassigned">-- Unassign --</option>
                                    {% for ev in events %}
                                    <option value="{{ ev.event_name }}">{{ ev.event_name }}</option>
                                    {% endfor %}
                                </select>
                                <button type="submit" class="btn">Update</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="color: #666;">No workers registered. Add staff above.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

RAVENCLAW_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Ravenclaw Analytics</title>
    """ + BLUE_BRONZE_CSS + """
</head>
<body>
    <div class="navbar">
        <h1>RAVENCLAW ANALYTICS</h1>
        <div class="nav-links"><a href="/">Main Hall</a></div>
    </div>
    <div class="container">
        <div class="card">
            <h2>Financial Overview</h2>
            
            <div class="stat-grid">
                <div class="stat-box">
                    <h3>Gross Revenue</h3>
                    <p>₹{{ "{:,.2f}".format(total_revenue) }}</p>
                </div>
                <div class="stat-box">
                    <h3>Margin Profit</h3>
                    <p style="color: #2D6A4F;">+₹{{ "{:,.2f}".format(total_margin_profit) }}</p>
                </div>
                <div class="stat-box">
                    <h3>Venue Fee (10%)</h3>
                    <p style="color: #A63A50;">-₹{{ "{:,.2f}".format(total_venue_share) }}</p>
                </div>
                <div class="stat-box">
                    <h3>Payroll Deducted</h3>
                    <p style="color: #A63A50;">-₹{{ "{:,.2f}".format(selected_payroll) }}</p>
                </div>
            </div>

            <div style="background: #000A1A; color: #C5A059; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
                <h3 style="margin:0; font-size: 12px; text-transform: uppercase;">Net Profit Balance</h3>
                <h1 style="margin:5px 0 0 0; font-size: 28px; color: #FFF;">₹{{ "{:,.2f}".format(net_profit) }}</h1>
            </div>

            <h2>Payroll Filter</h2>
            {% if workers %}
            <form method="POST" action="/ravenclaw">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 40px; text-align: center;">Deduct</th>
                            <th>Worker</th>
                            <th>Role</th>
                            <th>Assigned Event</th>
                            <th>Salary</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for worker in workers %}
                        <tr>
                            <td style="text-align: center;">
                                <input type="checkbox" name="selected_workers" value="{{ worker.id }}" 
                                {% if worker.id in selected_ids %}checked{% endif %}>
                            </td>
                            <td><b>{{ worker.name }}</b></td>
                            <td>{{ worker.role }}</td>
                            <td>{{ worker.assigned_event }}</td>
                            <td>₹{{ "{:,.2f}".format(worker.salary) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <button type="submit" class="btn">Recalculate Net Profit</button>
            </form>
            {% else %}
            <p style="color: #666;">No workers present for payroll deduction.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

MANAGER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Slytherin Desk</title>
    """ + GREEN_SILVER_CSS + """
</head>
<body>
    <div class="navbar">
        <h1>SLYTHERIN CONFIG DESK</h1>
        <div class="nav-links"><a href="/">Main Hall</a></div>
    </div>
    <div class="container">
        <div class="card">
            <h2>Global Profit Margin Control</h2>
            <form method="POST" action="/update_config">
                <div class="form-group">
                    <label>Master Suite Margin (%)</label>
                    <input type="number" step="0.1" name="global_margin" value="{{ current_margin }}" required>
                </div>
                <button type="submit" class="btn">Update Margin</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

INVOICE_PRINT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Customer Invoice - {{ title }}</title>
    <style>
        body { font-family: 'Helvetica Neue', Arial, sans-serif; color: #333; padding: 40px; max-width: 800px; margin: auto; }
        .invoice-header { display: flex; justify-content: space-between; border-bottom: 3px solid #2D1442; padding-bottom: 20px; }
        .logo h1 { margin: 0; color: #2D1442; font-size: 28px; }
        .logo p { margin: 5px 0 0 0; color: #666; font-size: 13px; }
        .invoice-title { text-align: right; }
        .invoice-title h2 { margin: 0; color: #D4AF37; font-size: 24px; text-transform: uppercase; }
        .meta-grid { display: flex; justify-content: space-between; margin: 30px 0; background: #FAFAFA; padding: 15px; border-radius: 6px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { background: #2D1442; color: white; padding: 12px; text-align: left; font-size: 13px; }
        td { padding: 12px; border-bottom: 1px solid #EEE; font-size: 14px; }
        .total-box { margin-top: 30px; text-align: right; }
        .total-box h2 { color: #2D1442; font-size: 26px; margin: 5px 0; }
        .footer { margin-top: 50px; text-align: center; color: #888; font-size: 12px; border-top: 1px solid #DDD; padding-top: 20px; }
        @media print {
            .no-print { display: none; }
            body { padding: 0; }
        }
    </style>
</head>
<body>
    <div class="no-print" style="margin-bottom: 20px; text-align: right;">
        <button onclick="window.print()" style="padding: 10px 20px; background: #2D1442; color: white; border: none; font-weight: bold; cursor: pointer; border-radius: 4px;">🖨 Print or Save as PDF</button>
    </div>

    <div class="invoice-header">
        <div class="logo">
            <h1>HOGWARTS SUITE</h1>
            <p>Premium Event Management Solutions</p>
        </div>
        <div class="invoice-title">
            <h2>ESTIMATE INVOICE</h2>
            <p style="margin: 3px 0 0 0; font-size: 12px; color: #888;">Official Client Quotation</p>
        </div>
    </div>

    <div class="meta-grid">
        <div>
            <strong>Event Title:</strong> {{ title }}<br>
            <strong>Venue:</strong> {{ h_name }}
        </div>
        <div style="text-align: right;">
            <strong>Guest Count:</strong> {{ guests }} Pax<br>
            <strong>Date Generated:</strong> Today
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Service Description</th>
                <th>Details</th>
                <th style="text-align: right;">Amount (₹)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><b>Catering Service</b><br><small>{{ c_name }}</small></td>
                <td>{{ c_style }} - {{ guests }} Guests @ ₹{{ "{:,.2f}".format(plate_rate) }}/plate</td>
                <td style="text-align: right;">₹{{ "{:,.2f}".format(c_final) }}</td>
            </tr>
            <tr>
                <td><b>Venue Rental</b></td>
                <td>{{ h_name }}</td>
                <td style="text-align: right;">₹{{ "{:,.2f}".format(h_final) }}</td>
            </tr>
            <tr>
                <td><b>Decor Package</b></td>
                <td>{{ d_company }}</td>
                <td style="text-align: right;">₹{{ "{:,.2f}".format(d_final) }}</td>
            </tr>
        </tbody>
    </table>

    <div class="total-box">
        <p style="margin: 0; color: #666; font-size: 14px;">Grand Total (Inc. Margins & Services):</p>
        <h2>₹{{ "{:,.2f}".format(total) }}</h2>
    </div>

    <div class="footer">
        <p>Thank you for partnering with Hogwarts Suite Event Solutions.</p>
    </div>
</body>
</html>
"""

# ==============================================================================
# ROUTE HANDLERS
# ==============================================================================
@app.route('/background.mp4')
def serve_video():
    return send_from_directory(basedir, 'background.mp4')

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/gryffindor')
def gryffindor():
    workers = Worker.query.all()
    events = EventExpense.query.all()
    return render_template_string(GRYFFINDOR_HTML, workers=workers, events=events)

@app.route('/add_worker', methods=['POST'])
def add_worker():
    name = request.form.get('name')
    role = request.form.get('role')
    salary = float(request.form.get('salary', 0.0))
    new_worker = Worker(name=name, role=role, salary=salary)
    db.session.add(new_worker)
    db.session.commit()
    return redirect(url_for('gryffindor'))

@app.route('/assign_worker', methods=['POST'])
def assign_worker():
    worker_id = request.form.get('worker_id')
    event_name = request.form.get('event_name')
    worker = Worker.query.get(worker_id)
    if worker:
        worker.assigned_event = event_name
        db.session.commit()
    return redirect(url_for('gryffindor'))

@app.route('/manager')
def manager():
    config = SystemConfiguration.query.first()
    margin = config.global_margin_percent if config else 17.0
    return render_template_string(MANAGER_HTML, current_margin=margin)

@app.route('/update_config', methods=['POST'])
def update_config():
    margin = float(request.form.get('global_margin', 17.0))
    config = SystemConfiguration.query.first()
    if not config:
        config = SystemConfiguration(global_margin_percent=margin)
        db.session.add(config)
    else:
        config.global_margin_percent = margin
    db.session.commit()
    return redirect(url_for('manager'))

@app.route('/planner', methods=['GET', 'POST'])
def planner():
    config = SystemConfiguration.query.first()
    margin = config.global_margin_percent if config else 17.0
    report = None

    if request.method == 'POST':
        title = request.form.get('event_title')
        c_name = request.form.get('catering_name')
        c_style = request.form.get('catering_style')
        per_plate = float(request.form.get('per_plate_cost', 0.0))
        guests = int(request.form.get('guest_count', 1))
        h_name = request.form.get('hall_name')
        h_base = float(request.form.get('hall_rent', 0.0))
        d_company = request.form.get('decor_company')
        d_base = float(request.form.get('decor_cost', 0.0))

        multiplier = 1 + (margin / 100.0)
        c_base = per_plate * guests
        c_final = c_base * multiplier
        h_final = h_base * multiplier
        d_final = d_base * multiplier
        grand_total = c_final + h_final + d_final
        profit_earned = grand_total - (c_base + h_base + d_base)

        event_entry = EventExpense(
            event_name=title,
            catering_name=c_name,
            hall_base=h_base,
            hall_final=h_final,
            total_revenue=grand_total,
            profit_margin_earned=profit_earned
        )
        db.session.add(event_entry)
        db.session.commit()

        report = {
            'event_title': title,
            'c_name': c_name,
            'c_style': c_style,
            'guest_count': guests,
            'per_plate': per_plate,
            'c_final': c_final,
            'h_name': h_name,
            'h_final': h_final,
            'd_company': d_company,
            'd_final': d_final,
            'grand_total': grand_total
        }

    past_orders = EventExpense.query.order_by(EventExpense.id.desc()).all()
    return render_template_string(PLANNER_HTML, report=report, past_orders=past_orders)

@app.route('/ravenclaw', methods=['GET', 'POST'])
def ravenclaw():
    workers = Worker.query.all()
    events = EventExpense.query.all()

    total_revenue = sum(e.total_revenue for e in events)
    total_margin_profit = sum(e.profit_margin_earned for e in events)
    total_venue_share = total_revenue * 0.10

    selected_ids = []
    if request.method == 'POST':
        selected_ids = [int(x) for x in request.form.getlist('selected_workers')]

    selected_payroll = sum(w.salary for w in workers if w.id in selected_ids)
    net_profit = total_margin_profit - total_venue_share - selected_payroll

    return render_template_string(
        RAVENCLAW_HTML,
        workers=workers,
        total_revenue=total_revenue,
        total_margin_profit=total_margin_profit,
        total_venue_share=total_venue_share,
        selected_payroll=selected_payroll,
        net_profit=net_profit,
        selected_ids=selected_ids
    )

@app.route('/print_invoice')
def print_invoice():
    return render_template_string(
        INVOICE_PRINT_HTML,
        title=request.args.get('title', 'Event Estimate'),
        c_name=request.args.get('c_name', ''),
        c_style=request.args.get('c_style', ''),
        guests=int(request.args.get('guests', 0)),
        plate_rate=float(request.args.get('plate_rate', 0.0)),
        c_final=float(request.args.get('c_final', 0.0)),
        h_name=request.args.get('h_name', ''),
        h_final=float(request.args.get('h_final', 0.0)),
        d_company=request.args.get('d_company', ''),
        d_final=float(request.args.get('d_final', 0.0)),
        total=float(request.args.get('total', 0.0))
    )

if __name__ == '__main__':
    app.run(debug=True)
