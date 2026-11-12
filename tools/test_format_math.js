function esc(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function formatMathText(raw) {
  if (!raw) return '';
  let text = esc(raw);

  // Format fractions like 3/8, (4/7), 3/8th, 33 1/3, 5/9
  text = text.replace(/(\()?(\d+(?:\.\d+)?|\?)\s*\/\s*(\d+(?:\.\d+)?|\?)(\))?(th|st|nd|rd)?(?!\w)/gi, (match, openParen, num, den, closeParen, ord) => {
    const ordHtml = ord ? `<sup>${ord}</sup>` : '';
    return `<span class="cbt-frac"><span class="cbt-num">${num}</span><span class="cbt-den">${den}</span></span>${ordHtml}`;
  });

  // Powers
  text = text.replace(/²/g, '<sup>2</sup>').replace(/³/g, '<sup>3</sup>');

  // Square roots
  text = text.replace(/√([0-9\.\?]+)/g, '<span style="font-family:serif;">√<span style="border-top:1.5px solid currentColor; padding-top:1px;">$1</span></span>');
  text = text.replace(/∛([0-9\.\?]+)/g, '<span style="font-family:serif;">∛<span style="border-top:1.5px solid currentColor; padding-top:1px;">$1</span></span>');

  return text;
}

const tests = [
  '59.99% of 800 = ? + (4/7) of 91.01',
  '33 1/3% water',
  '3/8th of the students',
  '(17.01)² + 15.01%',
  '√1443.98 + (16.02)² = 6 × (?)²'
];

tests.forEach(t => console.log(t, '\n  ===>', formatMathText(t)));
