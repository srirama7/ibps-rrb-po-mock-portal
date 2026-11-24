const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..');
const server = http.createServer((req, res) => {
  let p = path.join(root, req.url.split('?')[0]);
  if (p.endsWith('/') || p.endsWith('\\')) p = path.join(p, 'karnataka.html');
  try {
    const data = fs.readFileSync(p);
    res.writeHead(200);
    res.end(data);
  } catch (e) {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(0, async () => {
  const port = server.address().port;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:' + port + '/karnataka.html');

  // Verify Hero pill & text
  const heroText = await page.locator('.kb-hero').innerText();
  if (!heroText.includes('unlimited retakes') || !heroText.includes('no 3-attempt limit')) {
    throw new Error('Hero does not mention unlimited retakes');
  }

  // Populate 3 existing attempts
  await page.evaluate(() => {
    const hist = [
      { testId: 'KBL-01', answers: {}, startedAt: Date.now() - 300000, completedAt: Date.now() - 240000, timedOut: false, correct: 40, wrong: 10, penalty: 2.5, score: 37.5 },
      { testId: 'KBL-01', answers: {}, startedAt: Date.now() - 200000, completedAt: Date.now() - 140000, timedOut: false, correct: 50, wrong: 8, penalty: 2.0, score: 48 },
      { testId: 'KBL-01', answers: {}, startedAt: Date.now() - 100000, completedAt: Date.now() - 40000, timedOut: false, correct: 60, wrong: 5, penalty: 1.25, score: 58.75 }
    ];
    localStorage.setItem('karnataka_csa_history_v1', JSON.stringify(hist));
  });
  await page.reload();

  // Verify card shows 3 attempts completed and Retake mock (Attempt #4)
  const cardText = await page.locator('.kb-card').first().innerText();
  console.log('Card text with 3 attempts:\n' + cardText);
  if (!cardText.includes('3 attempt(s) completed') || !cardText.includes('Retake mock (Attempt #4)')) {
    throw new Error('Card does not show Attempt #4');
  }

  // Click Retake mock (Attempt #4)
  await page.locator('.kb-card button[data-start]').first().click();
  const instrHeader = await page.locator('.kb-result .kb-label').innerText();
  console.log('Instructions header: ' + instrHeader);
  if (!instrHeader.includes('ATTEMPT #4')) {
    throw new Error('Instructions do not show ATTEMPT #4');
  }
  const beginBtnText = await page.locator('#kbBegin').innerText();
  console.log('Begin button: ' + beginBtnText);
  if (!beginBtnText.includes('Attempt #4')) {
    throw new Error('Begin button does not say Attempt #4');
  }

  // Begin attempt 4
  await page.locator('#kbBegin').click();
  // Submit attempt 4
  await page.locator('#kbSubmit').click();
  await page.locator('#kbConfirm').click();

  // On result page:
  const resultCard = await page.locator('.kb-result').innerText();
  console.log('Result card snippet:\n' + resultCard.slice(0, 300));
  if (!resultCard.includes('ATTEMPT #4') || !resultCard.includes('Unlimited Retakes')) {
    throw new Error('Result card does not show Attempt #4 or Unlimited Retakes');
  }

  // Retake from result page (to Attempt #5)
  await page.locator('#kbRetakeTop').click();
  const nextInstr = await page.locator('.kb-result .kb-label').innerText();
  console.log('Next instructions header: ' + nextInstr);
  if (!nextInstr.includes('ATTEMPT #5')) {
    throw new Error('Did not advance to ATTEMPT #5');
  }

  // Back to library
  await page.locator('#kbBack').click();
  const updatedCard = await page.locator('.kb-card').first().innerText();
  console.log('Card after 4 attempts:\n' + updatedCard);
  if (!updatedCard.includes('4 attempt(s) completed') || !updatedCard.includes('Retake mock (Attempt #5)')) {
    throw new Error('Card does not show 4 attempts and Attempt #5');
  }

  // Check attempt history table
  const tableText = await page.locator('.kb-table').last().innerText();
  console.log('Table text:\n' + tableText.slice(0, 250));
  if (!tableText.includes('Attempt #4') || !tableText.includes('Attempt #3')) {
    throw new Error('History table missing attempt tags');
  }

  // Test reset for single mock
  await page.locator('[data-reset="KBL-01"]').click();
  await page.locator('#kbConfirm').click();
  const resetCard = await page.locator('.kb-card').first().innerText();
  console.log('Card after reset:\n' + resetCard);
  if (!resetCard.includes('Ready for Attempt #1')) {
    throw new Error('Mock did not reset to Attempt #1');
  }

  console.log('\n>>> ALL UNLIMITED RETAKE TESTS PASSED! <<<');
  await browser.close();
  server.close();
  process.exit(0);
});
