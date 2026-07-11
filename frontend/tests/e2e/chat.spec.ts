import { test, expect } from '@playwright/test';

test.describe('Patient Chat Flow', () => {
  test('anonymous user can access chat and send a message', async ({ page }) => {
    await page.goto('/chat');

    // Assuming the chat page has an input for messaging
    const chatInput = page.getByPlaceholder(/type a message/i);
    await expect(chatInput).toBeVisible();

    await chatInput.fill('I have a headache and a fever.');
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for the AI's response in the chat window
    // Looking for a message that is not from the user
    await expect(page.locator('.message-ai').first()).toBeVisible({ timeout: 15000 });
  });
});
