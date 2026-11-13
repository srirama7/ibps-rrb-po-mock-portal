with open('adda.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

new_css = """
/* Interactive Section Navigation Tabs */
.section-nav-tab-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 750;
  cursor: pointer;
  border: 1px solid var(--border);
  background: #ffffff;
  color: #475569;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.15s ease;
  font-family: inherit;
}

.section-nav-tab-btn:hover {
  background: #f1f5f9;
  color: var(--primary);
  border-color: #cbd5e1;
}

.section-nav-tab-btn.active {
  background: #edf3e8;
  color: var(--primary);
  border-color: #67905d;
  box-shadow: 0 1px 4px rgba(40, 87, 71, 0.12);
}

.sec-pill-badge {
  background: #e2e8f0;
  color: #64748b;
  padding: 2px 7px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 800;
}

.section-nav-tab-btn.active .sec-pill-badge {
  background: #285747;
  color: #ffffff;
}

/* Question Palette Section Toggles */
.pal-tab-btn {
  padding: 5px 11px;
  font-size: 11px;
  font-weight: 750;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid var(--border);
  background: #ffffff;
  color: var(--text-muted);
  transition: all 0.15s ease;
  font-family: inherit;
}

.pal-tab-btn:hover {
  border-color: #94a3b8;
  color: var(--primary);
}

.pal-tab-btn.active {
  background: var(--primary);
  border-color: var(--primary);
  color: #ffffff;
}

/* Pause Break Modal & Overlay */
.cbt-pause-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.72);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(4px);
  padding: 16px;
  animation: cbtFadeIn 0.2s ease-out;
}

@keyframes cbtFadeIn {
  from { opacity: 0; transform: scale(0.97); }
  to { opacity: 1; transform: scale(1); }
}

.cbt-pause-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 36px 32px;
  max-width: 520px;
  width: 100%;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.3);
  text-align: center;
  border: 1px solid #e2e8f0;
}

.cbt-pause-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin: 22px 0 26px;
}

.cbt-pause-stat-item {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 8px;
}
"""

if '.cbt-pause-overlay' not in css_content:
    with open('adda.css', 'w', encoding='utf-8') as f:
        f.write(css_content + '\n' + new_css)
    print("Appended new CSS styles to adda.css successfully!")
else:
    print("Styles already present in adda.css.")
