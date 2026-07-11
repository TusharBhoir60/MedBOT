import { test, expect } from '@playwright/test';

test.describe('Review Queue Workflows', () => {
  test.beforeEach(async ({ page }) => {
    // Login as a physician before accessing review queue
    await page.goto('/auth/login');
    await page.getByLabel(/username/i).fill('dr_smith');
    await page.getByLabel(/password/i).fill('password123');
    await page.getByRole('button', { name: /login/i }).click();
    await expect(page).toHaveURL(/.*\/dashboard/);
  });

  test('physician can view review queue and navigate to a task', async ({ page }) => {
    await page.goto('/dashboard/tasks');
    
    // Check if tasks are visible
    const taskLinks = page.locator('a[href^="/dashboard/tasks/"]');
    
    // Wait for tasks to load or handle empty state
    await page.waitForTimeout(1000);
    const count = await taskLinks.count();
    
    if (count > 0) {
      // Click the first task
      await taskLinks.first().click();
      await expect(page).toHaveURL(/.*\/dashboard\/tasks\/.+/);
      
      // Verify review actions are present
      await expect(page.getByRole('button', { name: /approve/i })).toBeVisible();
      await expect(page.getByRole('button', { name: /reject/i })).toBeVisible();
      await expect(page.getByRole('button', { name: /override/i })).toBeVisible();
    }
  });
});
