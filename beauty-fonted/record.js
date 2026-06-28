import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

(async () => {
  console.log('Starting Playwright...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: {
      dir: 'demo-video',
      size: { width: 1280, height: 720 }
    }
  });

  const page = await context.newPage();
  
  try {
    console.log('Navigating to QA page...');
    await page.goto('http://localhost:5173/app/qa', { waitUntil: 'networkidle' });
    
    // Type the question
    const question = '天鹅颈打造结束后，新顾客和老顾客的推荐护理频率分别是多少？';
    console.log(`Typing question: ${question}`);
    await page.fill('.input-field', question);
    
    // Click send
    console.log('Clicking send...');
    await page.click('.send-btn');
    
    // Wait for the AI response and the reference docs to appear
    console.log('Waiting for AI response...');
    // We wait for the "参考文档" text to appear in the related docs header
    const docsHeader = page.locator('.related-docs-header').last();
    await docsHeader.waitFor({ state: 'visible', timeout: 30000 });
    
    // Wait a bit for the animation of the AI bubble to finish
    await page.waitForTimeout(2000);
    
    // Click to expand
    console.log('Clicking expand on reference document...');
    await docsHeader.click();
    
    // Wait for the docs to be fully expanded and readable
    await page.waitForTimeout(3000);
    
    // Total video length should be around 10s. We've spent some time typing and waiting.
    console.log('Done recording.');
  } catch (err) {
    console.error('Error during automation:', err);
  } finally {
    // Close context to save video
    const videoPath = await page.video().path();
    await context.close();
    await browser.close();
    
    // Rename video to demo.webm
    const targetPath = path.join('demo-video', 'demo.webm');
    if (fs.existsSync(targetPath)) {
      fs.unlinkSync(targetPath);
    }
    fs.renameSync(videoPath, targetPath);
    console.log(`Video saved to ${targetPath}`);
  }
})();
