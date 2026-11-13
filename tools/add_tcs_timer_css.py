with open('adda.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

tcs_timer_css = """
/* Official TCS iON / IBPS Exam Header Timer Widget */
.tcs-timer-widget {
  background: #ffffff;
  border: 1px solid #cfdbc8;
  border-radius: 8px;
  padding: 6px 14px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.tcs-timer-main {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.tcs-timer-label {
  font-size: 13.5px;
  font-weight: 700;
  color: #334155;
  letter-spacing: 0.3px;
}

.tcs-timer-digits {
  font-family: 'Courier New', Courier, monospace;
  font-size: 20px;
  font-weight: 800;
  color: #173c34;
  min-width: 62px;
  text-align: right;
  letter-spacing: 0.5px;
}

.tcs-timer-digits.urgent {
  color: #c62828 !important;
  animation: pulseTimer 1s infinite alternate;
}

@keyframes pulseTimer {
  from { opacity: 1; }
  to { opacity: 0.5; }
}

.tcs-timer-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  margin-top: 1px;
}

.tcs-sec-label {
  color: #173c34;
  font-weight: 750;
}

.tcs-total-label {
  color: #64748b;
  border-left: 1px solid #cbd5e1;
  padding-left: 8px;
}
"""

if '.tcs-timer-widget' not in css_content:
    with open('adda.css', 'w', encoding='utf-8') as f:
        f.write(css_content + '\n' + tcs_timer_css)
    print("Added tcs-timer-widget styles to adda.css!")
else:
    print("tcs-timer-widget styles already present.")
