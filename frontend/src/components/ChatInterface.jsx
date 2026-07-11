import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { dealdeskAPI } from '../services/api';
import './chat.css';

export const ChatInterface = () => {
    const [messages, setMessages] = useState([
        {
            role: 'ai',
            text: 'Hello! I\'m **DealDesk AI** — your SaaS-savvy sales copilot. Ask me to *compare vendors*, handle *objections*, draft *emails*, or surface *pricing details*. Try:\n\n- "Compare Firebase and Supabase authentication"\n- "Which platform is better for Postgres and predictable pricing?"\n- "Draft a reply to a customer worried about Vercel costs"'
        }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [vendor, setVendor] = useState('');
    const [mode, setMode] = useState('qa');
    const [uploading, setUploading] = useState(false);

    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userQuery = input.trim();
        setMessages(prev => [...prev, { role: 'user', text: userQuery }]);
        setInput('');
        setLoading(true);

        try {
            const response = await dealdeskAPI.ask(userQuery, {
                vendor: vendor || null,
                mode: mode
            });

            setMessages(prev => [...prev, {
                role: 'ai',
                text: response.answer,
                citations: response.citations,
                confidence: response.confidence,
                log_id: response.log_id,
                feedbackSent: null
            }]);
        } catch (error) {
            setMessages(prev => [...prev, {
                role: 'ai',
                text: `**Error:** ${error.message}\n\nMake sure the FastAPI backend is running:\n\`\`\`\npython -m uvicorn api.main:app --reload\n\`\`\``
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setUploading(true);
        setMessages(prev => [...prev, { role: 'user', text: `📄 Uploading document: **${file.name}**...` }]);

        try {
            await dealdeskAPI.upload(file, vendor || 'Custom');
            setMessages(prev => [...prev, {
                role: 'ai',
                text: `✅ **${file.name}** has been ingested!\n\nThe DealDesk RAG index is now updated. Try asking questions about the newly uploaded document.`
            }]);
        } catch (error) {
            setMessages(prev => [...prev, {
                role: 'ai',
                text: `❌ **Upload Error:** ${error.message}`
            }]);
        } finally {
            setUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const submitFeedback = async (msgIdx, logId, value) => {
        try {
            await dealdeskAPI.sendFeedback(logId, value);
            setMessages(prev => prev.map((msg, idx) =>
                idx === msgIdx ? { ...msg, feedbackSent: value } : msg
            ));
        } catch (e) {
            console.error("Feedback failed", e);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <div className="chat__wrapper">
            {/* ── HEADER ── */}
            <div className="chat__header">
                <div className="chat__logo">
                    <div className="chat__logo-icon">🧠</div>
                    <div>
                        <div className="chat__title">DealDesk AI</div>
                        <div className="chat__tagline">RAG-Powered SaaS Sales Copilot</div>
                    </div>
                </div>

                <div className="chat__controls">
                    <div className="chat__select-wrapper">
                        <select
                            id="vendor-select"
                            className="chat__select"
                            value={vendor}
                            onChange={(e) => setVendor(e.target.value)}
                        >
                            <option value="">All Vendors</option>
                            <option value="Supabase">Supabase</option>
                            <option value="Firebase">Firebase</option>
                            <option value="Vercel">Vercel</option>
                            <option value="Render">Render</option>
                        </select>
                    </div>

                    <div className="chat__select-wrapper">
                        <select
                            id="mode-select"
                            className="chat__select"
                            value={mode}
                            onChange={(e) => setMode(e.target.value)}
                        >
                            <option value="qa">General Q&amp;A</option>
                            <option value="compare">Compare</option>
                            <option value="objection">Objection Handling</option>
                            <option value="email">Draft Email</option>
                            <option value="recommend">Recommend</option>
                        </select>
                    </div>

                    <input
                        type="file"
                        ref={fileInputRef}
                        style={{ display: 'none' }}
                        onChange={handleFileUpload}
                    />
                    <button
                        className="chat__upload-btn"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={uploading || loading}
                    >
                        {uploading ? '⏳ Uploading...' : '📁 Upload Doc'}
                    </button>
                </div>
            </div>

            {/* ── MESSAGES ── */}
            <div className="chat__messages">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message message--${msg.role}`}>
                        <div className={`message__avatar message__avatar--${msg.role}`}>
                            {msg.role === 'user' ? 'U' : '🧠'}
                        </div>
                        <div className="message__bubble">
                            <div className="message__content">
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                    {msg.text}
                                </ReactMarkdown>
                            </div>

                            {/* Citations & Feedback footer */}
                            {(msg.citations?.length > 0 || msg.confidence) && (
                                <div className="message__footer">
                                    {msg.citations?.length > 0 && (
                                        <div>
                                            <div className="message__citations-label">Sources</div>
                                            {msg.citations.map((cit, cIdx) => (
                                                <a
                                                    key={cIdx}
                                                    href={cit.source_url}
                                                    target="_blank"
                                                    rel="noreferrer"
                                                    className="message__citation-item"
                                                >
                                                    🔗 [{cit.id}] {cit.vendor} — {cit.title}
                                                </a>
                                            ))}
                                        </div>
                                    )}

                                    <div className="message__meta">
                                        {msg.confidence && (
                                            <span className="message__confidence">
                                                Confidence: {msg.confidence}
                                            </span>
                                        )}
                                        {msg.log_id && msg.feedbackSent === null && (
                                            <div className="message__feedback">
                                                <button
                                                    className="message__feedback-btn"
                                                    onClick={() => submitFeedback(idx, msg.log_id, 1)}
                                                >
                                                    👍 Helpful
                                                </button>
                                                <button
                                                    className="message__feedback-btn"
                                                    onClick={() => submitFeedback(idx, msg.log_id, -1)}
                                                >
                                                    👎 Not helpful
                                                </button>
                                            </div>
                                        )}
                                        {msg.feedbackSent != null && (
                                            <span className="message__feedback-thanks">✨ Thanks for the feedback!</span>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="message message--ai">
                        <div className="message__avatar message__avatar--ai">🧠</div>
                        <div className="message__bubble">
                            <div className="loading-dots">
                                <span></span><span></span><span></span>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* ── INPUT BAR ── */}
            <div className="chat__input-bar">
                <form className="chat__input-form" onSubmit={handleSubmit}>
                    <input
                        type="text"
                        id="chat-input"
                        className="chat__input"
                        placeholder="Ask about SaaS pricing, compare vendors, draft emails..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={loading}
                        autoFocus
                    />
                    <button
                        type="submit"
                        className="chat__send-btn"
                        disabled={loading || !input.trim()}
                    >
                        {loading ? 'Thinking...' : 'Send ↵'}
                    </button>
                </form>
                <div className="chat__hint">
                    Press <kbd style={{ background: 'rgba(255,255,255,0.08)', padding: '1px 5px', borderRadius: '4px', fontSize: '0.7rem' }}>Enter</kbd> to send · <kbd style={{ background: 'rgba(255,255,255,0.08)', padding: '1px 5px', borderRadius: '4px', fontSize: '0.7rem' }}>Shift+Enter</kbd> for new line
                </div>
            </div>
        </div>
    );
};
