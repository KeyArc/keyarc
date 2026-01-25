import { Component, signal, computed } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

/**
 * Main layout component for KeyArc application.
 * Provides the shell structure with header, sidenav, and content area.
 *
 * Uses:
 * - Angular Material: Toolbar, Sidenav, List, Icons
 * - TailwindCSS: Layout, spacing, responsive design
 */
@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatToolbarModule,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    MatButtonModule
  ],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.scss'
})
export class LayoutComponent {
  /** Current theme mode */
  protected readonly isDarkMode = signal(false);

  /** Theme icon based on current mode */
  protected readonly themeIcon = computed(() =>
    this.isDarkMode() ? 'light_mode' : 'dark_mode'
  );

  /** Navigation items */
  protected readonly navItems = signal([
    { label: 'Dashboard', icon: 'dashboard', route: '/dashboard' },
    { label: 'Secrets', icon: 'key', route: '/secrets' },
    { label: 'Teams', icon: 'group', route: '/teams' },
    { label: 'Settings', icon: 'settings', route: '/settings' }
  ]);

  /** Toggle between light and dark theme */
  protected toggleTheme(): void {
    this.isDarkMode.update(current => !current);
    const theme = this.isDarkMode() ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', theme);
  }
}
