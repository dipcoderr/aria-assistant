from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from agent import get_agent, DB_URI
from langgraph.checkpoint.postgres import PostgresSaver
import uuid, os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY') or os.urandom(32)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text_from_file(filepath: str, filename: str) -> str:
    """Extract plain text from uploaded files."""
    ext = filename.rsplit('.', 1)[-1].lower()
    try:
        if ext == 'txt':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif ext == 'pdf':
            import pypdf
            reader = pypdf.PdfReader(filepath)
            return "\n".join(page.extract_text() or '' for page in reader.pages)
        elif ext in ('doc', 'docx'):
            import docx
            doc = docx.Document(filepath)
            return "\n".join(p.text for p in doc.paragraphs)
        elif ext in ('csv',):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        else:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    except Exception as e:
        return f"[Could not read file: {e}]"

def get_ai_reply(content: str, thread_id: str) -> str:
    import re
    with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
        checkpointer.setup()
        agent = get_agent(checkpointer)
        response = agent.invoke(
            {"messages": [{"role": "user", "content": content}]},
            {"configurable": {"thread_id": thread_id}}
        )
    reply = response['messages'][-1].content
    if isinstance(reply, list):
        reply = " ".join(
            p.get("text", "") if isinstance(p, dict) else str(p)
            for p in reply
        ).strip()

    # Convert IMAGE_URL: marker to an HTML img tag
    reply = re.sub(
        r'IMAGE_URL:(https?://\S+)',
        r'<img src="\1" alt="Generated image" style="max-width:100%;border-radius:12px;margin-top:8px;display:block;">',
        reply
    )
    return reply

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    if 'thread_id' not in session:
        session['thread_id'] = str(uuid.uuid4())
    if 'messages' not in session:
        session['messages'] = []
    return render_template('chat.html', messages=session['messages'])

@app.route('/send', methods=['POST'])
def send():
    user_message = request.form.get('message', '').strip()
    file         = request.files.get('file')
    file_content = ''
    file_name    = ''

    # Handle file upload
    if file and file.filename:
        file_name = file.filename
        filepath  = os.path.join(UPLOAD_FOLDER, file_name)
        file.save(filepath)
        file_content = extract_text_from_file(filepath, file_name)
        # Combine file content with user message
        if user_message:
            full_content = f"{user_message}\n\n[File: {file_name}]\n{file_content}"
        else:
            full_content = f"[File uploaded: {file_name}]\n{file_content}\n\nPlease analyze or summarize this content."
        display_message = f"📎 {file_name}" + (f"\n{user_message}" if user_message else "")
    else:
        if not user_message:
            return redirect(url_for('home'))
        full_content    = user_message
        display_message = user_message

    # Get AI reply
    ai_reply = get_ai_reply(full_content, session['thread_id'])

    # Store in session
    session['messages'].append({'type': 'human', 'content': display_message})
    session['messages'].append({'type': 'ai',    'content': ai_reply})
    session.modified = True

    return redirect(url_for('home'))

@app.route('/new')
def new_conversation():
    session.clear()
    return redirect(url_for('home'))

@app.route('/clear-uploads', methods=['POST'])
def clear_uploads():
    """Clean up uploaded files."""
    for f in os.listdir(UPLOAD_FOLDER):
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, f))
        except Exception:
            pass
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', '5000')),
        debug=os.getenv('FLASK_DEBUG') == '1',
    )
