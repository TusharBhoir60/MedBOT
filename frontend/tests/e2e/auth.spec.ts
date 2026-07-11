import { test, expect } from '@playwright/test';

test.describe('Authentication Flows', () => {
  test('redirects to login for unauthenticated access to protected routes', async ({ page }) => {
    await page.goto('/dashboard/analytics');
    await expect(page).toHaveURL(/.*\/auth\/login.*/);
  });

  test('successful login as physician redirects to dashboard', async ({ page }) => {
    await page.goto('/auth/login');
    
    // Assuming a standard shadcn/ui login form with accessible labels
    await page.getByLabel(/username/i).fill('dr_smith');
    await page.getByLabel(/password/i).fill('password123');
    
    await page.getByRole('button', { name: /login|sign in/i }).click();

    // Verify successful login
    await expect(page).toHaveURL(/.*\/dashboard/);
    await expect(page.getByText('dr_smith')).toBeVisible();
  });

  test('successful login as admin redirects to dashboard', async ({ page }) => {
    await page.goto('/auth/login');
    
    await page.getByLabel(/username/i).fill('admin');
    await page.getByLabel(/password/i).fill('password123');
    
    await page.getByRole('button', { name: /login|sign in/i }).click();

    // Verify successful login
    await expect(page).toHaveURL(/.*\/dashboard/);
    await expect(page.getByText('admin')).toBeVisible();
  });
});
