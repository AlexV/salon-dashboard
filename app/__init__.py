from __future__ import annotations

from datetime import date

from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_wtf.csrf import CSRFProtect

from . import repository
from .config import Config
from .database import close_db, get_db, init_db, seed_demo_data
from .forms import AppointmentForm

csrf = CSRFProtect()


def _validate_date_param(raw: str | None) -> str:
    if not raw:
        return date.today().isoformat()
    try:
        return date.fromisoformat(raw).isoformat()
    except ValueError:
        abort(400, description="Invalid date format")


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    csrf.init_app(app)
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()
        if not app.config.get("TESTING"):
            seed_demo_data()

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "frame-ancestors 'none'"
        )
        return response

    @app.route("/")
    def dashboard():
        target_date = _validate_date_param(request.args.get("date"))
        db = get_db()
        kpis = repository.daily_kpis(db, target_date)
        appointments = repository.list_appointments(db, target_date)
        services = repository.list_services(db)
        form = AppointmentForm()
        return render_template(
            "dashboard.html",
            kpis=kpis,
            appointments=appointments,
            services=services,
            form=form,
            target_date=target_date,
        )

    @app.route("/appointments", methods=["POST"])
    def create_appointment():
        form = AppointmentForm()
        if not form.validate_on_submit():
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", "error")
            return redirect(url_for("dashboard"))

        db = get_db()
        if not repository.service_exists(db, form.service_id.data):
            flash("Selected service does not exist", "error")
            return redirect(url_for("dashboard"))

        repository.create_appointment(
            db,
            client_name=form.client_name.data.strip(),
            service_id=form.service_id.data,
            appointment_date=form.appointment_date.data,
        )
        flash("Appointment created", "success")
        return redirect(
            url_for("dashboard", date=form.appointment_date.data)
        )

    @app.route("/api/kpis")
    def api_kpis():
        target_date = _validate_date_param(request.args.get("date"))
        db = get_db()
        return jsonify(repository.daily_kpis(db, target_date))

    @app.route("/api/status-breakdown")
    def api_status_breakdown():
        target_date = _validate_date_param(request.args.get("date"))
        db = get_db()
        return jsonify(repository.status_breakdown(db, target_date))

    @app.route("/api/revenue-by-service")
    def api_revenue_by_service():
        target_date = _validate_date_param(request.args.get("date"))
        db = get_db()
        return jsonify(repository.revenue_by_service(db, target_date))

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app
