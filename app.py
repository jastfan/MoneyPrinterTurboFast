#!/usr/bin/env python3
"""
Platform Hub — Phase 2: MongoDB-backed users, connected accounts (encrypted
tokens), video storage, and full per-platform tracking/report.

Pages:
  /login              simple email login (creates a user in MongoDB)
  /                   search
  /connect            connect accounts — OAuth tokens saved to MongoDB, encrypted
  /dashboard          full report: every video + every platform's status
  /upload             uploads a video to storage, queues a post job per platform

RUN:
  pip install -r requirements.txt
  cp .env.example .env   # fill in MongoDB URI, S3 keys, TOKEN_ENCRYPTION_KEY, etc.
  python app.py
"""
import socket
import dns.resolver
from services import content_pipeline

_dns_cache = {}

def _use_google_dns(host, port, family=0, type=0, proto=0, flags=0):
    if host not in _dns_cache:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = ["1.1.1.1", "8.8.8.8"]
        try:
            answer = resolver.resolve(host, "A")
            _dns_cache[host] = answer[0].to_text()
        except Exception:
            _dns_cache[host] = host  # fallback to normal resolution

    resolved_ip = _dns_cache[host]
    return socket._original_getaddrinfo(resolved_ip, port, family, type, proto, flags)

socket._original_getaddrinfo = socket.getaddrinfo
socket.getaddrinfo = _use_google_dns


import os
import secrets

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

from config import Config
from services import search_service, oauth_service, content_service, upload_service, storage_service
import db

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

from RenderDetect import init_render
init_render(app)

from hook_detector2 import init_hooks
init_hooks(app)

from services.scheduler import start_scheduler
_scheduler =start_scheduler()


from creator_tracker import init_creator_tracker
init_creator_tracker(app, scheduler=_scheduler)


UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads_tmp")
os.makedirs(UPLOAD_DIR, exist_ok=True)

PLATFORM_LIST = [
    {"id": "google", "name": "Google"},
    {"id": "youtube", "name": "YouTube"},
    {"id": "facebook", "name": "Facebook"},
    {"id": "x", "name": "X (Twitter)"},
    {"id": "tiktok", "name": "TikTok"},
]


def current_user_id():
    return session.get("user_id")


def require_login():
    if not current_user_id():
        flash("Please log in first.")
        return redirect(url_for("login"))
    return None


# ============================================================================
# LOGIN (simple, email-based — swap for real auth before going to production)
# ============================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        name = request.form.get("name", "").strip()
        if not email:
            flash("Email is required.")
            return redirect(url_for("login"))

        user = db.create_or_get_user(email, name)
        session["user_id"] = str(user["_id"])
        session["user_email"] = email
        flash(f"Logged in as {email}")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/health/db")
def health_db():
    """Simple endpoint to check whether MongoDB is actually connected or not."""
    result = db.check_connection()
    status_code = 200 if result["connected"] else 503
    return jsonify(result), status_code

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ============================================================================
# SEARCH
# ============================================================================
@app.route("/")
def index():
    return render_template("index.html", query=None, data=None)


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return redirect(url_for("index"))

    data = search_service.search_youtube(query)
    return render_template("index.html", query=query, data=data)


# ============================================================================
# CONNECT ACCOUNTS  (tokens now saved to MongoDB, encrypted — not session)
# ============================================================================
@app.route("/connect")
def connect():
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    user_id = current_user_id()
    connected = db.list_connected_platforms(user_id)

    platforms = []
    for p in PLATFORM_LIST:
        state = secrets.token_urlsafe(16)
        session[f"state_{p['id']}"] = state

        if p["id"] == "google":
            url = oauth_service.google_authorize_url(state)
        elif p["id"] == "facebook":
            url = oauth_service.facebook_authorize_url(state)
        elif p["id"] == "x":
            url, verifier = oauth_service.x_authorize_url(state)
            session["x_pkce_verifier"] = verifier
        elif p["id"] == "tiktok":
            url = oauth_service.tiktok_authorize_url(state)
        else:
            url = "#"

        platforms.append({**p, "connect_url": url})

    return render_template(
        "connect.html",
        platforms=platforms,
        connected=connected,
        telegram_bot_username=Config.TELEGRAM_BOT_USERNAME,
    )


@app.route("/connect/google/callback")
def connect_google_callback():
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    code = request.args.get("code")
    if not code:
        flash("Google connection was cancelled.")
        return redirect(url_for("connect"))

    token_data = oauth_service.google_exchange_code(code)
    if "access_token" not in token_data:
        flash(f"Google connection failed: {token_data}")
        return redirect(url_for("connect"))

    user_id = current_user_id()
    db.save_connected_account(user_id, "google", token_data)
    db.save_connected_account(user_id, "youtube", token_data)  # same token grants YouTube access
    flash("Google/YouTube connected and saved.")
    return redirect(url_for("dashboard"))


@app.route("/connect/facebook/callback")
def connect_facebook_callback():
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    code = request.args.get("code")
    if not code:
        flash("Facebook connection was cancelled.")
        return redirect(url_for("connect"))

    token_data = oauth_service.facebook_exchange_code(code)
    if "access_token" not in token_data:
        flash(f"Facebook connection failed: {token_data}")
        return redirect(url_for("connect"))

    db.save_connected_account(current_user_id(), "facebook", token_data)
    flash("Facebook connected and saved. Instagram Business accounts linked to your Pages are now available too.")
    return redirect(url_for("dashboard"))


@app.route("/connect/x/callback")
def connect_x_callback():
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    code = request.args.get("code")
    verifier = session.get("x_pkce_verifier")
    if not code or not verifier:
        flash("X connection was cancelled.")
        return redirect(url_for("connect"))

    token_data = oauth_service.x_exchange_code(code, verifier)
    if "access_token" not in token_data:
        flash(f"X connection failed: {token_data}")
        return redirect(url_for("connect"))

    db.save_connected_account(current_user_id(), "x", token_data)
    flash("X connected and saved.")
    return redirect(url_for("dashboard"))


@app.route("/connect/tiktok/callback")
def connect_tiktok_callback():
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    code = request.args.get("code")
    if not code:
        flash("TikTok connection was cancelled.")
        return redirect(url_for("connect"))

    token_data = oauth_service.tiktok_exchange_code(code)
    if "access_token" not in token_data:
        flash(f"TikTok connection failed: {token_data}")
        return redirect(url_for("connect"))

    db.save_connected_account(current_user_id(), "tiktok", token_data)
    flash("TikTok connected and saved.")
    return redirect(url_for("dashboard"))


@app.route("/connect/telegram/callback")
def connect_telegram_callback():
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    auth_data = request.args.to_dict()
    if not oauth_service.telegram_verify_login(auth_data):
        flash("Telegram login verification failed.")
        return redirect(url_for("connect"))

    db.save_connected_account(current_user_id(), "telegram", auth_data)
    flash("Telegram connected and saved.")
    return redirect(url_for("dashboard"))


@app.route("/disconnect/<platform>")
def disconnect(platform):
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    db.disconnect_account(current_user_id(), platform)
    flash(f"{platform.capitalize()} disconnected.")
    return redirect(url_for("connect"))


# ============================================================================
# DASHBOARD — full report: every video, every platform's status
# ============================================================================
@app.route("/dashboard")
def dashboard():
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    user_id = current_user_id()
    connected = db.list_connected_platforms(user_id)
    report = db.get_user_report(user_id)  # [{video, posts}, ...] — the full report

    return render_template("dashboard.html", connected=connected, report=report)

@app.route("/review")
def review():
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp
    user_id = current_user_id()
    content_pipeline.sync_finished_jobs(user_id)   # har baar page kholte hi latest check
    connected = db.list_connected_platforms(user_id)
    pending_clips = db.list_pending_clips(user_id)
    return render_template("review.html", pending_clips=pending_clips, connected=connected)


@app.route("/review/approve/<pending_clip_id>", methods=["POST"])
def review_approve(pending_clip_id):
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp
    user_id = current_user_id()
    title = request.form.get("title", "")
    caption = request.form.get("caption", "")
    platforms = request.form.getlist("platforms")
    try:
        content_pipeline.approve_clip_to_upload(
            user_id, pending_clip_id, title=title, caption=caption, platforms=platforms
        )
        flash("Clip approved — uploaded to storage and queued for posting.")
    except Exception as e:
        flash(f"Approve failed: {e}")
    return redirect(url_for("review"))


@app.route("/review/discard/<pending_clip_id>", methods=["POST"])
def review_discard(pending_clip_id):
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp
    pending = db.get_pending_clip(pending_clip_id)
    if pending and str(pending["user_id"]) == str(current_user_id()):
        db.delete_pending_clip(pending_clip_id)
        flash("Clip discarded.")
    return redirect(url_for("review"))


# ============================================================================
# UPLOAD — saves the video to storage, creates a DB record, and a tracked
# post job per selected platform (Phase 3 will add AI content + a real
# background worker to actually run these jobs on a schedule; for now this
# uploads immediately and records the outcome).
# ============================================================================
@app.route("/upload", methods=["POST"])
def upload():
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    user_id = current_user_id()
    selected_platforms = request.form.getlist("platforms")
    title = request.form.get("title", "")
    caption = request.form.get("caption", "")

    video_file = request.files.get("video_file")
    if not video_file or not video_file.filename:
        flash("Please choose a video file.")
        return redirect(url_for("dashboard"))

    local_path = os.path.join(UPLOAD_DIR, video_file.filename)
    video_file.save(local_path)

    try:
        # 1. Upload to permanent storage (S3-compatible) and record it in
        #    MongoDB. The local file is kept around too — YouTube/Facebook
        #    take a local file upload; Instagram/Pinterest need the public
        #    URL storage just gave us. It's only deleted once every
        #    platform below has finished (success or fail).
        try:
            storage_result = storage_service.upload_video_file(local_path, user_id)
        except Exception as e:
            flash(f"Storage upload failed: {e}")
            return redirect(url_for("dashboard"))

        video_doc = db.create_video(
            user_id=user_id,
            filename=video_file.filename,
            storage_key=storage_result["storage_key"],
            storage_url=storage_result["public_url"],
            size_bytes=storage_result["size_bytes"],
        )
        db.update_video(video_doc["_id"], ai_title=title, ai_description=caption, status="ready")

        # 2. Create a tracked post job per selected platform, then attempt it
        for platform in selected_platforms:
            post_job = db.create_post_job(user_id, video_doc["_id"], platform)
            db.update_post_job(post_job["_id"], status="processing")

            try:
                account = db.get_connected_account(user_id, platform)
                if not account:
                    raise RuntimeError(f"{platform} is not connected.")

                token = account["tokens"]
                if not token.get("access_token"):
                        raise RuntimeError(f"No access token stored for {platform}. Reconnect the account.")

                # IMPORTANT: only actually-implemented platforms reach
                # mark_post_success. Anything else raises, so it's honestly
                # recorded as "failed" with a clear reason — never silently
                # marked "posted" when nothing was posted.
                result = _post_to_platform(platform, token, local_path, storage_result, title, caption)

                db.mark_post_success(
                    post_job["_id"],
                    platform_post_id=str(result.get("id", "")),
                    platform_post_url=result.get("url", ""),
                )
                flash(f"{platform}: posted successfully.")

            except Exception as e:
                db.mark_post_failed(post_job["_id"], str(e))
                flash(f"{platform}: FAILED — {e}")

        return redirect(url_for("dashboard"))

    finally:
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
            except PermissionError:
                pass


def _post_to_platform(platform, token, local_path, storage_result, title, caption):
    """
    Dispatches to the right upload_service function per platform.
    YouTube/Facebook upload the local file directly; Instagram/Pinterest
    would need a public HTTPS URL (storage_result already has one) plus an
    extra per-user ID this app doesn't collect yet — see the note below.
    """
    if platform == "youtube":
        return upload_service.upload_to_youtube(token, local_path, title, caption)

    access_token = token.get("access_token") if isinstance(token, dict) else token

    if platform == "facebook":
        # The token stored from OAuth is the *user's* token; posting to a
        # Page needs that Page's own access token, fetched via Graph API.
        pages = content_service.get_facebook_pages(token)
        if not pages:
            raise RuntimeError("No Facebook Page found for this account. Connect a Page in the Meta OAuth screen.")
        page = pages[0]
        return upload_service.upload_to_facebook(page["id"], page["access_token"], local_path, caption)

    if platform == "tiktok":
        return upload_service.upload_to_tiktok(token, local_path, title)

    if platform == "x":
        raise RuntimeError(
            "X's OAuth 2.0 user-context flow (used for /connect/x) doesn't grant "
            "the v1.1 media-upload access tweepy needs for video. Posting to X "
            "needs OAuth 1.0a user tokens, or X's chunked media upload over "
            "OAuth 2.0 (INIT/APPEND/FINALIZE against upload.twitter.com) — "
            "not wired up yet."
        )

    if platform in ("instagram", "pinterest"):
        raise RuntimeError(
            f"{platform.capitalize()} needs an extra account identifier "
            f"({'Instagram Business Account ID' if platform == 'instagram' else 'Pinterest Board ID'}) "
            "that this app doesn't collect yet — there's no /connect flow for "
            f"{platform} either. Add both before enabling this checkbox for real."
        )

    raise RuntimeError(f"Unsupported platform: {platform}")


from datetime import datetime, timezone, timedelta


@app.route("/bulk_upload", methods=["POST"])
def bulk_upload():
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    user_id = current_user_id()
    files = request.files.getlist("video_files")
    titles = request.form.getlist("titles")
    captions = request.form.getlist("captions")
    selected_platforms = request.form.getlist("platforms")
    gap_hours = float(request.form.get("gap_hours", 24))

    if not files:
        return jsonify({"error": "Please choose at least one video file."}), 400

    base_time = datetime.now(timezone.utc)
    count = 0

    for i, video_file in enumerate(files):
        if not video_file.filename:
            continue

        storage_result = storage_service.upload_video_stream(video_file.stream, video_file.filename, user_id)
        scheduled_time = base_time + timedelta(hours=gap_hours * (i + 1))
        title = titles[i] if i < len(titles) else video_file.filename
        caption = captions[i] if i < len(captions) else ""

        db.create_queued_video(
            user_id=user_id, filename=video_file.filename,
            storage_key=storage_result["storage_key"], storage_url=storage_result["public_url"],
            size_bytes=storage_result["size_bytes"], scheduled_time=scheduled_time,
            title=title, caption=caption, platforms=selected_platforms,
        )
        count += 1

    return jsonify({"message": f"{count} videos queued for scheduled posting."})

# @app.route("/bulk_upload", methods=["POST"])
# def bulk_upload():
#     redirect_resp = require_login()
#     if redirect_resp:
#         return redirect_resp

#     user_id = current_user_id()
#     files = request.files.getlist("video_files")
#     selected_platforms = request.form.getlist("platforms")
#     gap_hours = int(request.form.get("gap_hours", 24))  # default: 1 video per day

#     base_time = datetime.now(timezone.utc)

#     for i, video_file in enumerate(files):
#         local_path = os.path.join(UPLOAD_DIR, video_file.filename)
#         video_file.save(local_path)

#         storage_result = storage_service.upload_video_file(local_path, user_id)

#         scheduled_time = base_time + timedelta(hours=gap_hours * (i + 1))

#         video_doc = db.create_queued_video(
#             user_id=user_id, filename=video_file.filename,
#             storage_key=storage_result["storage_key"], storage_url=storage_result["public_url"],
#             size_bytes=storage_result["size_bytes"], scheduled_time=scheduled_time,
#         )
#         db.update_video(video_doc["_id"], platforms=selected_platforms)

#         os.remove(local_path)  # local file ki zaroorat nahi ab, R2 pe already hai

#     flash(f"{len(files)} videos queued for scheduled posting.")
#     return redirect(url_for("dashboard"))


@app.route("/submit_url", methods=["POST"])
def submit_url_route():
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp
    user_id = current_user_id()
    url = request.form.get("url", "").strip()
    if not url:
        flash("URL daalo pehle.")
        return redirect(url_for("dashboard"))
    from services import render_client
    job_id = render_client.submit_url(user_id, url)
    db.track_render_job(user_id, job_id)
    flash("Processing shuru — kuch der mein clips tumhare dashboard pe khud aa jayenge.")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    # threaded=True is required for the Publish Studio progress bars: while
    # a publish/upload request is streaming a file to storage, the page
    # polls /api/publish/upload_progress/<id> on a SEPARATE request to read
    # live progress — that only works if the dev server can handle more
    # than one request at a time.
    app.run(debug=True, port=5000, threaded=True)