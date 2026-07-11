import React, { useState, useRef, useEffect } from 'react';
import { dealdeskAPI } from '../services/api';
import './chat.css';

export const ChatInterface = () => {
    const [messages, setMessages] = useState([
        { role: 'ai', text: 'Hello! I am DealDesk AI. How can I assist you with SaaS documentation today?' }
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
                text: `Error: ${error.message}. Make sure the FastAPI backend is running.`
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setUploading(true);
        setMessages(prev => [...prev, { role: 'user', text: `Uploading document: ${file.name}...` }]);

        try {
            await dealdeskAPI.upload(file, vendor || 'Custom');
            setMessages(prev => [...prev, {
                role: 'ai',
                text: `Success! ${file.name} has been ingested and the DealDesk RAG index is updated.`
            }]);
        } catch (error) {
            setMessages(prev => [...prev, {
                role: 'ai',
                text: `Upload Error: ${error.message}`
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

    return (
        <div className="chat__container">
            <div className="chat__header">
                <div className="chat__title">DealDesk AI</div>
                <div className="chat__controls">
                    <select
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
                    <select
                        className="chat__select"
                        value={mode}
                        onChange={(e) => setMode(e.target.value)}
                    >
                        <option value="qa">General Q&A</option>
                        <option value="compare">Compare</option>
                        <option value="objection">Objection Hanlding</option>
                        <option value="email">Draft Email</option>
                    </select>
                    <input
                        type="file"
                        ref={fileInputRef}
                        style={{ display: 'none' }}
                        onChange={handleFileUpload}
                    />
                    <button
                        className="chat__button chat__upload-btn"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={uploading || loading}
                        style={{ padding: '8px 16px', fontSize: '0.9rem' }}
                    >
                        {uploading ? 'Uploading...' : '📁 Upload'}
                    </button>
                </div>
            </div>

            <div className="chat__messages">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message message--${msg.role}`}>
                        <div className="message__text">{msg.text}</div>

                        {msg.citations && msg.citations.length > 0 && (
                            <div className="message__citations">
                                <strong>Sources:</strong>
                                {msg.citations.map((cit, cIdx) => (
                                    <a key={cIdx} href={cit.source_url} target="_blank" rel="noreferrer" className="message__citation-item">
                                        [{cit.id}] {cit.vendor} - {cit.title}
                                    </a>
                                ))}
                            </div>
                        )}

                        {msg.confidence && (
                            <div style={{ fontSize: '0.8rem', opacity: 0.7, marginTop: '8px', display: 'flex', justifyContent: 'space-between' }}>
                                <span>Confidence: {msg.confidence}</span>
                                {msg.log_id && msg.feedbackSent === null && (
                                    <span style={{ cursor: 'pointer', display: 'flex', gap: '8px' }}>
                                        <span onClick={() => submitFeedback(idx, msg.log_id, 1)}>👍</span>
                                        <span onClick={() => submitFeedback(idx, msg.log_id, -1)}>👎</span>
                                    </span>
                                )}
                                {msg.feedbackSent !== null && msg.feedbackSent !== undefined && (
                                    <span>Thank you for your feedback!</span>
                                )}
                            </div>
                        )}
                    </div>
                ))}
                {loading && (
                    <div className="message message--ai">
                        <div className="loading-dots">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <form className="chat__input-area" onSubmit={handleSubmit}>
                <input
                    type="text"
                    className="chat__input"
                    placeholder="Ask a question about SaaS docs..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={loading}
                />
                <button type="submit" className="chat__button" disabled={loading || !input.trim()}>
                    Send
                </button>
            </form>
        </div>
    );
};
