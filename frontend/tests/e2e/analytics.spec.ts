import { test, expect } from '@playwright/test';

test.describe('Analytics Dashboards', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.getByLabel(/username/i).fill('admin');
    await page.getByLabel(/password/i).fill('password123');
    await page.getByRole('button', { name: /login/i }).click();
    await expect(page).toHaveURL(/.*\/dashboard/);
  });

  test('executive analytics dashboard loads charts', async ({ page }) => {
    await page.goto('/dashboard/analytics');
    
    // Verify specific analytics elements are present
    await expect(page.getByText('Total Conversations')).toBeVisible();
    await expect(page.getByRole('button', { name: /all time/i })).toBeVisible();
    
    // Charts take time to render
    await page.waitForTimeout(1000);
  });

  test('system health dashboard renders component statuses', async ({ page }) => {
    await page.goto('/dashboard/system');
    
    await expect(page.getByText(/system health/i)).toBeVisible();
    await expect(page.getByText(/database/i)).toBeVisible();
  });
});
